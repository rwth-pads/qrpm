from qrpm.analysis.counterOperations import cp_projection, item_type_projection
from qrpm.analysis.ocelOperations import event_selection, activity_selection
from qrpm.GLOBAL import PRE_EVENT_ILVL, TERM_QUANTITY_OPERATIONS, TERM_ITEM_LEVELS, TERM_ALL, ILVL_AVAILABLE, TERM_EVENT
import qrpm.analysis.quantityState as ilvvl
import qrpm.app.dataStructure as ds

def process_ilvl_data_according_to_selection(ilvl, overview_json, ilvl_type, ilvl_perspective, ilvl_property,
                                             cp_aggregation, it_aggregation, item_types_projection, cps_projection):

    ilvl = ilvvl.project_dimensions_item_level_data(ilvl=ilvl, cps=cps_projection, item_types=item_types_projection)

    if ilvl_type == PRE_EVENT_ILVL:
        pass
    else:
        qop = ds.get_raw_data(overview_json)[TERM_QUANTITY_OPERATIONS]
        ilvl = ilvvl.transform_pre_event_to_post_event_qstate(ilvl=ilvl, qop=qop)

    if ilvl_perspective == TERM_ITEM_LEVELS:
        pass
    else:
        ilvl = ilvvl.transform_to_item_associations(ilvl=ilvl)

    if ilvl_property == TERM_ALL:
        pass
    elif ilvl_property == ILVL_AVAILABLE:
        ilvl = ilvvl.available_items(ilvl=ilvl)
    else:
        ilvl = ilvvl.demanded_items(ilvl=ilvl)

    if cp_aggregation:
        ilvl = ilvvl.overall_quantity_state_collection_point_aggregation(ilvl=ilvl)
    else:
        pass

    if it_aggregation:
        ilvl = ilvvl.total_ilvl_item_type_aggregation(ilvl=ilvl)
    else:
        pass


    return ds.store_single_dataframe(ilvl)

def quantity_state_development(processed_qstate_json, qty_json, ilvl_display):
    ilvl = ds.get_single_dataframe(processed_qstate_json)
    qop, orig_ilvl, oqty = ds.get_qty_data(qty_json)

    if qop is None:
        events = None
    else:
        if ilvl_display == TERM_ALL:
            events = qop[TERM_EVENT].unique()
        else:
            ilvl = event_selection(event_data=ilvl, event_ids=qop[TERM_EVENT].unique())
            events = None

    return ilvl, events

def ilvl_data_for_execution(processed_qstate_json, qty_json, selected_activity, selected_cp, selected_it,
                                            it_active_selection):

    ilvl = ds.get_single_dataframe(processed_qstate_json)
    qop, orig_ilvl, oqty = ds.get_qty_data(qty_json)

    if qop is None:
        return None
    else:
        ilvl = event_selection(event_data=ilvl, event_ids=qop[TERM_EVENT].unique())

    if selected_activity:
        ilvl = activity_selection(data=ilvl, activities=selected_activity)
    else:
        pass

    if selected_cp:
        ilvl = cp_projection(qty=ilvl, cps=selected_cp)
    else:
        pass

    if selected_it:
        ilvl = item_type_projection(qty=ilvl, item_types=selected_it)
    else:
        pass

    if it_active_selection == TERM_ALL:
        pass
    else:
        ilvl = ilvvl.project_quantity_state_to_active_quantity_updates(ilvl=ilvl, qop=qop)

    return ds.store_single_dataframe(ilvl)


