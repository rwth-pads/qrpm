import base64
import json

import numpy as np
import pandas as pd
from dash import dcc, html

from qrpm.analysis.counterOperations import cp_projection, item_type_projection, get_active_instances
import qrpm.analysis.dataVisualisation as viz
import qrpm.app.data_operations.qstate_data as qstate
from qrpm.analysis.ocelOperations import event_selection, filter_events_for_time
from qrpm.analysis.generalDataOperations import split_instance_and_variable_entries, get_descriptive_statistics
from qrpm.analysis.quantityState import get_descriptive_statistics_for_qstate
import qrpm.app.dataStructure as ds
import plotly
from qrpm.GLOBAL import *

def set_filter_options_sublog(ocel_json):

    events, e2o, objects = ds.get_ocel_data(ocel_json)

    # event-based filter options
    activities = list(events[TERM_ACTIVITY].unique())

    non_attributes, event_attributes = split_instance_and_variable_entries(events.columns)
    selected_event_attribute = event_attributes[0] if event_attributes and len(event_attributes) > 0 else None

    # object-based filter options
    object_types = list(objects[TERM_OBJECT_TYPE].unique())
    selected_object_type = object_types[0] if object_types and len(object_types) > 0 else None
    non_attributes, object_attributes = split_instance_and_variable_entries(objects.columns)
    selected_object_attribute = object_attributes[0] if object_attributes and len(object_attributes) > 0 else None

    return (activities, activities,
            event_attributes, selected_event_attribute,
            activities,
            activities,
            activities, activities,
            object_types, object_types,
            object_types, object_attributes, selected_object_attribute,
            object_types, selected_object_type, object_types,
            object_types, selected_object_type)


def set_event_attribute_value_dropdown(event_attribute, event_data):
    return [str(val) for val in event_data[event_attribute].unique()]

def set_object_attribute_value_dropdown(object_attribute, objects):
    return [str(val) for val in objects[object_attribute].unique()]

def set_event_qty_state_filter_values(ilvl, events, selected_cp, selected_its):

    # get relevant ilvl data
    relevant_ilvls = event_selection(event_data=ilvl, event_ids=events[TERM_EVENT].unique())
    relevant_ilvls = cp_projection(qty=relevant_ilvls, cps=selected_cp)
    min_ilvl = relevant_ilvls[selected_its].min().min() if selected_its else None
    max_ilvl = relevant_ilvls[selected_its].max().max() if selected_its else None
    ilvl_range = [min_ilvl, max_ilvl] if selected_its and selected_cp else None

    return min_ilvl, max_ilvl, ilvl_range

def set_filters_for_quantity_data_full_log(qop):

    collections = list(qop[TERM_COLLECTION].unique())
    _, item_types = split_instance_and_variable_entries(qop.columns)

    selected_collection = collections[0] if collections and len(collections) > 0 else None
    selected_item_type = item_types[0] if item_types and len(item_types) > 0 else None

    return (collections, selected_collection, item_types, selected_item_type,
            item_types, item_types,
            collections, collections,
            item_types, item_types,
            collections, collections)

def set_filters_for_quantity_data_sublog(qop):

    collections = list(qop[TERM_COLLECTION].unique())
    _, item_types = split_instance_and_variable_entries(qop.columns)

    return (collections, item_types,
            item_types, item_types,
            collections, collections)

def set_filter_possible_selection_time_period(ocel_json):
    events, e2o, objects = ds.get_ocel_data(ocel_json)

    events[TERM_TIME] = pd.to_datetime(events[TERM_TIME])
    min_time = events[TERM_TIME].min()
    max_time = events[TERM_TIME].max()

    min_date = min_time.date()
    max_date = max_time.date()
    return min_date, max_date


def chart_ilvl_sublog_selection(ilvl, events, item_types, cp, selected_start_date,
                                                    selected_end_date):

    if events is None:
        fig = plotly.graph_objects.Figure()
    else:
        ilvl = item_type_projection(qty=ilvl, item_types=item_types)
        ilvl_events = event_selection(event_data=ilvl, event_ids=events[TERM_EVENT].unique())

        # update chart according to selected date range
        if selected_start_date or selected_end_date:
            ilvl_events = filter_events_for_time(data=ilvl_events, start_time=selected_start_date,
                                                end_time=selected_end_date)
        else:
            pass

        fig = viz.item_level_development_single_cp(ilvl=ilvl_events, cp=cp)

        fig.update_layout(title=f"Item Levels of {item_types} for {cp}",
                          showlegend=False)

    fig_comp = dcc.Loading(id="loading_events-cp-ilvl-graph", style={"display": "block"},
                type="circle", color='#0098A1',
                target_components={"events-ilvl-graph": "figure"}, children=[
                dcc.Graph(figure=fig)
        ]),

    return fig_comp

def charts_sublog_cp_active(qop):

    if qop is not None:
        cp_active_freq = viz.show_active_collection_point_distribution_event(qop=qop)
        cp_active_comb = viz.show_active_collection_point_combinations(qop=qop)
    else:
        cp_active_freq = plotly.graph_objects.Figure()
        cp_active_comb = plotly.graph_objects.Figure()

    fig_comp = html.Div([
        html.Div(style={"display": "flex", "flexDirection": "row"}, children=[
                    html.Div(style={"width": "50%", "align": "center", "textAlign": "center"},
                             hidden=False, children=[
                            html.H5("Number of cp-active Events per Collection Point"),
                            dcc.Loading(id="loading_events-cp-active-distribution-graph", style={"display": "block"},
                                        type="circle", color='#0098A1',
                                        target_components={"events-cp-active-distribution-graph": "figure"}, children=[
                                    dcc.Graph(figure=cp_active_freq)
                                ])
                        ]),
                    html.Div(style={"width": "50%", "align": "center", "textAlign": "center"},
                             hidden=False, children=[
                            html.H5("Frequency of Events with cp-active Combination"),
                            html.Div(
                                "(Counts the entire combination of active collection points--Total number = total number of cp-active events in current selection.)"),
                            dcc.Loading(id="loading_events-cp-active-combination-graph", style={"display": "block"},
                                        type="circle", color='#0098A1',
                                        target_components={"events-cp-active-combination-graph": "figure"}, children=[
                                    dcc.Graph(figure=cp_active_comb),
                                ])
                        ]),
                ])
        ])
    return fig_comp


def charts_sublog_it_active(qop):
    if qop is not None:
        it_active_freq = viz.show_active_item_type_distribution_per_event(qop=qop)
        it_active_comb = viz.show_active_item_type_combinations_and_frequencies_per_event(qop=qop)
    else:
        it_active_freq = plotly.graph_objects.Figure()
        it_active_comb = plotly.graph_objects.Figure()

    fig_comp = html.Div([
        html.Div(style={"display": "flex", "flexDirection": "row"}, children=[
            html.Div(style={"width": "50%", "align": "center", "textAlign": "center"},
                     hidden=False, children=[
                    html.H5("Number of item-type-active Events per Item type"),
                    dcc.Loading(id="loading_events-cp-active-distribution-graph", style={"display": "block"},
                                type="circle", color='#0098A1',
                                target_components={"events-cp-active-distribution-graph": "figure"}, children=[
                            dcc.Graph(figure=it_active_freq)
                        ])
                ]),
            html.Div(style={"width": "50%", "align": "center", "textAlign": "center"},
                     hidden=False, children=[
                    html.H5("Frequency of Item type combinations in active Events"),
                    html.Div(
                        "(Counts the entire combination of active item types, total number = total number of it-active events in current selection.)"),
                    dcc.Loading(id="loading_events-it-active-combination-graph", style={"display": "block"},
                                type="circle", color='#0098A1',
                                target_components={"events-it-active-combination-graph": "figure"}, children=[
                            dcc.Graph(figure=it_active_comb),
                        ])
                ]),
        ])
    ])
    return fig_comp

def sublog_returns(ocel, qty):

    if ocel is None:
        if qty[TERM_QUANTITY_OPERATIONS] is None:
            return None, ds.prepare_data_for_storage(qty), 0, 0, 0, 0, 0, 0
        else:
            raise ValueError("OCEL is empty but qop is not.")
    else:
        pass

    events = ocel[TERM_EVENT_DATA]
    objects = ocel[TERM_OBJECT_DATA]

    if qty is not None:
        qop = qty[TERM_QUANTITY_OPERATIONS]
        oqty = qty[TERM_OBJECT_QTY]
        active_oqtys = get_active_instances(oqty)
        no_qty_objects = len(active_oqtys[TERM_OBJECT].unique()) if len(active_oqtys) > 0 else 0

        if qop is None:
            no_qty_events = 0
            qups = 0
            qops = 0
        else:
            active_qops = get_active_instances(qop).replace(0, np.nan)
            no_qty_events = len(active_qops[TERM_EVENT].unique())
            qups = active_qops.count().sum()
            qops = len(active_qops)
    else:
        no_qty_objects = 0
        no_qty_events = 0
        qups = 0
        qops = 0

    no_events = len(events[TERM_EVENTS].unique())
    no_objects = len(objects[TERM_OBJECT].unique())

    return ds.prepare_data_for_storage(ocel), ds.prepare_data_for_storage(qty), no_qty_events, no_events, no_qty_objects, no_objects, qups, qops

def quantity_state_development_graph(processed_qstate_json, qty_json, ilvl_type, ilvl_display, display_type):

    ilvl, events = qstate.quantity_state_development(processed_qstate_json, qty_json, ilvl_display)

    if ilvl_type == PRE_EVENT_ILVL:
        post_ilvl = False
    else:
        post_ilvl = True

    fig = viz.item_level_development_activity_executions(ilvl=ilvl,
                                                          events=events,
                                                          post_ilvl=post_ilvl, joint_display=display_type)

    return dcc.Loading(id="loading_qstate_development", style={"display": "block"}, type="circle", color='#0098A1',
                target_components={"qstate-development-graph": "figure"}, children=[
            dcc.Graph(id="qstate-development-graph", figure=fig, style={'height': '700px', 'width': '100%'})
        ]),



def create_cp_stats_quantity_state(processed_qstate_json, qty_json, ilvl_display):
    ilvl = ds.get_single_dataframe(processed_qstate_json)
    qop, orig_ilvl, oqty = ds.get_qty_data(qty_json)

    if ilvl_display == TERM_ALL:
        pass
    else:
        ilvl = event_selection(event_data=ilvl, event_ids=qop[TERM_EVENT].unique())

    stats = get_descriptive_statistics_for_qstate(data=ilvl)

    return create_data_table_elements_for_stats(stats=stats, measure=False)


def create_data_table_elements_for_stats(stats: pd.DataFrame, measure: bool = True):

    stats = stats.reset_index()
    if measure:
        stats_columns = [{"name": "Measure", "id": "index"}]
    else:
        stats_columns = [{"name": "", "id": "index"}]

    stats_columns.extend([{"name": col, "id": col} for col in stats.columns if col != "index"])

    return stats.to_dict("records"), stats_columns

def create_data_table_elements(df: pd.DataFrame):

    df_columns = ([{"name": col, "id": col} for col in df.columns])

    return df.to_dict("records"), df_columns

def update_item_level_distribution(ilvl, ilvl_view):

    fig = viz.boxplots_of_distribution(data=ilvl, view=ilvl_view)

    stats = get_descriptive_statistics(data=ilvl, view=ilvl_view, count_zeros_frequency=True)

    data, columns = create_data_table_elements_for_stats(stats=stats)

    component = dcc.Loading(id="loading-ilvl-boxplots", style={"display": "block"}, type="circle", color='#0098A1',
                            target_components={"ilvl-boxplots_chart": "figure"}, children=[
                        dcc.Graph(id="ilvl-boxplots_chart", figure=fig)
                    ])

    return component, data, columns

def possible_selection_period_qop_filter(qty_relation):

    qty_relation.loc[:, TERM_TIME] = pd.to_datetime(qty_relation[TERM_TIME])
    min_time = qty_relation[TERM_TIME].min()
    max_time = qty_relation[TERM_TIME].max()

    min_date = min_time.date()
    max_date = max_time.date()

    return min_date, max_date #, start_date, end_data, 0

def quantity_update_distribution(qty_relation, qop_active, qop_view, display_points):

    fig = viz.boxplots_of_distribution(data=qty_relation, view=qop_view, display_points=display_points)

    if qop_active == TERM_ALL:
        stats = get_descriptive_statistics(data=qty_relation, view=qop_view, count_zeros_frequency=True)
    elif qop_active == TERM_ACTIVE_OPERATIONS:
        stats = get_descriptive_statistics(data=qty_relation, view=qop_view, count_zeros_frequency=False)
    else:
        stats = get_descriptive_statistics(data=qty_relation, view=qop_view, count_zeros_frequency=False)

    data, columns = create_data_table_elements_for_stats(stats=stats)

    return fig, data, columns


def plot_qup_distribution(qty_relation, item_type, view):

    # filter data for passed item type
    if TERM_VALUE in qop.columns:
        qop = qop.loc[qop[TERM_ITEM_TYPES] == item_type, :]
    else:
        non_item_types, it = split_instance_and_variable_entries(qop.columns)
        qop = qop.loc[:, non_item_types + [item_type]]

    fig = viz.boxplots_of_distribution(data=qop, view=view)

    return fig



