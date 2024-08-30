from qrpm.analysis.generalDataOperations import combine_instances
from qrpm.GLOBAL import TERM_OBJECT, TERM_ACTIVITY, TERM_COLLECTION, TERM_EVENT, TERM_OBJECT_TYPE, TERM_ALL
import pandas as pd
from typing import Iterable


def determine_object_quantity(qop: pd.DataFrame, e2o: pd.DataFrame, object_types: Iterable[str]=None) -> pd.DataFrame:
    """
    For every object of the specified object types: Get the overall quantity operations/item movements for all events of the same activity involving the same object.
    :param qop: Quantity operations
    :param e2o: Event to object relations
    :param object_types: Object types
    :param aggregation_type: Aggregation type
    :return: Quantity table with object-activity combinations as instances, describing the overall quantity operation/item Movement.
    Contains a column naming the first event id of the passed combination.
    """

    if object_types is None:
        e2o_filtered = e2o
    else:
        if isinstance(object_types, str):
            if object_types == TERM_ALL:
                object_types = set(e2o[TERM_OBJECT_TYPE].unique())
            else:
                object_types = {object_types}
        elif isinstance(object_types, Iterable):
            object_types = set(object_types)
        else:
            raise ValueError("Object types must be a set.")
        e2o_filtered = e2o.loc[e2o[TERM_OBJECT_TYPE].isin(object_types), :]

    events = list(e2o_filtered[TERM_EVENT].unique())

    qop_filtered = qop.loc[qop[TERM_EVENT].isin(events), :]

    # extend qop data by objects
    qop_extended = qop_filtered.merge(e2o_filtered, on=TERM_EVENT, how="inner")

    qop_aggregated = combine_instances(data=qop_extended,
                                       combine_instances=[TERM_OBJECT, TERM_COLLECTION, TERM_ACTIVITY],
                                       combination_count=True)

    return qop_aggregated

# def filter_qop_data_for_oqty(qop, e2o, object_types=None, activity=None, active_item_types=None):
#     if object_types is None:
#         e2o_filtered = e2o
#     else:
#         if isinstance(object_types, str):
#             object_types = {object_types}
#         elif isinstance(object_types, Iterable):
#             object_types = set(object_types)
#         else:
#             raise ValueError("Object types must be a set.")
#         e2o_filtered = e2o.loc[e2o[TERM_OBJECT_TYPE].isin(object_types), :]
#
#     events = list(e2o_filtered[TERM_EVENT].unique())
#
#     qop_filtered = qop.loc[qop[TERM_EVENT].isin(events), :]
#
#     # extend qop data by objects
#     qop_extended = qop_filtered.merge(e2o_filtered, on=TERM_EVENT, how="inner")
#
#     return qop_extended
