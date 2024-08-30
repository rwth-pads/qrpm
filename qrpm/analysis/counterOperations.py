from typing import Iterable

import numpy as np
import pandas as pd

from qrpm.analysis.generalDataOperations import split_instance_and_variable_entries, combine_instances
from qrpm.GLOBAL import TERM_ACTIVE, TERM_INACTIVE, TERM_ALL, TERM_COLLECTION, TERM_EVENT, \
    TERM_INSTANCE_COUNT, TERM_AGG_CP, TERM_AGG_ITEM_TYPES, TERM_ITEM_TYPES, TERM_VALUE

#### ITEM QUANTITY PER INSTANCE ####
def create_item_quantities(counters: pd.DataFrame) -> pd.DataFrame:
    """
    Pass a table of counters and get an item quantity table.
    :param qop: Quantity operations table.
    :return: quantity update table
    """

    non_item_types, item_types = split_instance_and_variable_entries(set(counters.columns))

    if len(item_types) == 1:
        counters.loc[:, TERM_ITEM_TYPES] = item_types[0]
        item_quantities = counters.rename(columns={item_types[0]: TERM_VALUE})
        return item_quantities
    elif len(item_types) == 0:
        raise ValueError("No item types in the data.")
    else:
        pass

    item_quantities = counters.melt(id_vars=non_item_types, var_name=TERM_ITEM_TYPES, value_name=TERM_VALUE)

    return item_quantities

##### INFORMATION #####
def get_enhanced_quantity_instances(qty: pd.DataFrame) -> pd.DataFrame:
    """Pass dataframe and for every instance get the active status of the instance."""

    non_item_types, item_types = split_instance_and_variable_entries(set(qty.columns))

    active_enhanced = qty.copy()
    active_enhanced[TERM_ACTIVE] = active_enhanced[item_types].apply(lambda row: all(val == 0 for val in row), axis=1)
    active_enhanced[TERM_ACTIVE] = active_enhanced[TERM_ACTIVE].replace({True: TERM_INACTIVE, False: TERM_ACTIVE})

    return active_enhanced

def get_active_item_types(qop: pd.DataFrame):
    """Get the name of all item types with at least one non-zero value."""

    non_item_types, item_types = split_instance_and_variable_entries(set(qop.columns))

    item_types = set(qop.loc[:, item_types].columns[(qop.loc[:, item_types] != 0).any()])

    return item_types

###### PROJECTIONS ######
## based on passed projection function ###
def projection_generic_function(data: pd.DataFrame,
                                projection_function_data: pd.DataFrame,
                                identifying_columns: list) -> pd.DataFrame:
    """Projects the data in the to be projected dataframe to all active cells in the projection function dataframe."""

    if not set(identifying_columns).issubset(set(projection_function_data.columns).intersection(set(data.columns))):
        raise ValueError("Identifying columns must be a subset of the columns in the projection function data.")
    else:
        pass

    data_non_item_types, data_item_types = split_instance_and_variable_entries(set(data.columns))
    projection_function_non_item_types, projection_function_item_types = split_instance_and_variable_entries(set(projection_function_data.columns))

    item_types_to_remove = set(data_item_types).difference(set(projection_function_item_types))
    joint_item_types = list(set(data_item_types).intersection(set(projection_function_item_types)))

    projection_function = projection_function_data.set_index(identifying_columns)
    data_projected = data.set_index(identifying_columns)

    data_projected = data_projected.loc[data_projected.index.intersection(projection_function.index)]


    if len(item_types_to_remove) > 0:
        data_projected = data_projected.drop(columns=list(item_types_to_remove))
    else:
        pass

    if len(joint_item_types) > 0:
        projection_function = projection_function_data.set_index(identifying_columns)

        projection_function.loc[:, joint_item_types] = projection_function[joint_item_types].replace(0, np.nan)

        mask = projection_function[joint_item_types].isna()

        data_projected[mask] = np.nan
    else:
        pass

    data_projected = data_projected.reset_index()

    return data_projected

### DIMENSIONALITY ###
def cp_projection(qty: pd.DataFrame, cps: Iterable[str] = None) -> (
pd.DataFrame, pd.DataFrame):
    """
    Get quantity instances for a specific set of collection points.
    :param qty: table of collection counters
    :param cps: set of collection points
    :return: quantity instances of for the selected collection points
    """

    if cps is not None:
        if cps == TERM_ALL:
            return qty
        else:
            pass

        if isinstance(cps, str):
            cps = {cps}
        elif isinstance(cps, Iterable):
            cps = set(cps)
        else:
            raise ValueError("Collections must be a set.")

        cps = cps.intersection(set(qty[TERM_COLLECTION]))

    else:
        return qty

    filtered_qty = qty.loc[qty[TERM_COLLECTION].isin(list(cps)), :]

    return filtered_qty

def item_type_projection(qty: pd.DataFrame, item_types: Iterable[str] = None) -> pd.DataFrame:
    """Filter the quantity instances for selected item types."""

    non_item_types, item_type_cols = split_instance_and_variable_entries(set(qty.columns))

    if item_types == TERM_ALL:
        return qty
    else:
        pass

    if isinstance(item_types, str):
        item_types = {item_types}
    elif isinstance(item_types, Iterable):
        item_types = set(item_types)
    else:
        raise ValueError("Item types must be a set.")

    if item_types.issubset(set(item_type_cols)):
        pass
    else:
        raise ValueError("Selected item types must be a subset of the item types in the data.")

    item_types_to_remove = set(item_type_cols).difference(item_types)

    qty_filtered = qty.drop(columns=list(item_types_to_remove))

    return qty_filtered

#### SELECTED COUNTERS (leave item quantities unchanged) ####

## Quantity Operations: ACTIVENESS ##
def get_active_instances(qty: pd.DataFrame) -> pd.DataFrame:
    """Get entries with active counter values."""

    if len(qty) == 0:
        return qty
    else:
        pass

    non_item_types, item_types = split_instance_and_variable_entries(set(qty.columns))

    if len(item_types) == 0:
        return pd.DataFrame(columns=non_item_types)
    else:
        pass

    # remove entries with zero on all item types
    qty_new = qty[~(qty[item_types] == 0).all(axis=1)]

    return qty_new

# Quantity Operations: CP-ACTIVE #
def cp_active_instances_any_cp(qty: pd.DataFrame, cps: Iterable[str] = None) -> pd.DataFrame:
    """Get the active objects from the event to object relations."""

    if cps is None:
        return qty
    else:
        if isinstance(cps, str):
            cps = {cps}
        elif isinstance(cps, Iterable):
            cps = set(cps)
        else:
            raise ValueError("Collection points must be a set.")

    filtered_qty = qty.loc[qty[TERM_COLLECTION].isin(cps), :]

    # only keep entries with at least one non-zero value
    active_qty = get_active_instances(filtered_qty)

    return active_qty

def cp_active_instances_all_cps(qty: pd.DataFrame, cps: Iterable[str] = None, instance_type=TERM_EVENT) -> pd.DataFrame:
    """Get all instances active for all of the passed set of cps."""

    if cps:
        pass
    else:
        return qty

    active_qops = cp_active_instances_any_cp(qty, cps)

    qty_tmp = active_qops.loc[:, [instance_type, TERM_COLLECTION]]
    qty_tmp = qty_tmp.groupby([TERM_EVENT]).size().reset_index(name=TERM_INSTANCE_COUNT)
    active_instances = qty_tmp.loc[qty_tmp[TERM_INSTANCE_COUNT] == len(cps), instance_type]

    qty_filtered = qty.loc[qty[instance_type].isin(active_instances), :]

    return qty_filtered

# Quantity Operations: ITEM TYPE ACTIVE #
def it_active_instances_all_item_types(qty: pd.DataFrame, item_types: Iterable[str]) -> pd.DataFrame:
    """Get counters active for all passed item types."""

    if isinstance(item_types, str):
        item_types = {item_types}
    elif isinstance(item_types, Iterable):
        item_types = set(item_types)
    else:
        raise ValueError("Item types must be a set.")

    non_item_types, cols_item_types = split_instance_and_variable_entries(set(qty.columns))

    item_types = list(item_types.intersection(set(cols_item_types)))

    # drop all columns with at least one 0 on the considered item types
    qty_new = qty[~(qty[item_types] == 0).any(axis=1)]

    return qty_new

def it_active_instances_any_item_type(qty: pd.DataFrame, item_types: Iterable[str]) -> pd.DataFrame:
    """Get the quantity operations that are active for all passed item types."""

    if isinstance(item_types, str):
        item_types = {item_types}
    elif isinstance(item_types, Iterable):
        item_types = set(item_types)
    else:
        raise ValueError("Item types must be a set.")

    non_item_types, cols_item_types = split_instance_and_variable_entries(set(qty.columns))

    item_types = list(item_types.intersection(set(cols_item_types)))

    # remove entries with zero on all item types
    active_qty = qty[~(qty[item_types] == 0).all(axis=1)]

    return active_qty


#### SELECTED ITEM QUANTITIES (project counters to selection of item types) ####

def positive_item_quantities(qty: pd.DataFrame) -> pd.DataFrame:
    non_item_types, item_types = split_instance_and_variable_entries(qty.columns)

    only_positive = qty.set_index(non_item_types)

    only_positive = only_positive.where(only_positive[item_types] > 0)

    only_positive[item_types] = only_positive[item_types].fillna(0)

    return only_positive.reset_index()

def negative_item_quantities(qty: pd.DataFrame) -> pd.DataFrame:
    non_item_types, item_types = split_instance_and_variable_entries(qty.columns)

    only_negative = qty.set_index(non_item_types)

    only_negative = only_negative.where(only_negative[item_types] < 0)

    only_negative[item_types] = only_negative[item_types].fillna(0)

    return only_negative.reset_index()


###### AGGREGATIONS ######
def joint_counters(qty: pd.DataFrame, instance_type=TERM_EVENT) -> pd.DataFrame:
    """Get one joint counter per instance."""

    non_item_type_cols, item_types = split_instance_and_variable_entries(set(qty.columns))
    columns_to_keep = set(non_item_type_cols).difference({TERM_COLLECTION})

    qty_aggregated = combine_instances(data=qty, combine_instances=instance_type, columns_to_keep=columns_to_keep,
                                       name_aggregation=TERM_COLLECTION,
                                       entry_aggregation_col=TERM_AGG_CP)

    return qty_aggregated

def total_item_quantities(qty: pd.DataFrame, item_types: set | list = None) -> pd.DataFrame:
    """Aggregate every counter to a one-dimensional counter with the total item quantity."""

    non_item_type_cols, item_type_cols = split_instance_and_variable_entries(set(qty.columns))

    if item_types is not None:
        if isinstance(item_types, str):
            item_types = {item_types}
        elif isinstance(item_types, set):
            pass
        elif isinstance(item_types, Iterable):
            item_types = set(item_types)
        else:
            raise ValueError("Item types must be a set or list.")

        if item_types.issubset(set(item_type_cols)):
            pass
        else:
            raise ValueError("Item types must be a subset of the item types in the data.")

        total_qty = item_type_projection(qty=qty, item_types=item_types)
    else:
        total_qty = qty
        item_types = item_type_cols

    total_qty[TERM_AGG_ITEM_TYPES] = qty[item_types].sum(axis=1)

    total_qty = total_qty.drop(columns=item_types)

    return total_qty
