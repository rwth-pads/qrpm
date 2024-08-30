from datetime import datetime, date
from typing import Iterable

import numpy as np
import pandas as pd

from qrpm.GLOBAL import TERM_OBJECT_TYPE, TERM_OBJECT, TERM_EVENT, TERM_OBJECT_TYPE_COUNT, TERM_OBJECT_COUNT, TERM_ACTIVITY, \
    TERM_TIME, TERM_EXECUTION_COUNT, TERM_EVENTS, TERM_TIME_SINCE_LAST_EXECUTION


#########################################################################
########################## Events #######################################
#########################################################################

### Information on events (returns extended data) ###
def add_time_since_last_instance(data: pd.DataFrame, instance_identification: Iterable[str] = None) -> pd.DataFrame:
    """
    Pass Quantity Table and columns to identify instance types. Get a table with the time since the last execution of
    the same instance type.
    :param data: Quantity Table
    :param instance_identification: List of columns to identify instance types
    :return: Quantity Table with time since last execution
    """

    if instance_identification:
        if isinstance(instance_identification, str):
            instance_identification = [instance_identification]
        elif isinstance(instance_identification, Iterable):
            pass
        else:
            raise ValueError("Instance identification must be a list.")
    else:
        instance_identification = [TERM_ACTIVITY]

    if set(instance_identification).issubset(set(data.columns)):
        data[TERM_TIME] = pd.to_datetime(data[TERM_TIME])
    else:
        raise ValueError("Instance identification must be a subset of the columns in the data.")

    if TERM_TIME in data.columns:
        pass
    else:
        raise ValueError("No time column in the data.")

    unique_entries = data.loc[:, instance_identification + [TERM_EVENT, TERM_TIME]]
    unique_entries = unique_entries.drop_duplicates()
    unique_entries = unique_entries.sort_values(by=TERM_TIME, ascending=True)

    unique_entries[TERM_TIME_SINCE_LAST_EXECUTION] = unique_entries.groupby(instance_identification)[TERM_TIME].diff()
    extended_data = data.merge(unique_entries, on=instance_identification + [TERM_EVENT, TERM_TIME], how='left')

    return extended_data


def event_selection(event_data: pd.DataFrame, event_ids: Iterable) -> pd.DataFrame:

    return event_data.loc[event_data[TERM_EVENT].isin(event_ids), :]

def filter_events_for_time(data:pd.DataFrame, start_time: datetime | str = None, end_time: datetime | str = None) -> pd.DataFrame:
    """only include instances during passed time period"""

    if TERM_TIME in data.columns:
        data.loc[:, TERM_TIME] = pd.to_datetime(data.loc[:, TERM_TIME])
    else:
        raise ValueError("Time column could not be identified in passed data.")

    if start_time is None:
        start_time = data[TERM_TIME].min()
    else:
        if isinstance(start_time, datetime):
            pass
        elif isinstance(start_time, str):
            if len(start_time) > 19:
                start_time = datetime.strptime(start_time, "%Y-%m-%d-%H-%M-%S-%f")
            elif len(start_time) > 16:
                start_time = datetime.strptime(start_time, "%Y-%m-%d-%H-%M-%S")
            elif len(start_time) > 10:
                start_time = datetime.strptime(start_time, "%Y-%m-%d-%H-%M")
            elif len(start_time) > 7:
                start_time = datetime.strptime(start_time, "%Y-%m-%d")
                start_time = datetime.combine(start_time, datetime.min.time())
            elif len(start_time) > 4:
                start_time = datetime.strptime(start_time, "%Y-%m")
                start_time = datetime.combine(start_time, datetime.min.time())
            else:
                start_time = datetime.strptime(start_time, "%Y")
                start_time = datetime.combine(start_time, datetime.min.time())
        elif isinstance(start_time, date):
            start_time = datetime.combine(start_time, datetime.min.time())
        else:
            raise ValueError("Start time must be a datetime object or a string in format %Y-%m-%d-%H-%M-%S-%f (or shorter variety of format).")

    if end_time is None:
        end_time = data[TERM_TIME].max()
    else:
        if isinstance(end_time, datetime):
            pass
        elif isinstance(end_time, str):
            if len(end_time) > 19:
                end_time = datetime.strptime(end_time, "%Y-%m-%d-%H-%M-%S-%f")
            elif len(end_time) > 16:
                end_time = datetime.strptime(end_time, "%Y-%m-%d-%H-%M-%S")
            elif len(end_time) > 10:
                end_time = datetime.strptime(end_time, "%Y-%m-%d-%H-%M")
            elif len(end_time) > 7:
                end_time = datetime.strptime(end_time, "%Y-%m-%d")
                end_time = datetime.combine(end_time, datetime.max.time())
            elif len(end_time) > 4:
                end_time = datetime.strptime(end_time, "%Y-%m")
                if end_time.month in {1,3,5,7,8,10,12}:
                    end_time = end_time.replace(day=31)
                elif end_time.month == 2:
                    end_time = end_time.replace(day=28)
                else:
                    end_time = end_time.replace(day=30)
                end_time = datetime.combine(end_time, datetime.max.time())
            else:
                end_time = datetime.strptime(end_time, "%Y")
                end_time = end_time.replace(month=12, day=31)
                end_time = datetime.combine(end_time, datetime.max.time())
        elif isinstance(end_time, date):
            end_time = datetime.combine(end_time, datetime.max.time())
        else:
            raise ValueError("End time must be a datetime object or a string.")

    filtered_data = data.loc[(data[TERM_TIME] >= start_time) & (data[TERM_TIME] <= end_time), :]

    return filtered_data


def activity_selection(data: pd.DataFrame, activities: Iterable[str] = None) -> (
        pd.DataFrame):
    """
    Get quantity instances referring to a specific set of activities.
    :param data: table of data
    :param activities: activity
    :return: quantity instances associated with activity
    """
    if TERM_ACTIVITY in data.columns:
        pass
    else:
        raise ValueError("No activity column in the data.")

    if activities:
        if isinstance(activities, str):
            activities = {activities}
        elif isinstance(activities, Iterable):
            activities = set(activities)
        else:
            raise ValueError("Activities must be a set.")

    else:
        activities = set()

    activities = activities.intersection(set(data[TERM_ACTIVITY]))

    filtered_data = data.loc[data[TERM_ACTIVITY].isin(activities), :]

    return filtered_data


def events_with_all_object_types(events: pd.DataFrame, e2o: pd.DataFrame, object_types: Iterable[str] = None) -> pd.DataFrame:
    """
    Get events referring to all of the passed object types.
    :param events: table containing a column with TERM_EVENT
    :param e2o: event to object relations
    :param object_types: set of object types
    :return: filtered event data
    """
    if object_types is None:
        object_types = []
    else:
        if isinstance(object_types, str):
            object_types = [object_types]
        elif isinstance(object_types, Iterable):
            object_types = list(object_types)
        else:
            raise ValueError("Collection points must be a set.")

    e2o_object_type_overview = event_object_type_count(e2o)
    e2o_object_type_overview[object_types] = e2o_object_type_overview[object_types].replace(0, np.nan)
    e2o_object_type_overview = e2o_object_type_overview.dropna(how="any", subset=object_types, axis=0)
    events_with_ots = list(e2o_object_type_overview[TERM_EVENT].unique())

    # get quantity operations for the objects
    filtered_events = events.loc[events[TERM_EVENT].isin(events_with_ots), :]

    return filtered_events

def events_with_any_object_type(events: pd.DataFrame, e2o: pd.DataFrame, object_types: Iterable[str] = None) -> (
        pd.DataFrame):
    """
    Get quantity operations for events referring to at least one object of the specified object types.
    :param events: quantity operations
    :param e2o: event to object relations
    :param object_types: object types
    :return: quantity operations for the object type
    """
    if object_types is None:
        return events
    else:
        if isinstance(object_types, str):
            object_types = {object_types}
        elif isinstance(object_types, Iterable):
            object_types = set(object_types)
        else:
            raise ValueError("Collection points must be a set.")

        object_types = object_types.intersection(set(e2o[TERM_OBJECT_TYPE]))

    if object_types:
        pass
    else:
        return events

    # get all events with specified object type
    event_ids = list(e2o.loc[e2o[TERM_OBJECT_TYPE].isin(list(object_types)), TERM_EVENT].unique())

    filtered_events = events.loc[events[TERM_EVENT].isin(event_ids), :]

    return filtered_events

def events_with_number_objects_of_object_type(events: pd.DataFrame, e2o: pd.DataFrame, object_type: str = None,
                                              no_objects: int = None) -> (pd.DataFrame):
    """
    Get events with specific number of objects of provided object type.
    :param events: table of events
    :param e2o: event to object relations
    :param object_type: object type
    :param no_objects: number of objects
    :return: events with specific number of objects of provided object type
    """
    if object_type is None or no_objects is None:
        return events
    else:
        if isinstance(object_type, str):
            if isinstance(no_objects, int):
                pass
            else:
                raise ValueError("Number of objects must be specified as integer.")
        else:
            raise ValueError("Object type must be string.")

    e2o_count = event_object_type_count(e2o)

    event_ids = list(e2o_count.loc[e2o_count[object_type] == no_objects, TERM_EVENT])
    filtered_events = events.loc[events[TERM_EVENT].isin(event_ids), :]

    return filtered_events

def events_with_total_object_count(events: pd.DataFrame, e2o: pd.DataFrame, object_count: int) -> (pd.DataFrame):
    """
    Get events with specific number of associated objects.
    :param events: quantity operations
    :param e2o: event to object relations
    :param object_count: number of objects
    :return: quantity operations for the object type
    """

    e2o_count = get_total_count_of_objects(e2o)

    event_ids = list(e2o_count.loc[e2o_count[TERM_OBJECT_COUNT] == object_count, TERM_EVENT])
    filtered_events = events.loc[events[TERM_EVENT].isin(event_ids), :]

    return filtered_events

def activity_iteration_object_type(events, e2o, execution_object_type, execution_number):
    """Pass event and e2o table, an object type, and a number of iterations. Returns all events describing the
    <<execution_number>>-th iteration of a single object of the passed object type."""

    if execution_number is not None and execution_number is not None:
        if isinstance(execution_number, int):
            if execution_number < 1:
                raise ValueError("Execution number must be greater than 0.")
            else:
                pass
        else:
            try:
                execution_number = int(execution_number)
                if execution_number < 1:
                    raise ValueError("Execution number must be greater than 0.")
                else:
                    pass
            except Exception as e:
                print(f"Execution number must be an integer, {e}")

    e2o_execution = get_execution_number(e2o, events, execution_object_type)
    event_ids = e2o_execution.loc[e2o_execution[TERM_EXECUTION_COUNT] == execution_number][TERM_EVENTS]

    events_filtered = events.loc[events[TERM_EVENTS].isin(event_ids)]

    return events_filtered


#########################################################################
########### E2O (Event to Object) #######################################
#########################################################################

### Information on e2o (returns extended data) ###

## simple enhancements ##
def add_activity_timestamp_to_e2o(e2o: pd.DataFrame, events: pd.DataFrame) -> pd.DataFrame:

    if not {TERM_ACTIVITY, TERM_EVENT, TERM_TIME}.issubset(set(events.columns)):
        raise ValueError("Non-e2o dataframne must contain event id, activity and timestamp.")
    else:
        pass

    extended_e2o = e2o.merge(events[[TERM_EVENT, TERM_ACTIVITY, TERM_TIME]], on=TERM_EVENT, how='left')
    extended_e2o = extended_e2o.drop_duplicates()

    return extended_e2o

## e2o-based calculations ##
def event_object_type_count(e2o: pd.DataFrame) -> pd.DataFrame:

    e2o_simple = e2o.loc[:, [TERM_EVENT, TERM_OBJECT, TERM_OBJECT_TYPE]]

    # Count the number of objects for each event and object type
    e2o_grouped = e2o_simple.groupby([TERM_EVENT, TERM_OBJECT_TYPE]).size().reset_index(name=TERM_OBJECT_TYPE_COUNT)

    # Change layout DF
    e2o_obj_count = e2o_grouped.pivot_table(index=TERM_EVENT, columns=TERM_OBJECT_TYPE, values=TERM_OBJECT_TYPE_COUNT, aggfunc='sum')

    e2o_obj_count = e2o_obj_count.fillna(0)

    e2o_obj_count = e2o_obj_count.reset_index()

    return e2o_obj_count

def get_total_count_of_objects(e2o: pd.DataFrame) -> pd.DataFrame:

    e2o_count = e2o.groupby(TERM_EVENT).size().reset_index(name=TERM_OBJECT_COUNT)

    return e2o_count

def get_execution_number(e2o:pd.DataFrame, events: pd.DataFrame, object_type: str) -> pd.DataFrame:

    if not object_type in e2o[TERM_OBJECT_TYPE].unique():
        raise ValueError("Object type not in the data.")
    else:
        pass

    if not {TERM_EVENT, TERM_ACTIVITY, TERM_TIME}.issubset(set(e2o.columns)):
        extended_e2o = add_activity_timestamp_to_e2o(e2o, events)
    else:
        extended_e2o = e2o.copy()

    extended_e2o = extended_e2o.drop_duplicates()

    # Filter the df for the specified object type
    e2o_filtered = extended_e2o.loc[extended_e2o[TERM_OBJECT_TYPE] == object_type]

    # remove duplicates of event-object combinations
    e2o_filtered = e2o_filtered.drop_duplicates(subset=[TERM_EVENT, TERM_OBJECT])

    # count number of objects
    e2o_grouped = e2o_filtered.groupby([TERM_EVENT, TERM_ACTIVITY, TERM_TIME]).size().reset_index(
        name=TERM_OBJECT_TYPE_COUNT)

    # only 1 object of object type
    e2o_relevant_events_only = e2o_grouped[e2o_grouped[TERM_OBJECT_TYPE_COUNT] == 1]

    # Sort
    e2o_sorted_events = e2o_relevant_events_only.sort_values(TERM_TIME)

    # add correct object names to the dataframe (filtered data)
    e2o_sorted_events = e2o_sorted_events.merge(e2o_filtered[[TERM_EVENT, TERM_OBJECT]], on=TERM_EVENT, how='left')

    # Calculate the cumulative count of events for each activity-object combination
    e2o_sorted_events[TERM_EXECUTION_COUNT] = e2o_sorted_events.groupby([TERM_ACTIVITY, TERM_OBJECT]).cumcount() + 1

    original_df = extended_e2o[[TERM_EVENT, TERM_ACTIVITY, TERM_TIME]].drop_duplicates()

    # Merge with the original DataFrame
    e2o_execution_count = pd.merge(original_df, e2o_sorted_events[[TERM_EVENT, TERM_OBJECT, TERM_EXECUTION_COUNT]],
                                   on=TERM_EVENT, how='left')

    return e2o_execution_count

### Filtering e2o ###

def e2o_for_instances(e2o: pd.DataFrame, filtered_data: pd.DataFrame, instance_type=TERM_EVENT) -> pd.DataFrame:

    if not instance_type in filtered_data.columns:
        raise ValueError("Dataframe must contain instance type.")

    e2o_filtered = e2o.loc[e2o[instance_type].isin(filtered_data[instance_type]), :]

    return e2o_filtered

def e2o_for_any_object_type_selection(e2o: pd.DataFrame, object_types: Iterable[str] = None) -> pd.DataFrame:
    """
        Remove all objects that are not of the specified object type as well as all events only referring to such objects.
        :param e2o: event to object relations
        :param object_types: object type
        :return: quantity operations for the object type
    """

    if object_types is None:
        return e2o
    else:
        if isinstance(object_types, str):
            object_types = {object_types}
        elif isinstance(object_types, Iterable):
            object_types = set(object_types)
        else:
            raise ValueError("Collection points must be a set.")

        object_types = object_types.intersection(set(e2o[TERM_OBJECT_TYPE]))

    if object_types:
        pass
    else:
        return e2o

    # remove all entries not referring to an object of one of the specified object types
    filtered_e2o = e2o.loc[e2o[TERM_OBJECT_TYPE].isin(list(object_types)), :]

    return filtered_e2o

def e2o_activity_object_type_selection(e2o: pd.DataFrame, events: pd.DataFrame, activity: Iterable, object_type: str) -> pd.DataFrame:
    """Pass event and e2o table and a selected activity and object type. Returns the filtered e2o table only
    containing the e2o relations of objects that have executed the selected activities at least once."""

    all_events_of_activity = events.loc[events[TERM_ACTIVITY].isin(activity), TERM_EVENT].unique()

    e2o_temp = e2o.loc[e2o[TERM_EVENT].isin(all_events_of_activity), :]
    relevant_objects = e2o_temp.loc[e2o_temp[TERM_OBJECT_TYPE]==object_type, TERM_OBJECT].unique()

    relevant_events = e2o.loc[e2o[TERM_OBJECT].isin(relevant_objects), TERM_EVENT].unique()

    return e2o.loc[e2o[TERM_EVENT].isin(relevant_events), :]

def e2o_object_type_with_looped_activity_selection(e2o: pd.DataFrame, events: pd.DataFrame, activity: str, object_type: str, restriction:int):
    """Pass event and e2o table, a selected activity and object type, and a number of iterations. Returns the filtered
    e2o table only containing events associated to objects of the passed type with exactly the specified number of
    iterations of the selected activity."""

    extended_e2o = e2o.merge(events[[TERM_EVENT, TERM_ACTIVITY]], on=TERM_EVENT, how="left")

    e2o_filtered = extended_e2o.loc[extended_e2o[TERM_OBJECT_TYPE] == object_type, :]
    e2o_filtered = e2o_filtered.loc[e2o_filtered[TERM_ACTIVITY] == activity, :]

    relevant_objects_data = e2o_filtered.groupby([TERM_OBJECT, TERM_ACTIVITY]).size().reset_index(name=TERM_EXECUTION_COUNT)
    relevant_objects = relevant_objects_data.loc[relevant_objects_data[TERM_EXECUTION_COUNT] == restriction, TERM_OBJECT].unique()

    relevant_events = e2o.loc[e2o[TERM_OBJECT].isin(relevant_objects), TERM_EVENT].unique()

    return e2o.loc[e2o[TERM_EVENT].isin(relevant_events), :]

def objects_of_selected_object_types(objects: pd.DataFrame, object_types: Iterable[str]) -> pd.DataFrame:
    """
    Get objects of specified object types.
    :param objects: table of objects
    :param object_types: object types
    :return: objects of any of the passed object types
    """
    if object_types is None:
        return objects
    else:
        if isinstance(object_types, str):
            object_types = {object_types}
        elif isinstance(object_types, Iterable):
            object_types = set(object_types)
        else:
            raise ValueError("Object types must be a set.")

    if object_types:
        pass
    else:
        return objects

    filtered_objects = objects.loc[objects[TERM_OBJECT_TYPE].isin(object_types), :]

    return filtered_objects

#########################################################################
########################## Sublog creation ##############################
#########################################################################

def sublog_for_passed_events(events: pd.DataFrame, e2o: pd.DataFrame, objects: pd.DataFrame, selected_events: Iterable[str]) -> (pd.DataFrame, pd.DataFrame, pd.DataFrame):
    """
    Create a sublog of passed events.
    :param events: table of events
    :param e2o: event to object relations
    :param objects: table of objects
    :return: events, e2o, objects of sublog
    """
    if selected_events is None:
        selected_events = events[TERM_EVENT].unique()
    else:
        pass

    events_new = events.loc[events[TERM_EVENT].isin(selected_events), :]
    e2o_new = e2o_for_instances(e2o=e2o, filtered_data=events, instance_type=TERM_EVENT)
    objects_new = objects.loc[objects[TERM_OBJECT].isin(e2o_new[TERM_OBJECT]), :]

    return events_new, e2o_new, objects_new

####################### newly added functions ##########################


# def remove_object_types(qop: pd.DataFrame, e2o: pd.DataFrame, object_types_to_keep: Iterable[str]) -> (pd.DataFrame, pd.DataFrame):
#     """
#     Remove all objects of specified object types from the quantity operations and event to object relations.
#     :param qop: Quantity operations
#     :param e2o: Event to object relations
#     :param object_types_to_keep: Object types to keep
#     :return: Quantity operations and event to object relations without the specified object types
#     """
#     if object_types_to_keep is None:
#         return qop, e2o
#     else:
#         pass
#
#     if isinstance(object_types_to_keep, str):
#         object_types_to_keep = {object_types_to_keep}
#     elif isinstance(object_types_to_keep, Iterable):
#         object_types_to_keep = set(object_types_to_keep)
#     else:
#         raise ValueError("Object types must be a set.")
#
#     object_types = list(set(e2o[TERM_OBJECT_TYPE]).intersection(object_types_to_keep))
#
#     e2o_filtered = e2o.loc[e2o[TERM_OBJECT_TYPE].isin(object_types), :]
#     events = list(e2o_filtered[TERM_EVENT].unique())
#     qop_filtered = qop.loc[qop[TERM_EVENT].isin(events), :]
#
#     return qop_filtered, e2o_filtered

