from typing import Iterable
import numpy as np
import pandas as pd

from qrpm.analysis.counterOperations import get_active_instances, item_type_projection, cp_active_instances_any_cp, \
    cp_active_instances_all_cps, it_active_instances_all_item_types, it_active_instances_any_item_type, \
    joint_counters, total_item_quantities, create_item_quantities, negative_item_quantities, positive_item_quantities
from qrpm.analysis.generalDataOperations import convert_numeric_columns, split_instance_and_variable_entries, combine_instances
from qrpm.GLOBAL import TERM_EVENT, TERM_ADDING, TERM_REMOVING, TERM_DIRECTION, TERM_ADDING_REMOVING, TERM_INACTIVE



###########################################################################
############################# SUBLOG CREATION #############################
###########################################################################

def event_data_from_qop(qop: pd.DataFrame, events: pd.DataFrame) -> pd.DataFrame:
    filtered_events = events.loc[qop[TERM_EVENT], :]
    return filtered_events

### Filtered on events or objects: Event ###

def qop_event_selection(qop: pd.DataFrame, events: pd.DataFrame) -> pd.DataFrame|None:
    """ Pass dataframe of events, return quantity operations for the selected events."""

    if qop:
        pass
    else:
        return None

    qop_new = qop.loc[qop[TERM_EVENT].isin(events[TERM_EVENT])]
    return qop_new

### Filtered on quantities: Property ###

def active_events(qop: pd.DataFrame) -> (pd.DataFrame):
    """Return quantity operations for active events."""

    active_qop = get_active_instances(qop)
    active_events = event_data_from_qop(qop=qop, events=active_qop)

    return active_events


def cp_active_events_all_cps(qop: pd.DataFrame, cps: Iterable[str] = None) -> pd.DataFrame:
    """ Get qop data filtered for cp-active events for all passed collection points. """

    active_qop = cp_active_instances_all_cps(qty=qop, cps=cps, instance_type=TERM_EVENT)
    active_events = event_data_from_qop(qop=qop, events=active_qop)

    return active_events


def cp_active_events_any_cp(qop: pd.DataFrame, cps: Iterable[str] = None) -> (
        pd.DataFrame):
    """ Get qop data filtered for cp-active events for any of the passed collection points. """

    active_qop = cp_active_instances_any_cp(qop, cps)
    active_events = event_data_from_qop(qop=qop, events=active_qop)

    return active_events


def it_active_events_all_item_types(qop: pd.DataFrame, item_types: Iterable[str] = None) -> (pd.DataFrame):
    """Filter quantity data to only include events that are quantity active for all of the passed item types."""

    active_qop = it_active_instances_all_item_types(qop, item_types)
    active_events = event_data_from_qop(qop=qop, events=active_qop)

    return active_events


def it_active_events_any_item_type(qop: pd.DataFrame,
                                   item_types: Iterable[str] = None) -> (
        pd.DataFrame):
    """Filter quantity data to only include events that are quantity active for all of the passed item types."""

    active_qop = it_active_instances_any_item_type(qop, item_types)
    active_events = event_data_from_qop(qop=qop, events=active_qop)

    return active_events


###########################################################################
######################## PREPARE QOP DATA #################################
###########################################################################

def transform_to_material_movements(qop: pd.DataFrame):
    """Transform dataframe so all numeric columns contain the absolute values of the quantity operations."""

    material_movements = convert_numeric_columns(qop)

    cols_non_item_types, cols_item_types = split_instance_and_variable_entries(set(material_movements.columns))

    material_movements[cols_item_types] = material_movements[cols_item_types].abs()

    return material_movements


def adding_qops(qop: pd.DataFrame) -> pd.DataFrame:
    """Projects remaining quantity operations to the adding quantity updates."""
    return positive_item_quantities(qop)


def removing_qops(qop: pd.DataFrame) -> pd.DataFrame:
    """Projects remaining quantity operations to removing quantity updates."""
    return negative_item_quantities(qop)


def create_quantity_updates(qop: pd.DataFrame) -> pd.DataFrame:
    """
    Pass a quantity operations table and get a quantity updates table.
    :param qop: Quantity operations table.
    :return: quantity update table
    """

    return create_item_quantities(qop)


def qop_cp_aggregation(qop: pd.DataFrame) -> (pd.DataFrame):
    """
    Determine Joint quantity operations or material movements per event by composing the quantity operations of every collection point.
    :param qop: Quantity operations
    :param aggregation_type: Aggregation type
    :return: Aggregated quantity operations
    """

    return joint_counters(qty=qop, instance_type=TERM_EVENT)


def total_quantity_operations(qop: pd.DataFrame, item_types: set | list = None) -> pd.DataFrame:
    return total_item_quantities(qty=qop, item_types=item_types)

def get_direction_quantity_instances(qop: pd.DataFrame) -> pd.DataFrame:
    """Pass dataframe and for every instance get whether it is adding, removing or both."""

    non_item_types, item_types = split_instance_and_variable_entries(set(qop.columns))

    active_enhanced = qop.copy()
    active_enhanced[item_types] = active_enhanced[item_types].fillna(0)
    active_enhanced[TERM_ADDING] = active_enhanced[item_types].apply(lambda row: any(val > 0 for val in row), axis=1)
    active_enhanced[TERM_REMOVING] = active_enhanced[item_types].apply(lambda row: any(val < 0 for val in row), axis=1)
    active_enhanced.loc[active_enhanced[TERM_ADDING] == True, TERM_DIRECTION] = TERM_ADDING
    active_enhanced.loc[active_enhanced[TERM_REMOVING] == True, TERM_DIRECTION] = TERM_REMOVING
    active_enhanced.loc[
        (active_enhanced[TERM_ADDING] & active_enhanced[TERM_REMOVING]), TERM_DIRECTION] = TERM_ADDING_REMOVING
    active_enhanced[TERM_DIRECTION] = active_enhanced[TERM_DIRECTION].replace(np.nan, TERM_INACTIVE)

    return active_enhanced
