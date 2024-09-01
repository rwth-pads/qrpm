import qrpm.app.layout as layout
from qrpm.GLOBAL import (TERM_EVENT, TERM_QTY_EVENTS, TERM_ACTIVITY, TERM_QTY_ACTIVITIES, TERM_OBJECT, TERM_QTY_OBJECTS, \
    TERM_OBJECT_TYPE, TERM_QTY_OBJECT_TYPES, TERM_COLLECTION, TERM_ITEM_TYPES, TERM_ACTIVE_QOP, TERM_QUANTITY_RELATIONS,
                    TERM_INITIAL_ILVL)
from qel_simulation import QuantityEventLog
import qrpm.analysis.quantityOperations as qopp

def get_log_overview(qel: QuantityEventLog):
    """Get an overview of the quantity event log."""

    log_overview = dict()

    log_overview[TERM_EVENT] = len(qel.events)
    log_overview[TERM_QTY_EVENTS] = len(qel.get_quantity_events())
    log_overview[TERM_ACTIVITY] = list(qel.activities)
    log_overview[TERM_QTY_ACTIVITIES] = list(qel.quantity_activities)
    objs = qel.get_objects()
    log_overview[TERM_OBJECT] = len(objs[TERM_OBJECT].unique())
    log_overview[TERM_QTY_OBJECTS] = len(qel.get_qty_objects())
    log_overview[TERM_OBJECT_TYPE] = list(qel.object_types)
    log_overview[TERM_QTY_OBJECT_TYPES] = list(qel.get_qty_object_types())
    qop = qel.get_quantity_operations()
    log_overview[TERM_ACTIVE_QOP] = len(qopp.get_active_instances(qop))
    log_overview[TERM_COLLECTION] = list(qel.collection_points)
    log_overview[TERM_ITEM_TYPES] = list(qel.item_types)
    log_overview[TERM_QUANTITY_RELATIONS] = list(qel.get_quantity_relations())

    initial_ilvl = dict()
    for cp in qel.collection_points:
        initial_ilvl[cp] = dict(qel.get_initial_item_level_cp(cp=cp))

    log_overview[TERM_INITIAL_ILVL] = initial_ilvl

    return log_overview


def update_qel_overview_numbers(overview):

    events = overview[TERM_EVENT]
    qty_events = overview[TERM_QTY_EVENTS]
    activities = len(overview[TERM_ACTIVITY])
    qactivities = len(overview[TERM_QTY_ACTIVITIES])
    objects = overview[TERM_OBJECT]
    qty_objects = overview[TERM_QTY_OBJECTS]
    object_types = len(overview[TERM_OBJECT_TYPE])
    qty_object_types = len(overview[TERM_QTY_OBJECT_TYPES])
    collections = len(overview[TERM_COLLECTION])
    item_types = len(overview[TERM_ITEM_TYPES])
    active_qop = overview[TERM_ACTIVE_QOP]
    qrs = len(overview[TERM_QUANTITY_RELATIONS])

    return events, activities, objects, object_types, qty_events, qactivities, qty_objects, qty_object_types, collections, item_types, active_qop, qrs

def update_qel_overview_details(overview):

    activities = layout.create_text_list(overview[TERM_ACTIVITY])
    qactivities = layout.create_text_list(overview[TERM_QTY_ACTIVITIES])
    object_types = layout.create_text_list(overview[TERM_OBJECT_TYPE])
    qty_object_types = layout.create_text_list(overview[TERM_QTY_OBJECT_TYPES])
    item_types = layout.create_text_list(overview[TERM_ITEM_TYPES])
    collections = layout.create_text_list(overview[TERM_COLLECTION])
    qrs = parse_quantity_relations(overview[TERM_QUANTITY_RELATIONS])

    return activities, object_types, qactivities, qty_object_types, item_types, collections, qrs

def parse_quantity_relations(quantity_relations: list[dict]) -> list[str]:
    """Converts a list of dictionaries to tuples with activity, collection"""
    qrs = []
    for qr in quantity_relations:
        activity = qr[TERM_ACTIVITY]
        collection = qr[TERM_COLLECTION]
        qrs.append(f"({activity}, {collection})")
    return qrs
