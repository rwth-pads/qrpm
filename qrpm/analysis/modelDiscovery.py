import pandas as pd
import pm4py

from qrpm.analysis.counterOperations import get_active_instances
from qrpm.analysis.pm4py_interface.interface_pm4py import create_ocel_from_qel, transform_ocpn_to_qnet, \
    create_ocel_from_data_tables
from qrpm.analysis.generalDataOperations import remove_empty_columns, split_instance_and_variable_entries
from qel_simulation import QuantityEventLog, QuantityNet
from qrpm.GLOBAL import TERM_COLLECTION, TERM_ACTIVITY


def mine_basic_qnet_from_qel(qel: QuantityEventLog) -> QuantityNet:
    """Transforms passed QEL to OCEL, mines OCPN using pm4py, transforms OCPN to QNet and adds collections and quantity
    relations."""

    # get ocpn using pm4py
    ocel = create_ocel_from_qel(qel)
    ocpn = pm4py.discover_oc_petri_net(ocel)

    # create qnet from ocpn
    qnet = transform_ocpn_to_qnet(ocpn)

    # add collections and quantity relations
    cp_names = qel.collection_points
    for cp_name in cp_names:
        cp = qnet.create_and_add_collection_point(cp_name)
        cp.item_types = qel.item_types_collection[cp_name]
        cp.silent = False

    quantity_relations = set()
    for active_qop in qel.active_quantity_operations.index:
        event = active_qop[0]
        collection_point = active_qop[1]
        activity = qel.get_activity(event)
        quantity_relations.add((activity, collection_point))

    for qcon in quantity_relations:
        qnet.create_and_add_qarc(qcon[0], qcon[1])

    return qnet

def mine_basic_qnet_from_qel_data_tables(events: pd.DataFrame, objects: pd.DataFrame, e2o: pd.DataFrame, qop: pd.DataFrame = None) -> QuantityNet:
    """Transforms passed QEL to OCEL, mines OCPN using pm4py, transforms OCPN to QNet and adds collections and quantity
    relations."""

    # get ocpn using pm4py
    ocel = create_ocel_from_data_tables(events=events, objects=objects, e2o=e2o)

    ocpn = pm4py.discover_oc_petri_net(ocel)

    # create qnet from ocpn
    qnet = transform_ocpn_to_qnet(ocpn)

    if qop is None or len(qop) == 0:
        return qnet
    else:
        pass
    # add collections and quantity relations
    cp_names = qop[TERM_COLLECTION].unique()
    for cp_name in cp_names:
        cp = qnet.create_and_add_collection_point(cp_name)
        qop_cp = qop.loc[qop[TERM_COLLECTION] == cp_name]
        qop_cp = remove_empty_columns(qop_cp, keep_zeros=False)
        _, item_types = split_instance_and_variable_entries(qop_cp.columns)
        cp.item_types = item_types
        cp.silent = False

    quantity_relations = get_active_instances(qop)
    quantity_relations = quantity_relations[[TERM_ACTIVITY, TERM_COLLECTION]].drop_duplicates()
    quantity_relations = list(quantity_relations.itertuples(index=False, name=None))

    for qcon in quantity_relations:
        qnet.create_and_add_qarc(qcon[0], qcon[1])

    return qnet
