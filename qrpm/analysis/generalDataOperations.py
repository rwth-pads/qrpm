from datetime import datetime
from typing import Iterable

import numpy as np
import pandas as pd

from qrpm.GLOBAL import TERM_EVENT, TERM_COLLECTION, TERM_ACTIVITY, TERM_TIME, TERM_OBJECT, TERM_OBJECT_TYPE, TERM_ACTIVE, \
    TERM_ITEM_TYPES, \
    TERM_COMBINED_INSTANCES, TERM_VALUE, QOP_ID, OBJECT_CHANGE


def remove_empty_columns(data: pd.DataFrame, keep_zeros: bool = True):
    """remove all columns that are zero"""
    if keep_zeros:
        data = data.dropna(axis=1, how="all")
    else:
        # data = data.fillna(0)
        data = data.loc[:, (data != 0).any()]
        data = data.dropna(axis=1, how="all")
    return data

def convert_numeric_columns(df):
    df = df.convert_dtypes()
    return df

def convert_to_timestamp(df):
    if TERM_TIME in df.columns:
        df[TERM_TIME] = pd.to_datetime(df[TERM_TIME])
    else:
        pass

    if "ocel_time" in df.columns:
        df["ocel_time"] = pd.to_datetime(df["ocel_time"])
    else:
        pass

    time_cols = [col for col in df.columns if "time" in col]
    for col_name in time_cols:
        df[col_name] = pd.to_datetime(df[col_name])

    return df

def convert_timestamp_columns_to_string(df):
    timestamp_cols = df.select_dtypes(include=[np.datetime64, datetime]).columns
    df_new = df.copy()
    df_new.loc[:, timestamp_cols] = df.loc[:, timestamp_cols].astype(str)
    if TERM_TIME in df.columns:
        df_new[TERM_TIME] = df_new.loc[:, TERM_TIME].astype(str)
    else:
        pass
    return df_new


def split_instance_and_variable_entries(column_names: set) -> (list[str], list[str]):
    """
    Determine the non-item type columns in a list of column names
    :param column_names: list of column names
    :return: list of non-item type columns
    """

    if isinstance(column_names, str):
        column_names = {column_names}
    elif isinstance(column_names, list):
        column_names = set(column_names)
    elif isinstance(column_names, set):
        pass
    elif isinstance(column_names, Iterable):
        column_names = set(column_names)
    else:
        raise ValueError("Column names must be a set.")

    cols_non_item_types = list(column_names.intersection({TERM_EVENT, TERM_COLLECTION, TERM_ACTIVITY, TERM_TIME, TERM_ITEM_TYPES, TERM_COMBINED_INSTANCES,
                                                              TERM_OBJECT, TERM_OBJECT_TYPE, TERM_ACTIVE, QOP_ID, OBJECT_CHANGE, "ocel_time"}))
    cols_item_types = list(column_names.difference(cols_non_item_types))

    return cols_non_item_types, cols_item_types


def combine_instances(data: pd.DataFrame, combine_instances: Iterable[str] = None, columns_to_keep: Iterable[str] = None,
                      name_aggregation: str = None, entry_aggregation_col: str = None,
                      combination_count: bool = False) -> pd.DataFrame:
    """
    Combine instances in a data set referring to the values for a subset of columns.
    :param data: Dataframe with counters - required: data to be aggregated has to be identifiable by column separation
    :param combine_instances: list of columns describing what instances to combine if they have the same values for all columns in the list/set
    :param columns_to_keep: list of columns that would be removed but should be kept - always keeps the first instance (sorted by time, if data contains a time column)
    :param aggregation_type: type of aggregation - sum or absolute values
    :param name_aggregation: name of the column with the new identifier
    """

    non_item_type_cols, item_type_cols = split_instance_and_variable_entries(set(data.columns))

    if combine_instances:
        if isinstance(combine_instances, str):
            combine_instances = {combine_instances}
        elif isinstance(combine_instances, set):
            pass
        elif isinstance(combine_instances, Iterable):
            combine_instances = set(combine_instances)
        else:
            raise ValueError("Aggregate by must be a string or an iterable of strings.")

        if combine_instances.issubset(set(data.columns)):
            pass
        else:
            raise ValueError("Not all columns in combine_instances are in the data.")

    else:
        if TERM_EVENT in data.columns:
            combine_instances = {TERM_EVENT}
        else:
            return data

    keep = set(item_type_cols).union(combine_instances)
    columns_to_drop = set(data.columns).difference(keep)
    combine_instances = list(combine_instances)

    if columns_to_keep:
        if isinstance(columns_to_keep, str):
            columns_to_keep = {columns_to_keep}
        elif isinstance(columns_to_keep, set):
            pass
        elif isinstance(columns_to_keep, Iterable):
            columns_to_keep = set(columns_to_keep)
        else:
            raise ValueError("Columns to keep must be a string or an iterable of strings.")

        if columns_to_keep.issubset(set(data.columns)):
            pass
        else:
            raise ValueError("Not all columns in columns_to_keep are in the data.")

        columns_to_keep = columns_to_keep.intersection(columns_to_drop)

        if columns_to_keep:
            columns_to_keep = list(columns_to_keep)
            merge_columns = combine_instances + columns_to_keep
            keep_data = data.copy()
            if TERM_TIME in data.columns:
                keep_data[TERM_TIME] = pd.to_datetime(keep_data[TERM_TIME])
                keep_data = keep_data.sort_values(by=TERM_TIME, ascending=True)
                keep_data = keep_data.loc[:, merge_columns]
                keep_data = keep_data.drop_duplicates(subset=combine_instances, keep='first')
            else:
                keep_data = keep_data.loc[:, merge_columns]
                keep_data = keep_data.drop_duplicates(subset=combine_instances, keep='first')
        else:
            keep_data = None
    else:
        keep_data = None

    # drop all no longer required columns
    aggregated_data = data.drop(columns=list(columns_to_drop))

    if combination_count:
        aggregated_data.loc[:, TERM_COMBINED_INSTANCES] = 1
    else:
        pass

    aggregated_data = aggregated_data.groupby(combine_instances).sum().reset_index()

    # add the kept data back to the aggregated data
    if keep_data is not None:
        aggregated_data = aggregated_data.merge(keep_data, on=combine_instances, how='left')
    else:
        pass

    # if required, add column that informs about the aggregation
    if name_aggregation:
        if entry_aggregation_col:
            aggregated_data[name_aggregation] = entry_aggregation_col
        else:
            aggregated_data[name_aggregation] = aggregated_data[combine_instances].apply(lambda x: '-'.join(x.astype(str)), axis=1)
    else:
        pass

    return aggregated_data


def get_descriptive_statistics_item_types(data: pd.DataFrame, count_zeros_frequency: bool = False) -> pd.DataFrame:
    """
    Get descriptive statistics of every item type in provided data
    :param data: data
    :return: descriptive statistics overview of the data
    """

    non_item_types, item_types = split_instance_and_variable_entries(set(data.columns))

    df = data[item_types]

    stats = pd.DataFrame(index=item_types)

    ## get info on frequency
    if count_zeros_frequency:
        df_freq = df
    else:
        df_freq = df.replace(0, np.nan)

    stats["abs_freq"] = df_freq.count()
    stats["rel_freq"] = df_freq.count() / len(df)

    ## get info on distribution
    # range
    stats["min"] = df.min()
    stats["max"] = df.max()

    # center
    stats["mean"] = df.mean()
    stats["median"] = df.median()
    stats["mode"] = df.mode().iloc[0] if len(df.mode()) > 0 else np.nan
    stats["unique"] = df.nunique()

    # spread
    stats["25%-Quartile"] = df.quantile(0.25)
    stats["75%-Quartile"] = df.quantile(0.75)
    stats["std"] = df.std()
    stats["var"] = df.var()

    stats = stats.round(3)
    stats = stats.T

    return stats

def get_descriptive_statistics(data: pd.DataFrame, view: str = TERM_COLLECTION, count_zeros_frequency: bool = False) -> pd.DataFrame:
    """
    Get descriptive statistics of values in selected columns
    :param data: data
    :return: descriptive statistics overview of the data
    """

    if view in [TERM_ITEM_TYPES, TERM_COLLECTION, TERM_ACTIVITY]:
        pass
    else:
        raise ValueError("View must be one of 'item_types', 'collections', or 'activity'.")

    non_item_types, item_types = split_instance_and_variable_entries(set(data.columns))

    if view == TERM_ITEM_TYPES:
        filtered_data = remove_empty_columns(data)
        return get_descriptive_statistics_item_types(filtered_data, count_zeros_frequency=count_zeros_frequency)
    else:
        data_melted = data.melt(id_vars=non_item_types, var_name=TERM_ITEM_TYPES, value_name=TERM_VALUE)
        data_melted = data_melted.reset_index()

    index = set(non_item_types).union({TERM_ITEM_TYPES})

    if view == TERM_COLLECTION:
        index_cp = index - {TERM_COLLECTION}
        df = data_melted.pivot(index=list(index_cp), columns=TERM_COLLECTION, values=TERM_VALUE)
        df = remove_empty_columns(df, keep_zeros=True)
        stats = pd.DataFrame(index=list(data[TERM_COLLECTION].unique()))
    else:
        index_act = index - {TERM_ACTIVITY}
        df = data_melted.pivot(index=list(index_act), columns=TERM_ACTIVITY, values=TERM_VALUE)
        df = remove_empty_columns(df, keep_zeros=True)
        stats = pd.DataFrame(index=list(data[TERM_ACTIVITY].unique()))

    ## get info on frequency
    if count_zeros_frequency:
        df_freq = df
    else:
        df_freq = df.replace(0, np.nan)

    stats["abs_freq"] = df_freq.count()
    stats["rel_freq"] = df_freq.count() / len(df)

    # range
    stats["min"] = df.min()
    stats["max"] = df.max()

    # center
    stats["mean"] = df.mean()
    stats["median"] = df.median()
    stats["mode"] = df.mode().iloc[0] if len(df.mode()) > 0 else np.nan
    stats["unique"] = df.nunique()

    # spread
    stats["25%-Quartile"] = df.quantile(0.25)
    stats["75%-Quartile"] = df.quantile(0.75)
    stats["std"] = df.std()
    stats["var"] = df.var()

    stats = stats.round(3)
    stats = stats.T

    return stats


