import numpy as np
import pandas as pd

from qrpm.analysis.counterOperations import item_type_projection, cp_projection, get_active_instances
import qrpm.analysis.quantityOperations as qopp
from qrpm.GLOBAL import TERM_QUANTITY_CHANGES, TERM_ITEM_MOVEMENTS, TERM_ALL, TERM_ADDING, TERM_REMOVING, \
    TERM_ACTIVE_OPERATIONS, TERM_COLLECTION, TERM_ACTIVITY
import qrpm.app.dataStructure as ds


def process_quantity_operations(qop:pd.DataFrame, qop_type, qop_property, qop_active, qop_it_agg,
                                qop_cp_agg, selected_item_types, selected_collection_points) -> (pd.DataFrame, pd.DataFrame):
    # project to item types
    qop = item_type_projection(qty=qop, item_types=selected_item_types)

    # project to collection points
    qop = cp_projection(qty=qop, cps=selected_collection_points)

    # Quantity Operations vs. Item Movements
    if qop_type == TERM_QUANTITY_CHANGES:
        pass
    elif qop_type == TERM_ITEM_MOVEMENTS:
        qop = qopp.transform_to_material_movements(qop=qop)
    else:
        raise ValueError(f"Quantity Change type {qop_type} is not valid.")

    # adding/removing projection
    if qop_property == TERM_ALL:
        pass
    elif qop_property == TERM_ADDING:
        qop = qopp.adding_qops(qop=qop)
    elif qop_property == TERM_REMOVING:
        qop = qopp.removing_qops(qop=qop)
    else:
        raise ValueError(f"Projection {qop_property} is not valid.")

    # item type aggregation
    if qop_it_agg:
        qop = qopp.total_quantity_operations(qop=qop)
    else:
        pass

    # collection point aggregation
    if qop_cp_agg:
        qop = qopp.qop_cp_aggregation(qop=qop)
    else:
        pass

    # only active instances
    if qop_active == TERM_ALL:
        pass
    else:
        qop = get_active_instances(qty=qop)

        if qop_active == TERM_ACTIVE_OPERATIONS:
            pass
        else:
            qop = qop.replace(0, np.nan)

    return ds.store_single_dataframe(qop)

def data_quantity_relation(qop: pd.DataFrame, cp: str | None, activity: str | None):

    if cp:
        qop = qop.loc[qop[TERM_COLLECTION] == cp, :]
    else:
        pass

    if activity:
        qop = qop.loc[qop[TERM_ACTIVITY] == activity, :]
    else:
        pass

    return ds.store_single_dataframe(qop)
