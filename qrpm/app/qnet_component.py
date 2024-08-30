from qrpm.analysis.counterOperations import cp_projection
from qrpm.analysis.modelDiscovery import mine_basic_qnet_from_qel_data_tables
from qrpm.analysis.ocelOperations import activity_selection, events_with_any_object_type, e2o_for_instances
from qrpm.app import layout
from qrpm.app.preparation import get_element_overview
from qel_simulation import QuantityNet, QuantityGraph
from qrpm.GLOBAL import (TERM_ACTIVITY, TERM_COLLECTION, TERM_QUANTITY_RELATIONS, TERM_OBJECT_TYPE,
                         TERM_QUANTITY_OPERATIONS, TERM_EVENT, TERM_QTY_EVENTS, TERM_QTY_ACTIVITIES, TERM_OBJECT,
                         TERM_QTY_OBJECTS, TERM_QTY_OBJECT_TYPES, TERM_ACTIVE_QOP, TERM_ITEM_TYPES)
from graphviz import Source


def discover_qnet(events, objects, e2o, qop) -> (QuantityNet, dict):
    """Discovers the quantity net from the QuantityEventLog object by extending an ocpn mined using pm4py."""

    # mine qnet
    qnet = mine_basic_qnet_from_qel_data_tables(events=events, objects=objects, e2o=e2o, qop=qop)

    qnet_data = dict()
    qnet_data[TERM_ACTIVITY] = {transition.name: transition.label for transition in qnet.transitions}
    qnet_data[TERM_COLLECTION] = [collection.name for collection in qnet.collection_points]
    qnet_data[TERM_QUANTITY_RELATIONS] = [(qarc.source.label, qarc.target.name) for qarc in qnet.quantity_arcs]
    qnet_data[TERM_OBJECT_TYPE] = {place.name: place.object_type.object_type_name for place in qnet.object_places}

    return qnet, qnet_data

def get_dot_string(qnet: QuantityNet) -> str:
    """Get the quantity net from the QuantityEventLog object."""

    # create graphviz graph
    qnet_graph_object = QuantityGraph(qnet)
    qnet_graph_object.create_graph()

    return qnet_graph_object.graph.to_string()

def process_node_selection(selected_node, qnet_data):

    if selected_node in qnet_data[TERM_COLLECTION]:
        return selected_node, TERM_COLLECTION
    elif selected_node in qnet_data[TERM_ACTIVITY].keys():
        activity = qnet_data[TERM_ACTIVITY][selected_node]
        if activity is not None:
            return activity, TERM_ACTIVITY
        else:
            return None, None
    elif selected_node in qnet_data[TERM_OBJECT_TYPE].keys():
        object_type = qnet_data[TERM_OBJECT_TYPE][selected_node]
        return object_type, TERM_OBJECT_TYPE
    else:
        return None, None

def export_qnet(dot_string):
    """Export the quantity net to an .svg file."""
    graph = Source(dot_string)
    graph.render(filename='files\discovered_graph', format='svg', cleanup=True)

def update_element_selection_data_overview(qop, e2o, element_type: str | None, element_name: str | None):

    if element_type == TERM_ACTIVITY:
        qop = activity_selection(data=qop, activities={element_name})
    elif element_type == TERM_COLLECTION:
        qop = cp_projection(qty=qop, cps={element_name})
    elif element_type == TERM_OBJECT_TYPE:
        qop = events_with_any_object_type(events=qop, e2o=e2o, object_types={element_name})
    else:
        raise ValueError(f"Element type {element_type} is not valid.")

    e2o = e2o_for_instances(e2o=e2o, filtered_data=qop, instance_type=TERM_EVENT)
    element_overview = get_element_overview(qop=qop, e2o=e2o)

    return (element_overview[TERM_EVENT],
            element_overview[TERM_QTY_EVENTS],
            len(element_overview[TERM_ACTIVITY]),
            len(element_overview[TERM_QTY_ACTIVITIES]),
            element_overview[TERM_OBJECT],
            element_overview[TERM_QTY_OBJECTS],
            len(element_overview[TERM_OBJECT_TYPE]),
            len(element_overview[TERM_QTY_OBJECT_TYPES]),
            len(element_overview[TERM_COLLECTION]),
            element_overview[TERM_ACTIVE_QOP],
            element_overview[TERM_QUANTITY_OPERATIONS],
            len(element_overview[TERM_ITEM_TYPES]),
            layout.create_text_list(element_overview[TERM_QTY_OBJECT_TYPES]),
            layout.create_text_list(element_overview[TERM_QTY_ACTIVITIES]),
            layout.create_text_list(element_overview[TERM_ITEM_TYPES]),
            layout.create_text_list(element_overview[TERM_COLLECTION]),
            )
