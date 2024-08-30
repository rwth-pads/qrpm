from qrpm.analysis.counterOperations import cp_projection, item_type_projection
from qrpm.analysis.ocelOperations import (e2o_for_any_object_type_selection, e2o_activity_object_type_selection, \
                                     e2o_object_type_with_looped_activity_selection, e2o_for_instances,
                                     events_with_number_objects_of_object_type, \
                                     events_with_all_object_types, event_selection, activity_selection,
                                     filter_events_for_time, events_with_any_object_type,
                                     events_with_total_object_count, activity_iteration_object_type,
                                     objects_of_selected_object_types)
from qrpm.analysis.generalDataOperations import remove_empty_columns
import qrpm.app.dataStructure as ds
import qrpm.analysis.quantityOperations as qopp
import qrpm.analysis.quantityState as ilvvl
from qrpm.GLOBAL import TERM_EVENT, TERM_OBJECT, TERM_ALL, TERM_ACTIVE


def create_ocel_from_qop(qop, ocel_json):
    """Pass filtered qop containing only the qop that should be considered. Returns events, e2o and objects to only
    contain the corresponding events and the associated objects."""

    events, e2o, objects = ds.get_ocel_data(ocel_json)

    if qop is not None and len(qop) > 0:
        e2o_new = e2o_for_instances(e2o=e2o, filtered_data=qop, instance_type=TERM_EVENT)
        events_new = events.loc[events[TERM_EVENT].isin(qop[TERM_EVENT]), :]
        objects_new = objects.loc[objects[TERM_OBJECT].isin(e2o_new[TERM_OBJECT]), :]
        objects_new = remove_empty_columns(objects_new)
        events_new = remove_empty_columns(events_new)

        return ds.events_e2o_objects_to_ocel_dict(events_new, e2o_new, objects_new)

    else:
        return None

def create_ocel_from_events(events_new, e2o, objects):
    """Pass filtered df containing only the events that should be considered. Returns ocel dict with events, e2o and objects to only
    containing the associated e2os and objects."""

    e2o_new = e2o_for_instances(e2o=e2o, filtered_data=events_new, instance_type=TERM_EVENT)
    objects_new = objects.loc[objects[TERM_OBJECT].isin(e2o_new[TERM_OBJECT]), :]
    objects_new = remove_empty_columns(objects_new)
    events_new = remove_empty_columns(events_new)

    return ds.events_e2o_objects_to_ocel_dict(events_new, e2o_new, objects_new)

def create_ocel_from_e2o(events, e2o_new, objects):
    """Pass filtered df containing only the e2os that should be considered. Returns ocel dict with events, e2o and objects to only
    containing the associated events and objects."""

    events_new = events.loc[events[TERM_EVENT].isin(e2o_new[TERM_EVENT]), :]
    objects_new = objects.loc[objects[TERM_OBJECT].isin(e2o_new[TERM_OBJECT]), :]
    objects_new = remove_empty_columns(objects_new)
    events_new = remove_empty_columns(events_new)

    return ds.events_e2o_objects_to_ocel_dict(events_new, e2o_new, objects_new)

def create_ocel_from_objects_events(events, e2o, objects_new):
    """Pass filtered df containing the relevant objects. Returns ocel dict with events, e2o and objects containing only
    the events, objects and e2os of events executed w.r.t. the selected objects."""

    e2o_temp = e2o.loc[e2o[TERM_OBJECT].isin(objects_new[TERM_OBJECT]), :]
    e2o_new = e2o.loc[e2o[TERM_EVENT].isin(e2o_temp[TERM_EVENT]), :]
    events_new = events.loc[events[TERM_EVENT].isin(e2o_new[TERM_EVENT]), :]
    objects_new = objects_new.loc[objects_new[TERM_OBJECT].isin(e2o_new[TERM_OBJECT]), :]
    objects_new = remove_empty_columns(objects_new)
    events_new = remove_empty_columns(events_new)

    return ds.events_e2o_objects_to_ocel_dict(events_new, e2o_new, objects_new)

def create_ocel_from_objects_objects(events, e2o, objects_new):
    """Pass filtered df containing the relevant objects. Returns ocel dict with events, e2o and objects containing only
    the events and e2os referreing to the selected objects."""

    e2o_new = e2o.loc[e2o[TERM_OBJECT].isin(objects_new[TERM_OBJECT]), :]
    events_new = events.loc[events[TERM_EVENT].isin(e2o_new[TERM_EVENT]), :]
    objects_new = remove_empty_columns(objects_new)
    events_new = remove_empty_columns(events_new)

    return ds.events_e2o_objects_to_ocel_dict(events_new, e2o_new, objects_new)

def create_qop_from_ocel(ocel_new, qop):
    """Pass filtered ocel containing only the events and objects that should be considered. Returns qop containing only the
    quantity operations of the corresponding events."""

    if qop is None or ocel_new is None:
        return None
    else:
        pass

    events, e2o, objects = ds.events_e2o_objects_from_ocel_dict(ocel_new)
    qop_new = qop.loc[qop[TERM_EVENT].isin(events[TERM_EVENT]), :]

    return qop_new if len(qop_new) > 0 else None


def filter_data_for_activity(ocel_json, selected_activities):
    """Returns sublog containing only the events of the selected activities as well as the corresponding e2os, qops and
    objects."""

    events, e2o, objects = ds.get_ocel_data(ocel_json)

    events_new = activity_selection(data=events, activities=selected_activities)
    ocel = create_ocel_from_events(events_new=events_new, e2o=e2o, objects=objects)

    return ocel

def filter_data_for_event_attribute(ocel_json, selected_attribute, selected_attribute_values):
    # TODO only filter corresponding activity
    events, e2o, objects = ds.get_ocel_data(ocel_json)

    events_new = events.loc[events[selected_attribute].isin(selected_attribute_values), :]
    ocel = create_ocel_from_events(events_new=events_new, e2o=e2o, objects=objects)

    return ocel

def filter_data_for_events_with_object_type(ocel_json, selected_object_types):

    events, e2o, objects = ds.get_ocel_data(ocel_json)

    events_new = events_with_all_object_types(events, e2o, selected_object_types)
    return create_ocel_from_events(events_new=events_new, e2o=e2o, objects=objects)

def filter_data_for_object_attribute_value(ocel_json, selected_attribute, selected_attribute_values):
    """Only keep events associated with an object with the selected attribute value."""

    events, e2o, objects = ds.get_ocel_data(ocel_json)

    objects.loc[:, [selected_attribute]] = objects[selected_attribute].astype(str)
    objects_new = objects.loc[objects[selected_attribute].isin(selected_attribute_values), :]
    return create_ocel_from_objects_events (events=events, e2o=e2o, objects_new=objects_new)


def filter_data_for_object_type_number(ocel_json, selected_object_type_object_type, selected_object_type_number):
    events, e2o, objects = ds.get_ocel_data(ocel_json)

    events_new = events_with_number_objects_of_object_type(events=events, e2o=e2o,
                                                           object_type=selected_object_type_object_type,
                                                           no_objects=selected_object_type_number)
    return create_ocel_from_events(events_new=events_new, e2o=e2o, objects=objects)

def filter_data_for_iteration(ocel_json, selected_object_type_iteration, selected_iteration_number):
    """Pass ocel, an object type, and a number of iterations. Returns an ocel only containing events representing the
        <<execution_number>>-th iteration of a single object of the passed object type of the corresponding activity."""
    events, e2o, objects = ds.get_ocel_data(ocel_json)

    events_new = activity_iteration_object_type(events=events, e2o=e2o, execution_object_type=selected_object_type_iteration,
                                                execution_number=selected_iteration_number)
    return create_ocel_from_events(events_new=events_new, e2o=e2o, objects=objects)

def filter_data_for_total_object_counts(ocel_json, total_objects):

    events, e2o, objects = ds.get_ocel_data(ocel_json)

    events_new = events_with_total_object_count(events=events, e2o=e2o, object_count=total_objects)
    return create_ocel_from_events(events_new=events_new, e2o=e2o, objects=objects)


def filter_data_for_time_period(ocel_json, selected_start_date, selected_end_date):
    events, e2o, objects = ds.get_ocel_data(ocel_json)

    events_new= filter_events_for_time(data=events, start_time=selected_start_date, end_time=selected_end_date)
    return create_ocel_from_events(events_new=events_new, e2o=e2o, objects=objects)

def filter_for_objects_with_activity_execution(ocel_json, object_selection_object_type, object_activity_execution_selection):
    """Pass ocel and a selected activity and object type. Returns sublog of objects which have executed the selected
    activity. Sublog contains all events associated to these objects."""
    events, e2o, objects = ds.get_ocel_data(ocel_json)


    e2o_new = e2o_activity_object_type_selection(e2o=e2o, events=events,
                                                 object_type=object_selection_object_type,
                                                 activity=object_activity_execution_selection)
    return create_ocel_from_e2o(events=events, e2o_new=e2o_new, objects=objects)

def filter_objects_with_specified_iterations_of_activity(ocel_json, object_type, activity, restriction):
    """Pass ocel, a selected activity and object type, and a number of iterations. Returns sublog only containing
    objects of the passed type with exactly the specified number of iterations of the selected activity and all of the
    events they were part of."""
    events, e2o, objects = ds.get_ocel_data(ocel_json)

    e2o_new = e2o_object_type_with_looped_activity_selection(e2o=e2o, events=events, object_type=object_type, activity=activity,
                                                             restriction=restriction)
    return create_ocel_from_e2o(events=events, e2o_new=e2o_new, objects=objects)

def filter_objects_of_object_types(ocel_json, object_types_to_include):
    events, e2o, objects = ds.get_ocel_data(ocel_json)

    objects_new = objects_of_selected_object_types(objects=objects, object_types=object_types_to_include)
    return create_ocel_from_objects_objects(events=events, e2o=e2o, objects_new=objects_new)

def filter_data_for_active_event_selection(qop, active_selection):
    if active_selection == TERM_ALL:
        return qop
    else:
        qop_active = qopp.active_events(qop)

    if active_selection == TERM_ACTIVE:
        return qop_active
    else:
        qop_inactive = qop.loc[~qop[TERM_EVENT].isin(qop_active[TERM_EVENT]), :]
        return qop_inactive

def filter_data_for_cp_active_events(qop, cp_active_selection, cp_any_all):

    if cp_any_all == TERM_ALL:
        qop_new = qopp.cp_active_events_all_cps(qop=qop, cps=cp_active_selection)
    else:
        qop_new = qopp.cp_active_events_any_cp(qop=qop, cps=cp_active_selection)

    return qop_new

def filter_data_for_it_active_events(qop, it_active_selection, it_any_all):

    if it_any_all == TERM_ALL:
        qop_new = qopp.it_active_events_all_item_types(qop=qop, item_types=it_active_selection)
    else:
        qop_new = qopp.it_active_events_any_item_type(qop=qop, item_types=it_active_selection)
    return qop_new

def filter_data_for_events_in_ilvl(qop, ilvl,selected_ilvl_range, selected_cp_item_balance, selected_it_item_balances):

    event_ids_in_range = ilvvl.events_at_qstate(ilvl=ilvl, collection_point=selected_cp_item_balance,
                                             item_types=selected_it_item_balances,
                                             min=selected_ilvl_range[0], max=selected_ilvl_range[-1])
    return qop.loc[qop[TERM_EVENT].isin(event_ids_in_range), :]

def filter_data_for_selected_collection_points(qop, selected_collection_points_projection):

    qop_new = cp_projection(qty=qop, cps=selected_collection_points_projection)
    return qop_new

def filter_data_for_selected_item_types(qop, selected_item_types_projection):

    qop_new = item_type_projection(qty=qop, item_types=selected_item_types_projection)
    return qop_new
