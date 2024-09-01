from collections import Counter
from typing import Iterable

import numpy as np
import pandas as pd
import datetime

from qrpm.analysis.generalDataOperations import convert_numeric_columns, split_instance_and_variable_entries, remove_empty_columns
from qrpm.analysis.counterOperations import total_item_quantities, joint_counters, \
    projection_generic_function, get_active_instances, cp_projection, item_type_projection, positive_item_quantities, \
    negative_item_quantities
from qel_simulation import QuantityEventLog
from qrpm.GLOBAL import TERM_COLLECTION, TERM_ITEM_TYPES, TERM_VALUE, TERM_TIME, TERM_EVENT, TERM_ACTIVITY, TERM_INIT


#############################################################
################ Determine QUANTITY STATE ###################
#############################################################

def determine_quantity_state_cp(qop: pd.DataFrame, cp: str, initial_item_level: Counter, post_event: bool = False) -> pd.DataFrame:
    """
    Determine the item levels before or after an event was executed
    :param qop: Assumed to be a dataframe describing the quantity operations without important index with the following
    columns: event_id, activity, timestamp, and one column per relevant item type.
    Only relevant quantity operations assumed to be present.
    :param initial_item_level: Counter object with the initial item levels of passed collection
    :param post_event: boolean telling if pre- or post-event item levels should be returned.
    :return: dataframe with item levels before or after the event was executed
    """


    # filter quantity operations for selected collection
    if isinstance(cp, str):
        pass
    else:
        raise ValueError("Collection point must be a string.")

    if cp in qop[TERM_COLLECTION].unique():
        pass
    else:
        raise ValueError("Collection point not found in quantity operations.")

    ilvl = qop.loc[qop[TERM_COLLECTION] == cp, :]

    # format timestamps and get earliest timestamp
    ilvl.loc[:, TERM_TIME] = pd.to_datetime(ilvl[TERM_TIME])
    earliest_timestamp = ilvl[TERM_TIME].min()

    # add initial item level
    new_entry = dict(initial_item_level)
    new_entry[TERM_EVENT] = TERM_INIT
    new_entry[TERM_ACTIVITY] = TERM_INIT
    new_entry[TERM_COLLECTION] = cp
    new_entry[TERM_TIME] = earliest_timestamp - datetime.timedelta(seconds=1)
    new_entry_df = pd.DataFrame([new_entry])
    new_entry_df = new_entry_df.fillna(0)
    ilvl = pd.concat([ilvl, new_entry_df], ignore_index=True)

    # sort by timestamp
    ilvl = ilvl.sort_values(by=TERM_TIME, ascending=True)

    # set all non-item type columns as index to simplify the rest
    ilvl = ilvl.set_index([TERM_EVENT, TERM_ACTIVITY, TERM_COLLECTION, TERM_TIME])

    # apply accumulated sum so that item levels are determined
    ilvl = ilvl.cumsum()

    if post_event:
        ilvl = ilvl.reset_index()
    else:
        ilvl = ilvl.shift(1)
        ilvl = ilvl.fillna(0)
        ilvl = ilvl.reset_index()
        ilvl = ilvl.loc[ilvl[TERM_EVENT] != TERM_INIT, :]

    return ilvl

def determine_quantity_state_qel(qel: QuantityEventLog) -> pd.DataFrame:
    """
    Get the item level development for a quantity event log.
    :param qel: quantity event log
    :return: item level development
    """

    item_levels = pd.DataFrame()

    qop = qel.get_quantity_operations()

    if len(qop) == 0:
        return item_levels
    else:
        pass

    for cp in qel.collection_points:
        initial_item_level = qel.get_initial_item_level_cp(cp=cp)
        ilvl = determine_quantity_state_cp(qop=qop,
                                           cp=cp,
                                           initial_item_level=initial_item_level,
                                           post_event=False)
        item_levels = pd.concat([item_levels, ilvl])

    # sort according to timestamps
    item_levels[TERM_TIME] = pd.to_datetime(item_levels[TERM_TIME])
    item_levels = item_levels.sort_values(by=TERM_TIME, ascending=True)

    item_levels = item_levels.reset_index(drop=True)

    return item_levels

def determine_quantity_state_qop(qop: pd.DataFrame, initial_item_level: dict[str: dict]) -> pd.DataFrame:
    """
    Get the item level development for a quantity event log.
    :param qop: quantity operations of events
    :param initial_item_level: initial item levels for each collection point (as dict)
    :return: item level development
    """

    item_levels = pd.DataFrame()

    if len(qop) == 0:
        return item_levels
    else:
        pass

    for cp in qop[TERM_COLLECTION].unique():
        initial_item_level_cp = Counter(initial_item_level[cp])
        ilvl = determine_quantity_state_cp(qop=qop,
                                           cp=cp,
                                           initial_item_level=initial_item_level_cp,
                                           post_event=False)
        item_levels = pd.concat([item_levels, ilvl])

    # sort according to timestamps
    item_levels[TERM_TIME] = pd.to_datetime(item_levels[TERM_TIME])
    item_levels = item_levels.sort_values(by=TERM_TIME, ascending=True)

    item_levels = item_levels.reset_index(drop=True)

    return item_levels

#############################################################
################### SUBLOG CREATION #########################
#############################################################

def events_at_qstate(ilvl: pd.DataFrame, collection_point: str, item_types: Iterable[str], min: int | None, max: int | None):
    """return all event ids where the item level is in the specified area."""

    relevant_item_levels = ilvl.loc[ilvl[TERM_COLLECTION] == collection_point, :]

    if min is not None:
        if len(item_types) > 1:
            relevant_item_levels = relevant_item_levels.loc[(relevant_item_levels[item_types] >= min), :]
        else:
            relevant_item_levels = relevant_item_levels.loc[(relevant_item_levels[item_types] >= min).any(axis=1), :]
    else:
        pass

    if max is not None:
        if len(item_types) > 1:
            relevant_item_levels = relevant_item_levels.loc[(relevant_item_levels[item_types] <= max), :]
        else:
            relevant_item_levels = relevant_item_levels.loc[(relevant_item_levels[item_types] <= max).any(axis=1), :]
    else:
        pass

    return relevant_item_levels[TERM_EVENT].unique()

###########################################################################
######################## PREPARE Q-STATE ##################################
###########################################################################

##### PROJECTIONS #####
def project_quantity_state_to_active_quantity_updates(ilvl: pd.DataFrame, qop: pd.DataFrame) -> pd.DataFrame:
    """Project the quantity state to active quantity updates."""

    ilvl_active_qup = projection_generic_function(data=ilvl, projection_function_data=qop,
                                                  identifying_columns=[TERM_EVENT, TERM_COLLECTION])
    ilvl_active_qup = get_active_instances(qty=ilvl_active_qup)

    return ilvl_active_qup

### Dimensions ###
def project_dimensions_item_level_data(ilvl: pd.DataFrame, cps: set = None, item_types: set | list = None) -> pd.DataFrame:
    """
    Filter item levels or capacities for selected activities, collections, and item types
    """

    if cps:
        ilvl = cp_projection(qty=ilvl, cps=cps)
    else:
        pass

    if item_types:
        ilvl = item_type_projection(qty=ilvl, item_types=item_types)
    else:
        pass

    return ilvl

### Properties ###
def available_items(ilvl: pd.DataFrame) -> pd.DataFrame:
    """Projects item levels to the available items."""
    return positive_item_quantities(ilvl)

def demanded_items(ilvl: pd.DataFrame) -> pd.DataFrame:
    """Projects item level to in-demand item quantities."""
    return negative_item_quantities(ilvl)

### Aggregations ###
def total_ilvl_item_type_aggregation(ilvl: pd.DataFrame, item_types: set | list = None) -> pd.DataFrame:
    """
    Get the sum of the values of the selected item types in the data
    :param ilvl: data
    :param item_types: list of item types
    :return: data with item types
    """
    return total_item_quantities(qty=ilvl, item_types=item_types)

def overall_quantity_state_collection_point_aggregation(ilvl:pd.DataFrame) -> pd.DataFrame:
    """
    Pass item level and get the item levels per event which aggregate the item levels for all collections.
    :param ilvl: dataframe containing a column for the item level
    :return: dataframe with a single item level per event
    """

    return joint_counters(qty=ilvl, instance_type=TERM_EVENT)

### Transformations ###
def transform_pre_event_to_post_event_qstate(ilvl: pd.DataFrame, qop: pd.DataFrame) -> pd.DataFrame:
    """
    Transform item level development to post-event item level development
    :param ilvl: item level development
    :param qop: quantity operations
    :return: item level development for the event
    """

    ilvl_non_item_types, ilvl_item_types = split_instance_and_variable_entries(set(ilvl.columns))
    qop_non_item_types, qop_item_types = split_instance_and_variable_entries(set(qop.columns))

    item_type_intersection = list(set(ilvl_item_types).intersection(set(qop_item_types)))

    if (TERM_EVENT in ilvl_non_item_types and TERM_COLLECTION in ilvl_non_item_types and
            TERM_EVENT in qop_non_item_types and TERM_COLLECTION in qop_non_item_types and
            item_type_intersection):
        pass
    else:
        raise ValueError("Non-item type columns do not match between item level development and quantity operations.")

    qop_for_event = qop.loc[qop[TERM_EVENT].isin(ilvl[TERM_EVENT]), :]

    ilvl = ilvl.set_index([TERM_EVENT, TERM_COLLECTION])
    qop_for_event = qop_for_event.set_index([TERM_EVENT, TERM_COLLECTION])

    ilvl.loc[:, item_type_intersection] = ilvl.loc[:, item_type_intersection].add(qop_for_event.loc[:, item_type_intersection], fill_value=np.nan)
    ilvl = ilvl.reset_index()

    return ilvl

def transform_to_item_associations(ilvl: pd.DataFrame):
    """Transform dataframe so all numeric columns contain the absolute values of the quantity operations."""

    qty_ass = convert_numeric_columns(ilvl)

    cols_non_item_types, cols_item_types = split_instance_and_variable_entries(set(qty_ass.columns))

    qty_ass[cols_item_types] = qty_ass[cols_item_types].abs()

    return qty_ass


##### INFORMATION ######
def get_descriptive_statistics_for_qstate(data: pd.DataFrame) -> pd.DataFrame | None:
    """
    Get descriptive statistics of values in selected columns
    :param data: data
    :return: descriptive statistics overview of the data
    """

    stats = pd.DataFrame(columns=list(data[TERM_COLLECTION].unique()))

    for cp in data[TERM_COLLECTION].unique():

        df = data.loc[data[TERM_COLLECTION] == cp]
        df = remove_empty_columns(df, keep_zeros=False)
        non_item_types, item_types = split_instance_and_variable_entries(set(df.columns))

        # stock out periods
        out_of_stock_counts = count_stock_out_periods(df)

        df = df.melt(id_vars=non_item_types, var_name=TERM_ITEM_TYPES, value_name=TERM_VALUE)
        df = df.reset_index()

        stats.loc["item types", cp] = len(item_types)
        stats.loc["item balances", cp] = len(df)

        # counts of item balances
        stats.loc["positive", cp] = len(df.loc[df[TERM_VALUE] > 0])
        stats.loc["empty", cp] = len(df.loc[df[TERM_VALUE] == 0])
        stats.loc["negative", cp] = len(df.loc[df[TERM_VALUE] < 0])
        unavailable_item_types = list(df.loc[df[TERM_VALUE] <= 0, TERM_ITEM_TYPES].unique())
        stats.loc["unav. types",  cp] = len(unavailable_item_types)
        stats.loc["unav. periods", cp] = sum(out_of_stock_counts.values())

        # range
        minimum = df[TERM_VALUE].min()
        maximum = df[TERM_VALUE].max()
        min_item_types = list(df.loc[df[TERM_VALUE] == minimum, TERM_ITEM_TYPES].unique())
        max_item_types = list(df.loc[df[TERM_VALUE] == maximum, TERM_ITEM_TYPES].unique())
        stats.loc["min", cp] = minimum
        stats.loc["min types", cp] = ", ".join(min_item_types)
        stats.loc["max", cp] = maximum
        stats.loc["max types", cp] = ", ".join(max_item_types)

    return stats

def count_stock_out_periods(ilvl: pd.DataFrame) -> dict:

    non_item_types, item_types = split_instance_and_variable_entries(set(ilvl.columns))
    out_of_stock_counts = {}

    for item_type in item_types:

        out_of_stock = ilvl[item_type] <= 0

        transitions = np.diff(out_of_stock.astype(int))

        out_of_stock_count = np.sum(transitions == 1)

        out_of_stock_counts[item_type] = out_of_stock_count

    return out_of_stock_counts
