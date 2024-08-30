import pandas as pd
import pm4py

from qel_simulation.simulation import create_object_type
from qel_simulation import QuantityEventLog, QuantityNet
from qrpm.GLOBAL import TERM_EVENT, TERM_ACTIVITY, TERM_TIME, TERM_OBJECT, TERM_OBJECT_TYPE


def load_ocpn_from_file(file_path: str) -> QuantityNet:
    ocel = pm4py.read_ocel2_sqlite(file_path)
    ocpn = pm4py.discover_oc_petri_net(ocel)
    qnet = transform_ocpn_to_qnet(ocpn=ocpn)
    return qnet


def transform_ocpn_to_qnet(ocpn: dict[str: dict[str, pm4py.objects.petri_net]]) -> QuantityNet:
    """
    Takes pm4py object-centric petri net and returns quantity net.
    Currently cannot process take over information on variable arcs.
    :param ocpn: Dict
    :return: QuantityNet object from ocpn
    """

    t_count = 0
    p_count = 0
    arcs = set()
    transition_labels = {}
    transition_identification_label = {}
    place_mapping = {}
    initial_places = set()
    final_places = set()
    for object_type_name, petri_net in ocpn["petri_nets"].items():
        object_type_class = create_object_type(object_type_name=object_type_name, default_attribute_values={})
        node_identification = {}

        for transition in petri_net[0].transitions:

            if transition.label:
                if transition.label in transition_identification_label.keys():
                    transition_name = transition_identification_label[transition.label]
                else:
                    transition_name = f"t{t_count}"
                    transition_labels[transition_name] = transition.label
                    transition_identification_label[transition.label] = transition_name
                    t_count += 1
            else:
                transition_name = f"t{t_count}"
                t_count += 1
            node_identification[transition.name] = transition_name

        for place in petri_net[0].places:
            place_name = f"p{p_count}"
            node_identification[place.name] = place_name

            # specify type of place
            place_mapping[place_name] = object_type_class

            if place.name == "source":
                initial_places.add(place_name)
            elif place.name == "sink":
                final_places.add(place_name)
            else:
                pass

            p_count += 1

        for arc in petri_net[0].arcs:
            qnet_name_source = node_identification[arc.source.name]
            qnet_name_target = node_identification[arc.target.name]
            arcs.add((qnet_name_source, qnet_name_target))

    qn = QuantityNet("ocpn_mined_with_pm4py")
    qn.set_net_structure(arcs=arcs)
    qn.set_initial_places(initial_places=initial_places)
    qn.set_final_places(final_places=final_places)
    qn.set_place_types(place_mapping=place_mapping)
    qn.set_transition_labels(transition_labels=transition_labels)

    # make arcs variable
    variable_connections_ocpn = {(activity, object_type) for object_type, activities in
                                 ocpn['double_arcs_on_activity'].items() for activity in activities if
                                 activities[activity]}
    variable_connections_identified = {(qn.identify_node(activity), qn.identify_object_type(object_type)) for
                                       (activity, object_type) in variable_connections_ocpn}

    variable_arcs = set()
    for (transition, object_type) in variable_connections_identified:
        variable_arcs = variable_arcs.union(
            {(input_place, transition) for input_place in transition.get_input_places_of_otype(object_type)})
        variable_arcs = variable_arcs.union(
            {(transition, output_place) for output_place in transition.get_output_places_of_otype(object_type)})

    qn.make_arcs_variable(variable_arcs)

    return qn

def create_ocel_from_qel(qel: QuantityEventLog):
    """Create pm4py OCEL object from QEL object."""

    # create event table for ocel
    ocel_events = qel.events.reset_index()
    ocel_events = ocel_events.rename(columns={qel.event_id_col: "ocel:eid",
                                              qel.timestamp_col: "ocel:timestamp",
                                              qel.activity_col: "ocel:activity"})

    # create object table for ocel
    obj = pd.DataFrame()
    for object_type, data in qel._object_data.items():
        object_type_data = data.copy()
        object_type_data[qel.object_type_col] = object_type
        obj = pd.concat([obj, object_type_data])
    obj = obj.drop(columns=[qel.object_change])
    obj = obj.rename(columns={qel.object_id_col: "ocel:oid",
                              qel.timestamp_col: "ocel:timestamp",
                              qel.object_type_col: "ocel:type"})

    # create relationship table for ocel
    e2o = qel.e2o

    e2o = pd.merge(e2o, qel.events[[qel.activity_col, qel.timestamp_col]],
                   left_on=qel.e2o_event,
                   right_index=True, how="left").copy()

    e2o = e2o.rename(columns={qel.activity_col: "ocel:activity",
                              qel.e2o_event: "ocel:eid",
                              qel.timestamp_col: "ocel:timestamp",
                              qel.qualifier: "ocel:qualifier"})

    e2o = pd.merge(e2o, qel.objects[qel.object_type_col],
                   left_on=qel.e2o_object,
                   right_index=True, how="inner").copy()

    e2o = e2o.rename(columns={qel.e2o_object: "ocel:oid",
                              qel.object_type_col: "ocel:type"})

    ocel = pm4py.OCEL(events=ocel_events, objects=obj, relations=e2o)

    ocel.objects["ocel:timestamp"] = pd.to_datetime(ocel.objects["ocel:timestamp"])
    ocel.events["ocel:timestamp"] = pd.to_datetime(ocel.events["ocel:timestamp"])

    return ocel

def create_ocel_from_data_tables(events, objects, e2o):
    """Create pm4py OCEL object from data tables."""

    # create event table for ocel
    ocel_events = events.copy()
    ocel_events = ocel_events.rename(columns={TERM_EVENT: "ocel:eid",
                                              TERM_TIME: "ocel:timestamp",
                                              TERM_ACTIVITY: "ocel:activity"})

    # create object table for ocel
    obj = objects.copy()
    if TERM_TIME in obj.columns:
        obj[TERM_TIME] = pd.to_datetime(obj[TERM_TIME])
        obj = obj.sort_values(by=[TERM_TIME], ascending=True)
    else:
        pass

    obj = obj.drop_duplicates(subset=[TERM_OBJECT], keep="last")
    obj = obj.rename(columns={TERM_OBJECT: "ocel:oid",
                              TERM_TIME: "ocel:timestamp",
                              TERM_OBJECT_TYPE: "ocel:type"})

    # create relationship table for ocel
    e2o = e2o.set_index(TERM_EVENT)

    e2o = pd.merge(e2o, ocel_events[["ocel:eid", "ocel:activity", "ocel:timestamp"]],
                   left_index=True,
                   right_on="ocel:eid", how="left").copy()

    e2o = e2o.rename(columns={TERM_OBJECT: "ocel:oid",
                              TERM_OBJECT_TYPE: "ocel:type"})

    e2o.loc[:, "ocel:qualifier"] = None
    e2o = e2o.reset_index(drop=True)

    ocel = pm4py.OCEL(events=ocel_events, objects=obj, relations=e2o)

    ocel.objects["ocel:timestamp"] = pd.to_datetime(ocel.objects["ocel:timestamp"])
    ocel.events["ocel:timestamp"] = pd.to_datetime(ocel.events["ocel:timestamp"])

    if "Object Types" in ocel.objects.columns:
        ocel.objects = ocel.objects.rename(columns={"Object Types": "ocel:type"})
        # print("Object Type column renamed in Object table.")
    else:
        pass

    if "Object Types" in ocel.relations.columns:
        ocel.relations = ocel.relations.rename(columns={"Object Types": "ocel:type"})
        # print("Object Type column renamed in e2o table.")
    else:
        pass

    return ocel
