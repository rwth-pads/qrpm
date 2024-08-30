import pandas as pd

from qrpm.analysis.counterOperations import get_active_item_types, get_active_instances
from qrpm.analysis.ocelOperations import e2o_for_instances
from qel_simulation import QuantityEventLog
from qrpm.GLOBAL import (TERM_EVENT, TERM_ITEM_TYPES, TERM_QTY_EVENTS, TERM_QTY_ACTIVITIES, TERM_QTY_OBJECTS,
                    TERM_QTY_OBJECT_TYPES,
                    TERM_ACTIVE_QOP, TERM_QUANTITY_RELATIONS, TERM_ACTIVITY, TERM_OBJECT,
                    TERM_OBJECT_TYPE, TERM_COLLECTION, TERM_QUANTITY_OPERATIONS)


def get_log_overview(qel: QuantityEventLog):
    """Get an overview of the quantity event log."""

    log_overview = dict()

    log_overview[TERM_EVENT] = len(qel.events)
    log_overview[TERM_QTY_EVENTS] = len(qel.get_quantity_events())
    log_overview[TERM_ACTIVITY] = list(qel.activities)
    log_overview[TERM_QTY_ACTIVITIES] = list(qel.quantity_activities)
    log_overview[TERM_OBJECT] = len(qel.objects)
    log_overview[TERM_QTY_OBJECTS] = len(qel.get_qty_objects())
    log_overview[TERM_OBJECT_TYPE] = list(qel.object_types)
    log_overview[TERM_QTY_OBJECT_TYPES] = list(qel.get_qty_object_types())
    log_overview[TERM_ACTIVE_QOP] = len(qel.active_quantity_operations)
    log_overview[TERM_COLLECTION] = list(qel.collection_points)
    log_overview[TERM_ITEM_TYPES] = list(qel.item_types)
    log_overview[TERM_QUANTITY_RELATIONS] = list(qel.get_quantity_relations())

    return log_overview

def get_element_overview(qop: pd.DataFrame, e2o: pd.DataFrame):
    """Get information about the events, objects, activities, object types, item types and collections involved in the
    passed (filtered?!) data."""

    active_qop = get_active_instances(qty=qop)
    active_e2o = e2o_for_instances(e2o=e2o, filtered_data=active_qop, instance_type=TERM_EVENT)

    overview = dict()

    overview[TERM_EVENT] = len(qop[TERM_EVENT].unique())
    overview[TERM_QTY_EVENTS] = len(active_qop[TERM_EVENT].unique())
    overview[TERM_OBJECT] = len(e2o[TERM_OBJECT].unique())
    overview[TERM_QTY_OBJECTS] = len(active_e2o[TERM_OBJECT].unique())
    overview[TERM_ACTIVITY] = list(qop[TERM_ACTIVITY].unique())
    overview[TERM_QTY_ACTIVITIES] = list(active_qop[TERM_ACTIVITY].unique())
    overview[TERM_OBJECT_TYPE] = list(e2o[TERM_OBJECT_TYPE].unique())
    overview[TERM_QTY_OBJECT_TYPES] = list(active_e2o[TERM_OBJECT_TYPE].unique())
    overview[TERM_COLLECTION] = list(qop[TERM_COLLECTION].unique())
    overview[TERM_QUANTITY_OPERATIONS] = len(qop)
    overview[TERM_ACTIVE_QOP] = len(active_qop)
    overview[TERM_ITEM_TYPES] = list(get_active_item_types(qop))

    return overview
