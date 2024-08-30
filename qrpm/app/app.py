import json

import dash
import plotly
from dash import Dash, dcc, html, Input, Output, State, callback

import qrpm.analysis.dataVisualisation as viz
import qrpm.app.layout as layout
import qrpm.app.operations as operations
import qrpm.app.data_operations.log_overview as log
import qrpm.app.data_operations.qstate_data as qstate
import qrpm.app.data_operations.qop_data as qopo

from qrpm.analysis.generalDataOperations import split_instance_and_variable_entries
from qrpm.GLOBAL import CHART_COLOURS, TERM_ALL, TERM_COLLECTION, TERM_ITEM_TYPES, PRE_EVENT_ILVL, STATE_DEMO, TOOL_STATE_QTY

import qrpm.app.dataStructure as ds
import qrpm.app.qnet_component as qdisc
import qrpm.app.data_operations.sublog_creation as slc


external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
AppTitle = "Quantity-related Process Mining"

app = Dash(title=AppTitle, external_stylesheets=external_stylesheets)

app.layout = html.Div(style={"padding": 15, "display": "block"}, children=[
    layout.UploadComponent,
    dcc.Store(id='raw-store'), # uploaded raw data
    dcc.Store(id='ocel'), # normal ocal data
    dcc.Store(id='quantity-data'), # additional qty related data
    dcc.Store(id='qop-processed'), # data for qop tab (applied operations on qop)
    dcc.Store(id='qty-relation'), # data for execution analysis and qup analysis
    dcc.Store(id='qstate-processed'), # data for qstate tab (applied operations on qstate)
    dcc.Store(id='qstate-execution'), # data for execution execution analysis data
    dcc.Store(id='state'),
    dcc.Store(id='qnet-data'),


    # dcc.Store(id='overview-store'),
    # dcc.Store(id='relevant-qop-data'),
    # dcc.Store(id="event-selection-store"),
    # dcc.Store(id="object-selection-store"),
    # dcc.Store(id='ilvl-data'),
    # dcc.Store(id="relevant-ilvl-data"),
    # dcc.Store(id="ilvl-execution-data"),
    # dcc.Store(id="qop-processed-data"),
    # dcc.Store(id="qop-analysis-data"),
    layout.ProcessOverview,
    layout.QRPMComponent
])

##############################################################################
########################## LOG UPLOAD & OVERVIEW #############################
##############################################################################

@callback(Output('file_selection', 'children'),
          Output('file_selection', 'style'),
          Input('upload-data', 'filename'))
def file_selection_button(filename):
    if filename is not None:
        return f'{filename}', {'color': CHART_COLOURS[1], "fontSize": 19, "align": "center", "height": "2.5cm", "width": "99%",
                               "textAlign": "center"}
    else:
        return "Add Event Log (.sqlite)", {"fontSize": 19, "height": "2.5cm", "width": "99%", "textAlign": "center"}

@callback(
    Output('demo-data', 'children'),
          Output('submit-button', 'children'),
        Output('raw-store', 'data'),
    Output('qel-overview', 'style'),
    Output('state', 'data'),
          Input("demo-data", "n_clicks"),
          Input('submit-button', 'n_clicks'),
          State('upload-data', 'contents'))
def upload_file(demo, n_clicks, contents):
    ctx = dash.callback_context

    if not ctx.triggered:
        return "Demo Data", 'Submit', None, {"display": "none"}, None
    else:
        button_id = ctx.triggered[0]['prop_id'].split('.')[0]

    if button_id == 'demo-data':

        # if demo button is clicked
        overview_json, state_json = ds.parse_demo_data()

        return 'Demo added', "Submit", overview_json, {"display": "block"}, state_json

    elif button_id == "submit-button" and contents is not None:

        # create QEL object
        qel = ds.parse_upload(contents)

        overview_json, state_json = ds.create_initial_stores(qel)

        return "Demo Data", 'File added', overview_json, {"display": "block"}, state_json
    else:
        return "Demo Data", 'Submit', None, {"display": "none"}, None

@callback(Output('qnet', 'dot_source'),
          Output('qnet', 'style'),
          Output("qnet-data", "data"),
          State('state', 'data'),
          Input('raw-store', 'data'),
          State("quantity-data", "data"),
          State("ocel", "data"),
          Input("rediscover-qnet", "n_clicks"))
def mine_qnet(state, overview_json, qty_data_json, ocel_json, *args):
    ctx = dash.callback_context

    if not ctx.triggered or not overview_json:
        return None, {'display': 'none'}, None
    else:
        button_id = ctx.triggered[0]['prop_id'].split('.')[0]

    if button_id == 'raw-store':

        state = json.loads(state)
        if state[STATE_DEMO]:

            with open("App/files/qnet_demo.dot", 'r') as file:
                dot_string = file.read()

            with open("App/files/qnet_data.json", 'r') as f:
                qnet_data = json.load(f)

            qnet_data_json = json.dumps(qnet_data)

            return (dot_string,
                    {'display': 'block', "height": "50%", "width": "75%", "margin": "10px", "verticalAlign": "middle"},
                    qnet_data_json)

        else:
            events, objects, e2o, qop, ilvl, oqty = ds.get_raw_data_dataframes(overview_json)

    else:
        if ocel_json:
            events, e2o, objects = ds.get_ocel_data(ocel_json)
            if qty_data_json is not None:
                qop, ilvl, oqty = ds.get_qty_data(qty_data_json)
            else:
                qop = None
        else:
            return None, {'display': 'none'}, None


    qnet, qnet_data = qdisc.discover_qnet(events=events, objects=objects, e2o=e2o, qop=qop)
    dot_string = qdisc.get_dot_string(qnet)
    qnet_data_json = json.dumps(qnet_data)

    with open("App/files/qnet_data.json", 'w') as file:
        json.dump(qnet_data, file)

    with open("App/files/qnet_demo.dot", 'w') as f:
        f.write(dot_string)

    return dot_string, {'display': 'block', "height": "50%", "width": "75%", "margin": "10px",
                        "verticalAlign": "middle"}, qnet_data_json

@callback(Output("loading-qel", "style"),
          Input('raw-store', 'data'))
def show_qel_overview(overview_json):
    if overview_json is not None:
        return {"display": "block"}
    else:
        return {"display": "none"}

@callback(Output("qnet-export-file", "data"),
          State("qnet", "dot_source"),
          Input("export-qnet-button", "n_clicks"),
          prevent_initial_call=True)
def export_qnet(dot_source, *args):
    qdisc.export_qnet(dot_source)
    return dcc.send_file('files/discovered_graph.svg')

@callback(Output("qel-no-events", "children"),
            Output("qel-no-activities", "children"),
            Output("qel-no-objects", "children"),
            Output("qel-no-object-types", "children"),
            Output("qel-no-q-events", "children"),
            Output("qel-no-q-activities", "children"),
            Output("qel-no-q-objects", "children"),
            Output("qel-no-q-object-types", "children"),
            Output("qel-no-collections", "children"),
            Output("qel-no-item-types", "children"),
            Output("qel-no-qops", "children"),
            Output("qel-no-quantity-relations", "children"),
            Input('raw-store', 'data'))
def update_numbers_qel_overview(overview_json):
    if overview_json is not None:
        overview = ds.get_raw_data(overview_json)
        return log.update_qel_overview_numbers(overview)
    else:
        return None, None, None, None, None, None, None, None, None, None, None, None

@callback(Output("qel-activities", "children"),
        Output("qel-object-types", "children"),
        Output("qel-q-activities", "children"),
        Output("qel-q-object-types", "children"),
        Output("qel-item-types", "children"),
        Output("qel-collections", "children"),
        Output("qel-quantity-relations", "children"),
        Input('raw-store', 'data'))
def update_qel_overview_details(overview_json):
    if overview_json is not None:
        pass
    else:
        return None, None, None, None, None, None, None
    overview = ds.get_raw_data(overview_json)
    return log.update_qel_overview_details(overview)

@callback(Output("data-overview", "style"),
Input("raw-store", "data"))
def display_analysis(overview_data):
    if overview_data:
        return {"margin": "5px", "display": "block"}
    else:
        return {"display": "none"}

##############################################################################
########################## Q-NET COMPONENT ###################################
##############################################################################


@callback(Output('process-overview', 'style'),
          Input("raw-store", "data"))
def display_qnet(data):
    if data is not None:
        return {"display": "block", "margin": "5px"}
    else:
        return {"display": "none"}

@callback(Output('selection-info', 'style'),
          Output("element-type", 'children'),
          Output("element-name", 'children'),
          Input("qnet", "selected_node"),
          State("qnet-data", "data"))
def display_selection_info(selected_node, qnet_data_json):
    """Display collection information if the selected node is a collection."""

    return_none = {"display": "none"}, None, None
    style_selected = {"display": "block", "marginTop": "25px"}

    if qnet_data_json is not None:
        qnet_data = json.loads(qnet_data_json)
    else:
        return return_none

    name, title = qdisc.process_node_selection(selected_node, qnet_data)

    if title is not None:
        return style_selected, title, name
    else:
        return return_none

@callback(Output("selection-overview", "style"),
          Input("raw-store", "data"),)
def display_selection_overview(overview_data):
    if overview_data:
        return {"display": "block"}
    else:
        return {"display": "none"}

@callback(
          Output("selection-no-events", "children"),
          Output("selection-no-qty-events", "children"),
          Output("selection-no-activities", "children"),
          Output("selection-no-qactivities", "children"),
          Output("selection-no-objects", "children"),
          Output("selection-no-qobjects", "children"),
          Output("selection-no-object-types", "children"),
          Output("selection-no-qobject-types", "children"),
          Output("selection-no-collections", "children"),
        Output("selection-no-active-qops", "children"),
          Output("selection-no-qops", "children"),
          Output("selection-no-item-types", "children"),
          Output("selection-q-object-types", "children"),
          Output("selection-q-activities", "children"),
          Output("selection-q-item-types", "children"),
        Output("selection-collections", "children"),
          Input("element-type", "children"),
          Input("element-name", "children"),
          Input("raw-store", "data"))
def update_element_overview(element_type, element_name, overview_json):
    if overview_json:
        pass
    else:
        return None, None, None, None, None, None, None, None, None, None, None, None, [], [], [], []

    if element_type and element_name:
        events, objects, e2o, qop, ilvl, oqty = ds.get_raw_data_dataframes(overview_json)
        return qdisc.update_element_selection_data_overview(element_type=element_type, element_name=element_name,
                                                                 qop=qop, e2o=e2o)
    else:
        return None, None, None, None, None, None, None, None, None, None, None, None, [], [], [], []


##############################################################################
########################## EVENT & OBJECT SELECTION ##########################
##############################################################################

##### if not QEL but only OCEL 2.0, don't show any of the QEL related figures and selections

@callback(Output("analysis", "style"),
          Output("sublog-qty-projection", "style"),
          Output("sublog_ilvl", "style"),
          Output("sublog_it-active", "style"),
          Output("sublog_cp-active", "style"),
          Output("active-events-selection", "style"),
          Input("state", "data"))
def show_qty_related_elements(state):
    if state:
        state = json.loads(state)
        if state[TOOL_STATE_QTY]:
            return [{"display": "block"}]*6
        else:
            pass
    else:
        pass
    return [{"display": "none"}]*6


### Filters for sublog selection ###

@callback(Output("events-total-objects-int", "value"),
          Output("events-execution-int", "value"),
          Output("events-objects-object-type-int", "value"),
          Output("events-active-selection", "value"),
          Output("events-time-period", "start_date"),
          Output("events-time-period", "end_date"),
          Output("events-cp-active-all-any", "value"),
          Output("events-it-active-all-any", "value"),
          Input("event-selection-reset", "n_clicks"))
def reset_filter_values_after_log_reset(*args):
    # TODO: also reset selections etc in quantity data tabs
    return None, None, None, TERM_ALL, None, None, TERM_ALL, TERM_ALL

@callback(Output("events-activity-filter", "options"),
          Output("events-activity-filter", "value"),
          Output("events-attribute-attribute-dropdown", "options"),
          Output("events-attribute-attribute-dropdown", "value"),
          Output("qstate-execution-activity-dropdown", "options"),
          Output("qop-activity-dropdown", "options"),
          Output("objects-activity-execution-filter", "options"),
          Output("objects-activity-iteration-filter", "options"),
          Output("events-object_type-filter", "options"),
          Output("object-type-filter", "options"),
          Output("object-type-filter", "value"),
          Output("events-object-attribute-dropdown", "options"),
          Output("events-object-attribute-dropdown", "value"),
          Output("events-execution-object-type-dropdown", "options"),
          Output("events-execution-object-type-dropdown", "value"),
          Output("events-objects-object-type-dropdown", "options"),
          Output("object-type-dropdown", "options"),
          Output("object-type-dropdown", "value"),

          Input("ocel", "data"))
def set_filters_based_on_event_data(ocel_json):
    if ocel_json:
        return operations.set_filter_options_sublog(ocel_json)
    else:
        return [], [], [], None, [], [], [], [], [], [], [], [], None, [], None, [], [], None

@callback(Output("events-attribute-value-dropdown", "options"),
          Input("events-attribute-attribute-dropdown", "value"),
          State("ocel", "data"))
def set_attribute_value_dropdown(event_attribute, ocel_json):
    # TODO: Also allow for anything EXCEPT for the selected attribute / multiple attributes
    if event_attribute and ocel_json:
        events, e2o, objects = ds.get_ocel_data(ocel_json)
        return operations.set_event_attribute_value_dropdown(event_attribute=event_attribute, event_data=events)
    else:
        return []

@callback(Output("events-object-attribute-value-dropdown", "options"),
          Input("events-object-attribute-dropdown", "value"),
          State("ocel", "data"))
def set_object_attribute_value_dropdown(object_attribute, ocel_json):
    if object_attribute and ocel_json:
        events, e2o, objects = ds.get_ocel_data(ocel_json)
        return operations.set_object_attribute_value_dropdown(object_attribute=object_attribute, objects=objects)
    else:
        return []

@callback(Output("events-time-period", "min_date_allowed"),
          Output("events-time-period", "max_date_allowed"),
          Input("ocel", "data"))
def possible_selection_period_event_filter(ocel_json):
    if ocel_json:
        return operations.set_filter_possible_selection_time_period(ocel_json)
    else:
        return None, None

@callback(Output("events-ilvl-range", "min"),
          Output("events-ilvl-range", "max"),
          Output("events-ilvl-range", "value"),
          Input("quantity-data", "data"),
          Input("ocel", "data"),
          Input("events-ilvl-cp-dropdown", "value"),
          Input("events-ilvl-item-type-dropdown", "value"))
def set_event_qty_state_filter_values(qty_json, ocel_json, selected_cp, selected_its):
    if qty_json:
        if ocel_json:
            events, e2o, objects = ds.get_ocel_data(ocel_json)
            qop, ilvl, oqty = ds.get_qty_data(qty_json)
            return operations.set_event_qty_state_filter_values(ilvl=ilvl, events=events, selected_cp=selected_cp,
                                                                selected_its=selected_its)
        else:
            pass
    else:
        pass

    return None, None, []

@callback(
          Output("events-ilvl-cp-dropdown", "options"),
          Output("events-ilvl-cp-dropdown", "value"),
          Output("events-ilvl-item-type-dropdown", "options"),
          Output("events-ilvl-item-type-dropdown", "value"),
          Output("qel-item-type-projection", "options"),
          Output("qel-item-type-projection", "value"),
          Output("qel-collection-point-projection", "options"),
          Output("qel-collection-point-projection", "value"),
          Output("ilvl-item-type-projection", "options"),
          Output("ilvl-item-type-projection", "value"),
          Output("ilvl-collection-point-projection", "options"),
          Output("ilvl-collection-point-projection", "value"),
          Input("raw-store", "data"))
def update_filters_based_on_quantity_data_full_log(overview_json):
    if overview_json is not None:
        events, objects, e2o, qop, ilvl, oqty = ds.get_raw_data_dataframes(overview_json)
        if qop is not None:
            return operations.set_filters_for_quantity_data_full_log(qop=qop)
        else:
            pass
    else:
        pass
    return [], None, [], [], [], [], [], [], [], [], [], []

@callback(Output("events-cp-active-filter", "options"),
          Output("events-it-active-filter", "options"),
          Output("qop-item-type-projection", "options"),
          Output("qop-item-type-projection", "value"),
          Output("qop-collection-point-projection", "options"),
          Output("qop-collection-point-projection", "value"),
          Input("quantity-data", "data"))
def update_filters_based_on_quantity_data_sublog(qty_json):
    if qty_json:
        qop, ilvl, oqty = ds.get_qty_data(qty_json)
        if qop is not None:
            return operations.set_filters_for_quantity_data_sublog(qop=qop)
        else:
            pass
    else:
        pass
    return [], [], [], [], [], []

### Figures OCEL sublog selection ###

@callback(Output("events-activity-graph", "figure"),
          Output("object-type-graph", "figure"),
          Output("events-object-type-graph", "figure"),
          Output("events-objects-object-type-graph", "figure"),
          Output("events-total-objects-graph", "figure"),
          Input("ocel", "data"))
def graphs_based_on_ocel(ocel_json):
    if ocel_json:
        pass
    else:
        return [plotly.graph_objects.Figure()]*5

    events, e2o, objects = ds.get_ocel_data(ocel_json)

    activities_graph = viz.plot_activity_distribution(events)
    object_type_graph = viz.plot_involved_objects_per_type(objects)
    event_ot_graph = viz.show_object_type_combination_for_events(events=events, e2o=e2o)
    no_objects_of_ot_graph = viz.plot_objects_per_object_type_in_events(e2o=e2o)
    total_objects_chart = viz.plot_number_of_involved_objects(e2o=e2o, events=events)

    return activities_graph, object_type_graph, event_ot_graph, no_objects_of_ot_graph, total_objects_chart

@callback(Output("events-attribute-graph", "figure"),
          Input("ocel", "data"),
          Input("events-attribute-attribute-dropdown", "value"))
def event_attribute_graph(ocel_json, attribute):
    if ocel_json and attribute:
        events, e2o, objects = ds.get_ocel_data(ocel_json)
        return viz.show_event_attribute_values(events=events, attribute=attribute)
    else:
        return plotly.graph_objects.Figure()

@callback(Output("objects-activity-execution-graph", "figure"),
          Input("ocel", "data"),
          Input("object-type-dropdown", "value"))
def activities_for_object_type_graph(ocel_json, object_type):
    if ocel_json and object_type:
        events, e2o, objects = ds.get_ocel_data(ocel_json)
        return viz.activities_object_type_involvement(e2o=e2o, events =events, object_type=object_type)
    else:
        return plotly.graph_objects.Figure()

@callback(Output("objects-multi-execution-activity-graph", "figure"),
            Input("ocel", "data"),
          Input("object-type-dropdown", "value"))
def object_type_activity_iterations(ocel_json, object_type):
    if ocel_json and object_type:
        events, e2o, objects = ds.get_ocel_data(ocel_json)
        return viz.objects_activity_execution_frequency(e2o=e2o, events=events, object_type=object_type)
    else:
        return plotly.graph_objects.Figure()

@callback(Output("events-object-attribute-graph", "figure"),
          Input("ocel", "data"),
          Input("events-object-attribute-dropdown", "value"))
def object_attribute_graph(ocel_json, attribute):
    if ocel_json:
        events, e2o, objects = ds.get_ocel_data(ocel_json)
        return viz.show_object_attribute_values(objects=objects, attribute=attribute)
    else:
        return plotly.graph_objects.Figure()

@callback(Output("events-execution-graph", "figure"),
          Input("ocel", "data"),
          Input("events-execution-object-type-dropdown", "value"))
def events_execution_graph(ocel_json, object_type):
    if ocel_json:
        events, e2o, objects = ds.get_ocel_data(ocel_json)
        return viz.plot_activity_executions_for_object_of_object_type(e2o=e2o, events=events, object_type=object_type)
    else:
        return plotly.graph_objects.Figure()

@callback(Output("events-active-graph", "figure"),
          Input("ocel", "data"),
          Input("quantity-data", "data"))
def quantity_active_events_graph(ocel_json, qty_json):
    if qty_json:
        qop, ilvl, oqty = ds.get_qty_data(qty_json)
        if qop is None:
            pass
        else:
            return viz.show_active_events(qop=qop)
    else:
        pass

    if ocel_json is not None:
        events, e2o, objects = ds.get_ocel_data(ocel_json)
        event_data, attributes = split_instance_and_variable_entries(events)
        events = events.loc[:, event_data]
        return viz.show_active_events(qop=events)
    else:
        return plotly.graph_objects.Figure()


@callback(Output("cp-active-figures", "children"),
          Output("it-active-figures", "children"),
          Input("quantity-data", "data"))
def sublog_quantity_charts(qty_json):
    if qty_json:
        pass
    else:
        return None, None

    qop, ilvl, oqty = ds.get_qty_data(qty_json)

    events_cp_active_component = operations.charts_sublog_cp_active(qop=qop)
    events_it_active_component = operations.charts_sublog_it_active(qop=qop)

    return events_cp_active_component, events_it_active_component

@callback(Output("sublog_ilvl-figure", "children"),
          Input("quantity-data", "data"),
          Input("ocel", "data"),
          Input("events-ilvl-cp-dropdown", "value"),
          Input("events-ilvl-item-type-dropdown", "value"),
          Input("events-time-period", "start_date"),
          Input("events-time-period", "end_date"))
def chart_ilvl_sublog_selection(qty_json, ocel_json, cp, item_types, selected_start_date, selected_end_date):

    if qty_json and cp and item_types:
        qop, ilvl, oqty = ds.get_qty_data(qty_json)
        if ocel_json:
            events, e2o, objects = ds.get_ocel_data(ocel_json)
        else:
            events = None

        return operations.chart_ilvl_sublog_selection(ilvl=ilvl, events=events,
                                                          cp=cp, item_types=item_types,
                                                          selected_start_date=selected_start_date,
                                                          selected_end_date=selected_end_date)

    else:
        return None


@callback(Output("ocel", "data"),
          Output("quantity-data", "data"),
          Output("qevents_sublog", "children"),
          Output("events_sublog", "children"),
          Output("qobjects_sublog", "children"),
          Output("objects_sublog", "children"),
          Output("qups_sublog", "children"),
          Output("qops_sublog", "children"),
        #### Inputs
          # Data
          Input("raw-store", "data"),
          State("ocel", "data"),
          State("quantity-data", "data"),

          # Selections
          State("events-activity-filter", "value"),
          State("events-attribute-value-dropdown", "value"),
          State("events-attribute-attribute-dropdown", "value"),
          State("events-object_type-filter", "value"),
          State("events-object-attribute-dropdown", "value"),
          State("events-object-attribute-value-dropdown", "value"),
          State("events-objects-object-type-dropdown", "value"),
          State("events-objects-object-type-int", "value"),
          State("events-execution-object-type-dropdown", "value"),
          State("events-execution-int", "value"),
          State("events-total-objects-int", "value"),
          Input("events-active-selection", "value"),
          State("events-cp-active-filter", "value"),
          State("events-cp-active-all-any", "value"),
          State("events-it-active-filter", "value"),
          State("events-it-active-all-any", "value"),
          State("events-ilvl-cp-dropdown", "value"),
          State("events-ilvl-item-type-dropdown", "value"),
          State("events-ilvl-range", "value"),
          State("events-time-period", "start_date"),
          State("events-time-period", "end_date"),
          State("qel-collection-point-projection", "value"),
          State("qel-item-type-projection", "value"),
          State("object-type-filter", "value"),
          State("object-type-dropdown", "value"),
          State("objects-activity-execution-filter", "value"),
          State("objects-activity-iteration-filter", "value"),
          State("objects-activity-execution-no", "value"),

          #### Triggers
          Input("events-activity-filter-button", "n_clicks"),
          Input("events-attribute-button", "n_clicks"),
          Input("event-selection-reset", "n_clicks"),
          Input("events-object_type-filter-button", "n_clicks"),
          Input("events-object-attribute-button", "n_clicks"),
          Input("events-objects-object-type-button", "n_clicks"),
          Input("events-objects-execution-button", "n_clicks"),
          Input("events-total-objects-button", "n_clicks"),
          Input("events-cp-active-filter-button", "n_clicks"),
          Input("events-it-active-filter-button", "n_clicks"),
          Input("events-ilvl-range-button", "n_clicks"),
          Input("events-time-period-button", "n_clicks"),
          Input("qel-collection-point-projection-button", "n_clicks"),
          Input("qel-item-type-projection-button", "n_clicks"),
          Input("object-type-filter-button", "n_clicks"),
          Input("objects-activity-execution-filter-button", "n_clicks"),
          Input("objects-activity-multi-execution-button", "n_clicks"),
          )
def create_selected_sublog(overview_json, ocel_json, qty_json,
                           selected_activities, selected_attribute_values, selected_attribute,
                           selected_object_types, selected_object_attribute, selected_object_attribute_values,
                           selected_object_type_object_type, selected_object_type_number,
                           selected_object_type_iteration, selected_iteration_number,
                           total_objects, active_selection,
                           cp_active_selection, cp_any_all,
                           it_active_selection, it_any_all,
                           selected_cp_item_balance, selected_it_item_balances, selected_ilvl_range,
                           selected_start_date, selected_end_date,
                           selected_collection_points_projection, selected_item_types_projection,
                           object_types_to_include,
                           object_selection_object_type, object_activity_execution_selection,
                           object_selection_multi_execution_activity, object_selection_iteration_no,
                           *args):

    if overview_json is None:
        return [None]*8
    else:
        pass

    ctx = dash.callback_context

    if not ctx.triggered:
        return ocel_json, qty_json, [None]*6
    else:
        button_id = ctx.triggered[0]['prop_id'].split('.')[0]

    #### only ocel data (completely qty independent) ######
    if button_id in {"raw-store", "event-selection-reset"}:
        ocel_new, qty_new = ds.reset_qel(overview_json=overview_json)
        return operations.sublog_returns(ocel_new, qty_new)
    else:
        pass

    if ocel_json is None:
        return None, qty_json, [None]*6
    else:
        pass

    filtered = True
    if button_id == "events-activity-filter-button":
        ocel_new = slc.filter_data_for_activity(ocel_json=ocel_json, selected_activities=selected_activities)
    elif button_id == "events-attribute-button":
        ocel_new = slc.filter_data_for_event_attribute(ocel_json=ocel_json, selected_attribute=selected_attribute,
                                                          selected_attribute_values=selected_attribute_values)
    elif button_id == "events-object_type-filter-button":
        ocel_new = slc.filter_data_for_events_with_object_type(ocel_json=ocel_json, selected_object_types=selected_object_types)
    elif button_id == "events-object-attribute-button":
        ocel_new = slc.filter_data_for_object_attribute_value(ocel_json=ocel_json, selected_attribute=selected_object_attribute,
                                                                 selected_attribute_values=selected_object_attribute_values)
    elif button_id == "events-objects-object-type-button":
        ocel_new = slc.filter_data_for_object_type_number(ocel_json=ocel_json, selected_object_type_object_type=selected_object_type_object_type,
                                                             selected_object_type_number=selected_object_type_number)
    elif button_id == "events-objects-execution-button":
        ocel_new = slc.filter_data_for_iteration(ocel_json=ocel_json, selected_object_type_iteration=selected_object_type_iteration,
                                                    selected_iteration_number=selected_iteration_number)
    elif button_id == "events-total-objects-button":
        ocel_new = slc.filter_data_for_total_object_counts(ocel_json=ocel_json, total_objects=total_objects)
    elif button_id == "events-time-period-button":
        ocel_new = slc.filter_data_for_time_period(ocel_json=ocel_json, selected_start_date=selected_start_date,
                                              selected_end_date=selected_end_date)
    elif button_id == "objects-activity-execution-filter-button":
        ocel_new = slc.filter_for_objects_with_activity_execution(ocel_json=ocel_json, object_selection_object_type=object_selection_object_type,
                                                                  object_activity_execution_selection=object_activity_execution_selection)
    elif button_id == "objects-activity-multi-execution-button":
        ocel_new = slc.filter_objects_with_specified_iterations_of_activity(ocel_json=ocel_json, object_type=object_selection_object_type,
                                                                               activity=object_selection_multi_execution_activity,
                                                                               restriction=object_selection_iteration_no)
    elif button_id == "object-type-filter-button":
        ocel_new = slc.filter_objects_of_object_types(ocel_json=ocel_json, object_types_to_include=object_types_to_include)
    else:
        filtered = None
        ocel_new = None


    if filtered:
        if qty_json is None:
            return operations.sublog_returns(ocel=ocel_new, qty=None)
        else:
            qop, ilvl, oqty = ds.get_qty_data(qty_json)
            qop_new = slc.create_qop_from_ocel(ocel_new=ocel_new, qop=qop)
            qty = ds.qop_ilvl_oqty_to_qty_dict(qop_new, ilvl, oqty)
            return operations.sublog_returns(ocel=ocel_new, qty=qty)
    else:
        if qty_json is None:
            raise ValueError("No filtering applied to ocel or reset triggered but also no quantity data available.")
        else:
            qop, ilvl, oqty = ds.get_qty_data(qty_json)

    if qop is None:
        raise ValueError("Dataframe of quantity operations is empty although ocel is non-empty.")
    else:
        pass

    filtered = True
    if button_id == "events-active-selection":
       qop_new = slc.filter_data_for_active_event_selection(qop=qop, active_selection=active_selection)
    elif button_id == "events-cp-active-filter-button":
        qop_new = slc.filter_data_for_cp_active_events(qop=qop, cp_active_selection=cp_active_selection,
                                                       cp_any_all=cp_any_all)
    elif button_id == "events-it-active-filter-button":
        qop_new = slc.filter_data_for_it_active_events(qop=qop, it_active_selection=it_active_selection, it_any_all=it_any_all)
    elif button_id == "events-ilvl-range-button":
        qop_new = slc.filter_data_for_events_in_ilvl(qop=qop, ilvl=ilvl,
                                                     selected_cp_item_balance=selected_cp_item_balance,
                                                     selected_it_item_balances=selected_it_item_balances,
                                                     selected_ilvl_range=selected_ilvl_range)
    else:
        filtered = False
        qop_new = None

    if filtered:
        ocel_new = slc.create_ocel_from_qop(qop_new, ocel_json)
        qty = ds.qop_ilvl_oqty_to_qty_dict(qop_new, ilvl, oqty)
        return operations.sublog_returns(ocel=ocel_new, qty=qty)
    else:
        pass

    if button_id == "qel-collection-point-projection-button":
        qop_new = slc.filter_data_for_selected_collection_points(qop=qop, selected_collection_points_projection=selected_collection_points_projection)
    elif button_id == "qel-item-type-projection-button":
        qop_new = slc.filter_data_for_selected_item_types(qop=qop, selected_item_types_projection=selected_item_types_projection)
    else:
        raise ValueError("No filtering applied to quantity operations.")

    qty = ds.qop_ilvl_oqty_to_qty_dict(qop_new, ilvl, oqty)
    events, e2o, objects = ds.get_ocel_data(ocel_json)
    ocel_new = ds.events_e2o_objects_to_ocel_dict(events, e2o, objects)
    return operations.sublog_returns(ocel=ocel_new, qty=qty)


##############################################################################
############################ QTY STATE OVERVIEW ##############################
##############################################################################

@callback(Output("qstate-processed", "data"),
          State("quantity-data", "data"),
          Input("raw-store", "data"),

          Input("ilvl-type", "value"),
          Input("ilvl-perspective", "value"),
          Input("ilvl-property", "value"),
          Input("ilvl-item-type-projection", "value"),
          Input("ilvl-collection-point-projection", "value"),
          Input("ilvl-cp-agg", "value"),
          Input("ilvl-it-agg", "value"),
          )
def get_relevant_ilvl_data(qty_json, overview_json,
                           ilvl_type, ilvl_perspective, ilvl_property,
                           item_type_projection, cp_projection,
                           cp_aggregation, it_aggregation,
                           *args):
    ctx = dash.callback_context

    if not ctx.triggered:
        return None
    else:
        button_id = ctx.triggered[0]['prop_id'].split('.')[0]

    if button_id == "raw-store":

        if overview_json is not None:
            pass
        else:
            return None

        events, objects, e2o, qop, ilvl, oqty = ds.get_raw_data_dataframes(overview_json=overview_json)

        if ilvl is None:
            return None
        else:
            return ds.store_single_dataframe(ilvl)
    else:

        if qty_json is not None:
            qop, ilvl, oqty = ds.get_qty_data(qty_json)
        else:
            return None

        return qstate.process_ilvl_data_according_to_selection(ilvl=ilvl, overview_json=overview_json,
                                                               ilvl_type=ilvl_type, ilvl_perspective=ilvl_perspective,
                                                               ilvl_property=ilvl_property,
                                                               cp_aggregation=cp_aggregation,
                                                               it_aggregation=it_aggregation,
                                                               item_types_projection=item_type_projection,
                                                               cps_projection=cp_projection
                                                               )

@callback(Output("qstate-dev-component", "children"),
          Input("qstate-processed", "data"),
          Input("quantity-data", "data"),
          State("ilvl-type", "value"),
          Input("ilvl-graph-display", "value"),
          Input("qstate-development-radio", "value")
          )
def update_quantity_state_development(processed_qstate_json, qty_json, ilvl_type, ilvl_display, display_type):
    if processed_qstate_json and qty_json:
        pass
    else:
        return None

    return operations.quantity_state_development_graph(processed_qstate_json=processed_qstate_json,
                                                              qty_json=qty_json,
                                                              ilvl_type=ilvl_type, ilvl_display=ilvl_display,
                                                              display_type=display_type)

@callback(Output("cp-stats", "data"),
          Output("cp-stats", "columns"),

          Input("qstate-processed", "data"),
          Input("quantity-data", "data"),
          Input("ilvl-graph-display", "value"),)
def cp_stats_data_table(processed_qstate_json, qty_json, ilvl_display):
    if processed_qstate_json and qty_json:
        pass
    else:
        return None, []

    return operations.create_cp_stats_quantity_state(processed_qstate_json=processed_qstate_json,
                                                     qty_json=qty_json,
                                                     ilvl_display=ilvl_display)


@callback(Output("qstate-execution-collection-point-dropdown", "options"),
          Input("qstate-processed", "data"),
          # Input("ilvl-collection-point-projection-button", "n_clicks")
          )
def quantity_state_execution_cp_filter_options(processed_qstate_json):
    if processed_qstate_json is not None:
        ilvl_data = ds.get_single_dataframe(processed_qstate_json)
        collection = ilvl_data[TERM_COLLECTION].unique()
        return list(collection)
    else:
        return []


@callback(Output("qstate-execution-item-type-dropdown", "options"),
          Input("qstate-processed", "data")
          )
def quantity_state_execution_it_filter_options(processed_qstate_json):
    if processed_qstate_json is not None:
        ilvl_data = ds.get_single_dataframe(processed_qstate_json)
        _, item_types = split_instance_and_variable_entries(ilvl_data.columns)
        return item_types
    else:
        return []

@callback(Output("qstate-execution-item-type-dropdown", "value"),
          Output("qstate-execution-collection-point-dropdown", "value"),
          Input("ocel", "data")
          )
def quantity_state_execution_it_filter_options(*args):
    return None, None

@callback(Output("qstate-execution", "data"),
          Input("qstate-processed", "data"),
          Input("quantity-data", "data"),
          Input("qstate-execution-activity-dropdown", "value"),
          Input("qstate-execution-collection-point-dropdown", "value"),
          Input("qstate-execution-item-type-dropdown", "value"),
          Input("qstate_display_item_type_active", "value"))
def update_quantity_state_execution_data(processed_qstate_json, qty_json, selected_activity, selected_cp,
                                   selected_it, it_active_selection):
    if processed_qstate_json and qty_json:
        return qstate.ilvl_data_for_execution(processed_qstate_json=processed_qstate_json,
                                                     qty_json=qty_json,
                                                     selected_activity=selected_activity,
                                                     selected_cp=selected_cp,
                                                     selected_it=selected_it,
                                                     it_active_selection=it_active_selection)
    else:
        return None

@callback(Output("ilvl-data-table", "data"),
          Output("ilvl-data-table", "columns"),
          Input("qstate-execution", "data"))
def creat_ilvl_data_table(execution_ilvl_json):
    if execution_ilvl_json:
        ilvl = ds.get_single_dataframe(execution_ilvl_json)
        return operations.create_data_table_elements(df=ilvl)
    else:
        return None, []


@callback(Output("ilvl-boxplots", "children"),
          Output("ilvl-stats", "data"),
          Output("ilvl-stats", "columns"),

          Input("qstate-execution", "data"),
          Input("ilvl-view", "value"))
def update_item_level_distribution(execution_ilvl_json, ilvl_view):
    if execution_ilvl_json:
        ilvl = ds.get_single_dataframe(execution_ilvl_json)
    else:
        return None, None, []

    return operations.update_item_level_distribution(ilvl=ilvl, ilvl_view=ilvl_view)

@callback(Output("ilvl-pre-post-component", "style"),
            Input("qstate-execution", "data"),
            Input("qstate-pre-post", "value"))
def show_pre_post_item_level_distribution(execution_ilvl_json, pre_post_selection):
    if execution_ilvl_json and pre_post_selection==PRE_EVENT_ILVL:
        return {"display": "block"}
    else:
        return {"display": "none"}

@callback(Output("ilvl-pre-post", "figure"),

          Input("qstate-execution", "data"),
          Input("quantity-data", "data"),
          Input("ilvl-type", "value"),
          Input("qstate-pre-post", "value"),)
def pre_post_event_quantity_state(execution_ilvl_json, qty_json, pre_post_selection, barchart):
    if execution_ilvl_json and qty_json and pre_post_selection==PRE_EVENT_ILVL:
        pass
    else:
        return plotly.graph_objs.Figure()

    ilvl = ds.get_single_dataframe(execution_ilvl_json)
    qop, orig_ilvl, oqty = ds.get_qty_data(qty_json)

    if barchart:
        return viz.quantity_state_pre_post_activity_execution_bar_chart(ilvl=ilvl, qop=qop)
    else:
        return viz.quantity_state_pre_post_activity_execution_boxplots(ilvl=ilvl, qop=qop)

@callback(Output("qstate-execution-bar-chart", "figure"),
          Input("qstate-execution", "data"),
          Input("qstate-execution-activity-dropdown", "value"),
          Input("qstate-execution-collection-point-dropdown", "value"),
          Input("qstate-execution-item-type-dropdown", "value"))
def update_qstate_execution_bar_chart(execution_ilvl_json, selected_activity, selected_cp,
                                   selected_it):

    if execution_ilvl_json:
        pass
    else:
        return plotly.graph_objs.Figure()

    if selected_activity is not None or selected_cp is not None or selected_it is not None:
        pass
    else:
        return plotly.graph_objs.Figure()

    ilvl = ds.get_single_dataframe(execution_ilvl_json)

    fig_bar_chart = viz.quantity_state_activity_execution_bar_chart(ilvl=ilvl)

    return fig_bar_chart

@callback(Output("qstate-execution-hist", "figure"),
          Input("qstate-execution", "data"),
          Input("qstate-execution-collection-point-dropdown", "value"),)
def update_qstate_execution_bar_chart(execution_ilvl_json, selected_cp):

    if execution_ilvl_json:
        pass
    else:
        return plotly.graph_objs.Figure()

    if selected_cp is not None:
        pass
    else:
        return plotly.graph_objs.Figure()

    ilvl = ds.get_single_dataframe(execution_ilvl_json)

    fig_bar_chart = viz.quantity_state_activity_execution_histogram(ilvl=ilvl)

    return fig_bar_chart

##############################################################################
############################ QTY STATE OVERVIEW ##############################
##############################################################################

@callback(Output("qop-processed", "data"),

          Input("quantity-data", "data"),
          Input("qop-type", "value"),
          Input("qop-property", "value"),
          Input("qop-active", "value"),
          Input("qop-it-agg", "value"),
          Input("qop-cp-agg", "value"),
          Input("qop-item-type-projection", "value"),
          Input("qop-collection-point-projection", "value"),
          )
def filter_quantity_data(qty_json, qop_type, qop_property, qop_active,
                         qop_it_agg, qop_cp_agg,
                         selected_item_types, selected_collection_points):

    if qty_json is not None:
        qop, ilvl, oqty = ds.get_qty_data(qty_json)
        if qop is None:
            pass
        else:
            return qopo.process_quantity_operations(qop=qop, qop_type=qop_type, qop_property=qop_property,
                                                qop_active=qop_active, qop_it_agg=qop_it_agg, qop_cp_agg=qop_cp_agg,
                                                selected_item_types=selected_item_types,
                                                selected_collection_points=selected_collection_points)
    else:
        pass

    return None

@callback(Output("qop-data-table", "data"),
          Output("qop-data-table", "columns"),
          Input("qop-processed", "data"))
def creat_ilvl_data_table(processed_qop_json):
    if processed_qop_json:
        qop = ds.get_single_dataframe(processed_qop_json)
        return operations.create_data_table_elements(df=qop)
    else:
        return None, []

@callback(Output("activity-impact-graph", "figure"),
          Input("qop-processed", "data"),
          Input("activity-impact-radio", "value"))
def activity_impact_overview_graph(processed_qop_json, impact_type):
    if processed_qop_json:
        qop = ds.get_single_dataframe(processed_qop_json)
        return viz.activity_cp_item_type_impact(qop=qop, number_quantity_operations=impact_type)
    else:
        return plotly.graph_objects.Figure()

@callback(Output("qop-cp-dropdown", "options"),
          Input("qop-collection-point-projection", "value"))
def qop_collection_point_options(cps):
    if cps:
        return cps
    else:
        return []

@callback(Output("qop-activity-qup-item-types-dropdown", "options"),
          # Output("qop-activity-qup-item-types-dropdown", "value"),
          Input("qop-item-type-projection", "value"))
def qop_item_types_options(item_types):
    if item_types:
        return item_types #, item_types[0]
    else:
        return [] #, None

@callback(Output("active-instances-cp-graph", "figure"),
          Input("qop-processed", "data"))
def qop_active_instances_graph(processed_qop_json):
    if processed_qop_json:
        qop = ds.get_single_dataframe(processed_qop_json)
        return viz.show_active_qops(qop)
    else:
        return plotly.graph_objects.Figure()

@callback(Output("direction-changes-graph", "figure"),
          Input("qop-processed", "data"))
def directions_qop_graph(processed_qop_json):
    if processed_qop_json:
        qop = ds.get_single_dataframe(processed_qop_json)
        return viz.show_instance_directions(qop)
    else:
        return plotly.graph_objects.Figure()

@callback(Output("qty-relation", "data"),
            Input("qop-processed", "data"),
            Input("qop-cp-dropdown", "value"),
            Input("qop-activity-dropdown", "value"))
def data_qops_activity_cp_quantity_relation(processed_qop_json, cp, activity):
    if processed_qop_json:
        qop = ds.get_single_dataframe(processed_qop_json)
        return qopo.data_quantity_relation(qop=qop, cp=cp, activity=activity)
    else:
        return None

@callback(Output("qop-it-active-distribution-graph", "figure"),
          Input("qty-relation", "data"))
def directions_qop_graph(qty_relation_json):
    if qty_relation_json:
        qty_relation = ds.get_single_dataframe(qty_relation_json)
        return viz.show_active_item_type_distribution_per_qop(qop=qty_relation)
    else:
        return plotly.graph_objects.Figure()

@callback(Output("qop-it-active-combination-graph", "figure"),
          Input("qty-relation", "data"))
def directions_qop_graph(qty_relation_json):
    if qty_relation_json:
        qty_relation = ds.get_single_dataframe(qty_relation_json)
        return viz.show_active_item_type_combinations_and_frequencies_qop(qty_relation)
    else:
        return plotly.graph_objects.Figure()

@callback(Output("qop-mean-additions-removals-graph", "figure"),
          Input("qty-relation", "data"),
          Input("qop-average-qup-time-unit", "value"))
def create_qop_cp_graph(qty_relation_json, unit):
    if qty_relation_json and unit:
        qty_relation = ds.get_single_dataframe(qty_relation_json)
        return viz.average_adding_removing_quantity_updates_per_time_unit(qop=qty_relation, time_unit=unit)
    else:
        return plotly.graph_objects.Figure()

@callback(Output("qop-time-period", "min_date_allowed"),
          Output("qop-time-period", "max_date_allowed"),
          Input("qty-relation", "data"))
def possible_selection_period_event_filter(qty_relation_json):
    if qty_relation_json:
        qty_relation = ds.get_single_dataframe(qty_relation_json)
        return operations.possible_selection_period_qop_filter(qty_relation)
    else:
        return None, None #, None, None, 0

@callback(Output("quantity-operation-overview-graph", "figure"),
          State("qty-relation", "data"),
          State("qop-time-period", "start_date"),
          State("qop-time-period", "end_date"),
          Input("qop-time-period-button", "n_clicks"))
def display_qops_over_time(qty_relation_json, start_date, end_date, *args):
    if qty_relation_json:
        qty_relation = ds.get_single_dataframe(qty_relation_json)
        return viz.plot_quantity_data_over_time(qop=qty_relation, start_time=start_date, end_time=end_date)
    else:
        return plotly.graph_objects.Figure()


@callback(Output("qop-boxplots-item-types", "figure"),
          Output("qop-stats-item-types", "data"),
          Output("qop-stats-item-types", "columns"),

          Input("qty-relation", "data"),
          Input("qop-active", "value"),
          Input("qop-boxplots-item-types-points", "value"))
def update_quantity_data_distribution(qty_relation_json, qop_active, display_points):
    if qty_relation_json:
        qty_relation = ds.get_single_dataframe(qty_relation_json)
        return operations.quantity_update_distribution(qty_relation=qty_relation, qop_active=qop_active,
                                                              qop_view=TERM_ITEM_TYPES, display_points=display_points)
    else:
        return plotly.graph_objects.Figure(), None, []


@callback(Output("qop-boxplots-freq-item-types", "figure"),
          Input("qty-relation", "data"))
def update_quantity_data_distribution(qty_relation_json):
    if qty_relation_json:
        qty_relation = ds.get_single_dataframe(qty_relation_json)
        return viz.time_between_it_active_qups_distribution(qop=qty_relation, view=TERM_ITEM_TYPES)
    else:
        return plotly.graph_objects.Figure()

@callback(Output("qop-mean-frequency-qup-type-graph", "figure"),
          Input("qty-relation", "data"))
def qop_mean_frequency_graph(qty_relation_json):
    if qty_relation_json:
        qty_relation = ds.get_single_dataframe(qty_relation_json)
        return viz.average_time_between_typed_qups_per_item_type(qop=qty_relation)
    else:
        return plotly.graph_objects.Figure()

@callback(Output("single-qup-executions-graph", "figure"),
          Input("qty-relation", "data"),
          Input("qop-activity-qup-item-types-dropdown", "value"))
def single_qups_item_type_figure(qty_relation_json, item_type):
    if qty_relation_json and item_type:
        qty_relation = ds.get_single_dataframe(qty_relation_json)
        return viz.qups_for_item_type(qop=qty_relation, item_type=item_type)
    else:
        return plotly.graph_objects.Figure()

@callback(Output("single-qup-freq-graph", "figure"),
          Input("qty-relation", "data"),
          Input("qop-activity-qup-item-types-dropdown", "value"))
def timedelta_single_qups_item_type_figure(qty_relation_json, item_type):
    if qty_relation_json and item_type:
        qty_relation = ds.get_single_dataframe(qty_relation_json)
        return viz.time_between_qups_item_type(qop=qty_relation, item_type=item_type)
    else:
        return plotly.graph_objects.Figure()

@callback(Output("qop-activity-qup-boxplots", "figure"),
          Input("qty-relation", "data"),
          Input("qop-activity-qup-item-types-dropdown", "value"),
          Input("qup-view", "value"))
def distribution_single_qups_item_type_figure(qty_relation_json, item_type, qup_view):
    if qty_relation_json and item_type:
        qty_relation = ds.get_single_dataframe(qty_relation_json)
        return operations.plot_qup_distribution(qty_relation=qty_relation, item_type=item_type, view=qup_view)
    else:
        return plotly.graph_objects.Figure()

@callback(Output("qup-freq-boxplots", "figure"),
          Input("qty-relation", "data"),
          Input("qop-activity-qup-item-types-dropdown", "value"),
          Input("qup-freq-view", "value"))
def distribution_single_qups_item_type_figure(qty_relation_json, item_type, qup_view):
    if qty_relation_json and item_type:
        qty_relation = ds.get_single_dataframe(qty_relation_json)
        return viz.time_between_it_active_qups_distribution(qop=qty_relation, item_type=item_type, view=qup_view)
    else:
        return plotly.graph_objects.Figure()


# @callback(Output("qop-activity-qup-graph", "figure"),
#           Input("qty-relation", "data"),
#           Input("qop-activity-qup-item-types-dropdown", "value"))
# def create_qop_cp_graph(qop_analysis_json, item_type):
#     if qop_analysis_json and item_type:
#         qop = operations.get_qop_analysis_data(qop_analysis_json)
#         return viz.collection_point_interaction_overview(qop=qop, item_type=item_type)
#     else:
#         return plotly.graph_objects.Figure()


if __name__ == '__main__':
    app.run_server(debug=True) #debug=True
    # dev_tools_hot_reload=False
