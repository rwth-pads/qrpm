import dash_interactive_graphviz
from dash import html, dcc, dash_table

from qrpm.GLOBAL import CHART_COLOURS, TERM_ALL, \
    TERM_ACTIVE, PRE_EVENT_ILVL, POST_EVENT_ILVL, TERM_COLLECTION, TERM_ITEM_TYPES, \
    TERM_ACTIVITY, TERM_ITEM_LEVELS, TERM_ITEM_ASSOCIATION, ILVL_AVAILABLE, ILVL_REQUIRED, TERM_INACTIVE, TERM_SUBLOG, \
    TERM_ITEM_TYPE_ACTIVE, TERM_QUANTITY_CHANGES, TERM_ITEM_MOVEMENTS, TERM_ADDING, TERM_REMOVING, TERM_ACTIVE_OPERATIONS, TERM_ACTIVE_UPDATES, TERM_MONTHLY, TERM_DAILY, TERM_EVENT, TERM_ANY


def create_boxplot_graph(id: str):
    div = html.Div(style={"display": "block", "margin": "5px", "padding": "5px", "border": "1px #bbb solid"}, children=[
        dcc.Loading(type="circle", color='#0098A1',
                    target_components={id: "figure"}, children=[
            dcc.Graph(id=id)
        ])
    ])
    return div

def create_data_table(id: str):

    return dash_table.DataTable(id=id, filter_action="native", sort_action="native", page_action="native",
                         page_current=0, page_size=10, style_table={"marginTop": "2px", "margin": "5px"},
                             style_header={"backgroundColor": "#bbb"},
                                export_format='xlsx',
                                export_headers='display',
                                merge_duplicate_headers=True
                             )

def create_simple_data_table(id: str):
    div = html.Div(style={"display": "block", "margin": "5px", "padding": "5px"}, children=[
        dash_table.DataTable(id=id, style_table={"marginTop": "2px"},
                             style_header={"backgroundColor": "#bbb"},
                             style_data_conditional=[{
                                 'if': {'column_id': "index"},
                                 'backgroundColor': '#bbb',
                                 "width": "50px"
                             }])
       ])
    return div

def create_data_overview_component(component_name: str):
    DataOverviewComponent = html.Div(id=f"{component_name}-data-overview", children=[
        create_simple_data_table(f"{component_name}-data-stats"),
        html.Details([html.Summary("View Data"),
                      create_data_table(f"{component_name}-data-view")]),
        create_boxplot_graph(f"{component_name}-boxplots")
    ])
    return DataOverviewComponent

UploadComponent = html.Div(style={'display': 'flex', 'flexDirection': 'row'}, children=[
    html.Div(style={'width': '90%', "height": "2.5cm"}, children=[
        dcc.Upload(id='upload-data', accept=".sqlite", children=[
            html.Button(id='file_selection')
        ]),
    ]),
    html.Div(style={'display': 'flex', 'flexDirection': 'column'}, children=[
        html.Button('Demo Data', id='demo-data', n_clicks=0, style={'color': 'white',
                                                                    "background": CHART_COLOURS[1],
                                                                    "height": "1.1cm",
                                                                    "fontSize": 19,
                                                                    "borderColor": "#CE108A",
                                                                    'textAlign': 'center',
                                                                    'marginBottom': '1mm'}),
        html.Button('Submit', id='submit-button', n_clicks=0, style={'color': 'white',
                                                                     "background": CHART_COLOURS[2],
                                                                     "height": "1.34cm",
                                                                     "fontSize": 19,
                                                                     "borderColor": '#0098A1',
                                                                     'textAlign': 'center'}),
        ]),
    ])

def create_text_list(list_of_text: list):
    return [html.Li(text) for text in list_of_text]

target_components_qel_overview = {
    "qel-no-events": "children",
    "qel-no-activities": "children",
    "qel-no-objects": "children",
    "qel-no-object-types": "children",
    "qel-no-item-types": "children",
    "qel-no-collections": "children",
    "qel-no-quantity-relations": "children",
}

LogOverviewComponent = html.Div(id="qel-overview", children=[
            dcc.Loading(id="loading-qel", type="circle", color='#0098A1', target_components=target_components_qel_overview, children=[
                html.Div(id="log-overview-details", style={"display": "flex", "flexDirection": "row"}, children=[
                    html.Table(style={"marginRight": "5px", "width": "33.3%"}, children=[
                        html.Tr([html.Td("Number of Events: "),
                                 html.Td(id="qel-no-events")]),
                        html.Tr([html.Td("Activities: "),
                                 html.Td(html.Details([
                                     html.Summary(id="qel-no-activities"),
                                     html.Ul(id="qel-activities")
                                    ]))
                                 ]),
                        html.Tr([html.Td("Number of Objects: "),
                                 html.Td(id="qel-no-objects")]),
                        html.Tr([html.Td("Object Types: "),
                                 html.Td(html.Details([
                                     html.Summary(id="qel-no-object-types"),
                                     html.Ul(id="qel-object-types")
                                    ]))
                                 ]),
                    ]),
                    html.Table(style={"marginLeft": "5px", "marginRight": "5px", "width": "33.3%"}, children=[
                        html.Tr([html.Td("Q-active Events: "),
                                 html.Td(id="qel-no-q-events")]),
                        html.Tr([html.Td("Q-Activities: "),
                                 html.Td(html.Details([
                                     html.Summary(id="qel-no-q-activities"),
                                     html.Ul(id="qel-q-activities")
                                    ]))
                                 ]),
                        html.Tr([html.Td("Q-active Objects: "),
                                 html.Td(id="qel-no-q-objects")]),
                        html.Tr([html.Td("Q-Object Types: "),
                                 html.Td(html.Details([
                                     html.Summary(id="qel-no-q-object-types"),
                                     html.Ul(id="qel-q-object-types")
                                 ]))
                            ])
                        ]),
                    html.Table(style={"marginLeft": "5px", "width": "33.3%"}, children=[
                        html.Tr(children=[html.Td("Item types: "),
                                 html.Td(html.Details([
                                     html.Summary(id="qel-no-item-types"),
                                     html.Ul(id="qel-item-types")
                                    ]))
                                 ]),
                        html.Tr([html.Td("Item Collections: "),
                                 html.Td(html.Details([
                                     html.Summary(id="qel-no-collections"),
                                     html.Ul(id="qel-collections")
                                 ]))
                                 ]),
                        html.Tr([html.Td("Active Qop: "),
                                 html.Td(id="qel-no-qops")]),
                        html.Tr([html.Td("Quantity Relations: "),
                                 html.Td(html.Details([
                                     html.Summary(id="qel-no-quantity-relations"),
                                     html.Ul(id="qel-quantity-relations"),
                                    ]))
                                 ])
                    ])
                ])
                # html.Div(style={"display": "flex", "flexDirection": "column"}, children=[
                #     html.Button("Filter Log", id="qel-filter",
                #                 style={"background": var.COLOURS[0], "color": "white", "fontSize": 14, "margin": "5px", "display": "flex"}),
                #     html.Button("Rediscover", id="qnet-rediscover",
                #                                     style={"background": var.COLOURS[0], "color": "white", "fontSize": 14, "display": "flex", "margin": "5px"})
                #     ])
            ])
    ])

SelectionType = html.Div(id="element-type", style={"display": "inline"})
SelectionName = html.Div(id="element-name", style={"display": "inline"})

SelectionNumberEvents = html.Div(id="selection-no-events",style={"display": "inline"})
SelectionNumberQuantityEvents = html.Div(id="selection-no-qty-events", style={"display": "inline"})
SelectionNumberActivities = html.Div(id="selection-no-activities", style={"display": "inline"})
SelectionNumberQuantityActivities = html.Div(id="selection-no-qactivities", style={"display": "inline"})
SelectionNumberObjects = html.Div(id="selection-no-objects", style={"display": "inline"})
SelectionNumberQuantityObjects = html.Div(id="selection-no-qobjects", style={"display": "inline"})
SelectionNumberQuantityObjectTypes = html.Div(id="selection-no-qobject-types", style={"display": "inline"})
SelectionNumberObjectTypes = html.Div(id="selection-no-object-types", style={"display": "inline"})
SelectionNumberQuantityOperations = html.Div(id="selection-no-qops", style={"display": "inline"})
SelectionNumberActiveQuantityOperations = html.Div(id="selection-no-active-qops", style={"display": "inline"})
SelectionNumberCollections = html.Div(id="selection-no-collections", style={"display": "inline"})
SelectionNumberItemTypes = html.Div(id="selection-no-item-types", style={"display": "inline"})

def create_drawer_filter(text:str, id: str):
    DrawerSelection = html.Div(style={"display": "block", "margin": "10px"}, children=[
        html.Div(text, style={"display": "inline"}),
        html.Div(style={"display": "flex", "flexDirection": "row"}, children=[
            dcc.Dropdown(id=id, multi=True, clearable=True, style={"margin": "10px", "width": "95%"}),
            html.Button(id=f"{id}-button", children=["Filter"], style={"display": "inline", "background": CHART_COLOURS[2], "color": "white", "fontSize": 14, "margin": "5px"}),
        ])
        # dcc.Dropdown(id=id, multi=True, clearable=True, style={"display": "inline", "margin": "10px"}),
        # html.Button(id=f"{id}-button", children=["Filter"],
        #             style={"display": "inline", "background": CHART_COLOURS[2], "color": "white", "fontSize": 14,
        #                    "margin": "5px"}),

    ])
    return DrawerSelection

def display_ratio(nominator_element, denominator_element):
    return html.Div([nominator_element, html.Div("/", style={"display": "inline"}), denominator_element], style={"display": "inline"})

SelectionOverview = html.Div(id="selection-overview", style={"align": "center"}, children=[
    html.Table(children=[
        html.Tr([html.Td("Q-Events: "),
                html.Td(display_ratio(SelectionNumberQuantityEvents, SelectionNumberEvents))
                 ]),
        html.Tr([html.Td("Q-Activities: "),
                html.Td(html.Details([
                    html.Summary(display_ratio(SelectionNumberQuantityActivities, SelectionNumberActivities)),
                    html.Ul(id="selection-q-activities")
                    ]))
                 ]),
        html.Tr([html.Td("Q-Objects: "),
                 html.Td(display_ratio(SelectionNumberQuantityObjects, SelectionNumberObjects))
                 ]),
        html.Tr([html.Td("Q-Object Types: "),
                html.Td(html.Details([
                    html.Summary(display_ratio(SelectionNumberQuantityObjectTypes, SelectionNumberObjectTypes)),
                    html.Ul(id="selection-q-object-types")
                    ]))
                ]),
        html.Tr([html.Td("Collections: "),
                html.Td(html.Details([
                    html.Summary(SelectionNumberCollections),
                    html.Ul(id="selection-collections")
                    ])),
                 ]),
        html.Tr([html.Td("Active Q-Operations: "),
                 html.Td(display_ratio(SelectionNumberActiveQuantityOperations, SelectionNumberQuantityOperations))
                 ]),
        html.Tr([html.Td("Item Types: "),
                html.Td(html.Details([
                    html.Summary(SelectionNumberItemTypes),
                    html.Ul(id="selection-q-item-types")
                    ]))
                ])
        ])
])


SelectionComponent = html.Div(id="selection-info", style={"display": "block", "marginTop": "25px"}, children=[
        html.H5([SelectionType, html.Div(": ", style={"display": "inline"}), SelectionName], style={"display": "inline"}),
    SelectionOverview,
    # html.Button("Reset Selection", id="reset-selection-qnet", style={"background": CHART_COLOURS[1], "color": "white", "fontSize": 14, "margin": "5px"}),
    ])

QnetDisplay = html.Div(style=dict(width="80%"), children=[
        dcc.Loading(id="loading", style={"display": "block"}, type="circle", color='#0098A1',
                    target_components={"qnet": "dot_source"}, children=[
            html.Div(dash_interactive_graphviz.DashInteractiveGraphviz(id="qnet",
                                                                           persistence=True,
                                                                           fit_button_content=" Autofit Net ",
                                                                           fit_button_style={"background": "white",
                                                                                             "fontsize": 18,
                                                                                             "border": "1px #bbb solid",
                                                                                             "color": "#bbb",
                                                                                             "padding": "3px"}),
                         style=dict(border="1px #bbb solid", height="55vh", align="center", verticalAlign="middle",
                                    margin="10px")),
            ]),
    ])

QnetComponent = html.Div(style={"display": "block"}, id="qnet-container", children=[
    html.Div(style={"display": "flex", "flexDirection": "row", "margin": "5px"}, children=[
        html.Div(style={"width": "90%", "margin": "5px"}, children=[
            html.H3("Quantity Net"),
            html.Div("Select activity (transition), object type (place) or collection (decoupling point) for further information."),
        ]),
        html.Div(style={"width": "10%"}, children=[
            html.Button("Export", id="export-qnet-button", style={"background": CHART_COLOURS[0], "color": "white", "fontSize": 14, "margin": "5px"}),
            dcc.Download(id="qnet-export-file"),
        ])
    ]),
    html.Div(style={"display": "flex", "flexDirection": "row", "marginTop": "10px"}, children=[
        html.Div(style={"display": "block", "width": "20%", "marginTop": "10px"}, children=[
            # html.Div(style={"display": "flex", "flexDirection": "row", "marginTop": "10px"}, children=[
                html.Button("Rediscover", id="rediscover-qnet", style={"background": CHART_COLOURS[2], "color": "white", "fontSize": 14, "margin": "5px", "display": "inline"}),
                html.Div("with filtered Sublog", style={"fontSize": 12, "margin": "5px", "display": "inline"}),
            # ]),
            SelectionComponent,
        ]),
        QnetDisplay
    ])
])

ProcessOverview = html.Div(id="process-overview", children=[
    html.H2("Process & Log Overview"),
    html.Div("Here you find some general information on the process described by the event log."),
    LogOverviewComponent,
    html.Div(style={"border": "1px #bbb solid", "marginTop": "10px"}, children=[
        QnetComponent,
    ])
])



ObjectTypeSelection = html.Div(children=[
    html.Div(style={"display": "flex", "flexDirection": "row", "margin": "5px"}, children=[
        html.Div(style={"width": "25%", "display": "block"}, children=[
            html.Div(["Object Selection"], style={"fontSize": 25, "margin": "5px"}),
            html.Div(["Select object types the sublog for your analysis should include. Events no longer referring to an object will be removed."], style={"fontSize": 14, "margin": "5px"}),
        ]),
        html.Div(style={"width": "75%", "margin": "5px"}, children=[
            dcc.Loading(id="loading_object-type-graph-graph", style={"display": "block"}, type="circle", color='#0098A1',
                                    target_components={"events-activity-graph": "figure"}, children=[
                                dcc.Graph(id="object-type-graph")
                            ]),
            create_drawer_filter("Select object types your analysis should include: ", "object-type-filter")
        ]),
    ]),
    html.Div(style={"margin": "5px", "border": "1px #bbb solid"}, children=[
        html.H4("Object Type Subset"),
        html.Div("Only consider events referring to a subset of objects of type: ", style={"fontSize": 14, "margin": "5px"}),
        dcc.Dropdown(id="object-type-dropdown", placeholder="object type", clearable=False, style={"margin": "5px"}),
        html.Div(style={"display": "flex", "flexDirection": "row", "margin": "5px"}, children=[
            html.Div(style={"width": "50%", "align": "center", "textAlign": "center"},
                     hidden=False, children=[
                    html.H5([
                        html.Div("Activity Execution", style={"display": "inline"})
                    ]),
                    dcc.Loading(id="loading_objects-activity-execution-graph", style={"display": "block"}, type="circle", color='#0098A1',
                                target_components={"objects-activity-execution-graph": "figure"}, children=[
                            dcc.Graph(id="objects-activity-execution-graph")
                        ]),
                    create_drawer_filter("Only include events referring to objects of selected type executing one of the following activities at least once: ", "objects-activity-execution-filter")
                ]),
            html.Div(style={"width": "50%", "align": "center", "textAlign": "center"},
                     hidden=False, children=[
                    html.H5(children=[
                        html.Div("Multiple Activity Executions", style={"display": "inline"}),
                    ]),
                    dcc.Loading(id="loading_objects-multi-execution-activity-graph", style={"display": "block"}, type="circle", color='#0098A1',
                                target_components={"objects-multi-execution-activity-graph": "figure"}, children=[
                            dcc.Graph(id="objects-multi-execution-activity-graph")
                        ]),
                    html.Div("Only include events referring to objects of selected type executing the following activity at least xx times: "),
                    dcc.Dropdown(id="objects-activity-iteration-filter", placeholder="activity", clearable=True, style={"margin": "5px"}),
                    dcc.Input(id="objects-activity-execution-no", type="number", placeholder="# executions (int)", style={"display": "inline", "margin": "5px"}),
                    html.Button(id="objects-activity-multi-execution-button", children=["Filter"], style={"display": "inline", "background": CHART_COLOURS[2], "color": "white", "fontSize": 14, "margin": "5px"})
                ])
        ])
    ])
])

EventSelection = html.Div(id="event-selection", children=[
    html.Details(style={"border": "1px #bbb solid", "margin": "5px"}, children=[
        html.Summary(
            style={"verticalAlign": "middle", "display": "flex", "flexDirection": "row"},
            children=[
                html.Div(style={"width": "25%"}, children=[
                    html.H4("Event & Object Selection", style={"verticalAlign": "middle",
                                                         "display": "inline", "margin": "5px"
                                                         }),
                    html.Div("Click here to get overview of currently selected events and change filter values to include fewer events."),
                ]),
                html.Div(style={"width": "75%", "alignText": "middle"}, children=[
                    html.Div(children=[
                        html.Div("Active Events in (Sub)log: ", style={"margin": "5px", "fontsize": 16, "display": "inline"}),
                        html.Div(id="qevents_sublog", style={"margin": "5px", "fontsize": 16, "display": "inline"}),
                        html.Div(" / ", style={"margin": "5px", "fontsize": 16, "display": "inline"}),
                        html.Div(id="events_sublog", style={"margin": "5px", "fontsize": 16, "display": "inline"}),
                    ]),
                    html.Div(children=[
                        html.Div("Active Objects in (Sub)log: ", style={"margin": "5px", "fontsize": 16, "display": "inline"}),
                        html.Div(id="qobjects_sublog", style={"margin": "5px", "fontsize": 16, "display": "inline"}),
                        html.Div(" / ", style={"margin": "5px", "fontsize": 16, "display": "inline"}),
                        html.Div(id="objects_sublog", style={"margin": "5px", "fontsize": 16, "display": "inline"}),
                    ]),
                    html.Div(children=[
                        html.Div("Included Quantity Updates: ", style={"margin": "5px", "fontsize": 16, "display": "inline"}),
                        html.Div(id="qups_sublog", style={"margin": "5px", "fontsize": 16, "display": "inline"}),
                        html.Div(" in ", style={"margin": "5px", "fontsize": 16, "display": "inline"}),
                        html.Div(id="qops_sublog", style={"margin": "5px", "fontsize": 16, "display": "inline"}),
                        html.Div(" quantity operations", style={"margin": "5px", "fontsize": 16, "display": "inline"}),
                    ])
                ])
            ]),
            html.Div(style={"display": "flex", "flexDirection": "row", "margin": "5px"}, children=[
                        html.Div("Reduce considered time period in log.", style={"margin": "5px", "fontsize": 14}),
                        dcc.DatePickerRange(id="events-time-period", clearable=True, style={"margin": "5px"},
                                            month_format='MMMM Y', display_format='D-M-Y', first_day_of_week = 1,
                                            start_date_placeholder_text="First Date",
                                            end_date_placeholder_text="Last Date"),
                        html.Button(id="events-time-period-button", children=["Filter"],
                                        style={"display": "inline", "background": CHART_COLOURS[2], "color": "white",
                                               "fontSize": 14, "margin": "5px"})
            ]),
        html.Div(style={"display": "flex", "flexDirection": "row", "margin": "5px"}, children=[
            html.Div(style={"width": "50%", "border": "1px #bbb solid", "align": "center", "textAlign": "center"},
                     hidden=False, children=[
                    html.H4([
                        html.Div("Activities ", style={"display": "inline"}),
                        html.Div(id="events-activity-filter-number", style={"display": "inline"})
                    ]),
                    dcc.Loading(id="loading_events-activity-graph", style={"display": "block"}, type="circle", color='#0098A1',
                                target_components={"events-activity-graph": "figure"}, children=[
                            dcc.Graph(id="events-activity-graph")
                        ]),
                    create_drawer_filter("Only consider events of the following activities: ", "events-activity-filter")
                ]),
            html.Div(style={"width": "50%", "border": "1px #bbb solid", "align": "center", "textAlign": "center"},
                     hidden=False, children=[
                    html.H4(children=[
                        html.Div("Event Attributes", style={"display": "inline"}),
                    ]),
                    html.Div(style={"display": "flex", "flexDirection": "row", "align": "center", "textAlign": "center"}, children=[
                        html.Div("Select event attribute: ", style={"margin": "10px"}),
                        dcc.Dropdown(id="events-attribute-attribute-dropdown", placeholder="attribute", style={"margin": "5px", "width": "50%"}),
                    ]),
                    dcc.Loading(id="loading_events-attribute-graph", style={"display": "block"}, type="circle", color='#0098A1',
                                target_components={"events-attribute-graph": "figure"}, children=[
                            dcc.Graph(id="events-attribute-graph")
                        ]),
                    html.Div("Only include events with the following event attribute values: "),
                    dcc.Dropdown(id="events-attribute-value-dropdown", placeholder="attribute values", multi=True, clearable=True, style={"margin": "5px"}),
                    html.Button(id="events-attribute-button", children=["Filter"], style={"display": "inline", "background": CHART_COLOURS[2], "color": "white", "fontSize": 14, "margin": "5px"})
                ]),
        ]),
        html.Div(style={"display": "flex", "flexDirection": "row","margin": "5px"}, children=[
            html.Div(style={"width": "50%", "border": "1px #bbb solid", "align": "center", "textAlign": "center"},
                     hidden=False, children=[
                    html.H4([
                        html.Div("Objects of Object Types involved in all selected Events", style={"display": "inline"}),
                        html.Div(id="events-object_type-filter-number", style={"display": "inline"})
                    ]),
                    dcc.Loading(id="loading_events-object-type-graph", style={"display": "block"}, type="circle", color='#0098A1',
                                target_components={"events-object-type-graph": "figure"}, children=[
                            dcc.Graph(id="events-object-type-graph")
                        ]),
                    create_drawer_filter("Only include events with all of the following object types: ",
                                         "events-object_type-filter")
                ]),
            html.Div(style={"width": "50%", "border": "1px #bbb solid", "align": "center", "textAlign": "center"},
                     hidden=False, children=[
                    html.H4("Events with Object Attributes", style={"display": "inline"}),
                    html.Div(style={"display": "flex", "flexDirection": "row", "align": "center", "textAlign": "center"}, children=[
                        html.Div("Select object attribute: ", style={"margin": "5px"}),
                        dcc.Dropdown(id="events-object-attribute-dropdown", placeholder="attribute", style={"margin": "5px", "width": "50%"}),
                    ]),
                    dcc.Loading(id="loading_events-object-attribute", style={"display": "block"}, type="circle",
                                color='#0098A1',
                                target_components={"events-object-attribute-graph": "figure"}, children=[
                            dcc.Graph(id="events-object-attribute-graph")
                        ]),
                    html.Div("Only include events associated with objects with the following objects attribute values:"),
                    dcc.Dropdown(id="events-object-attribute-value-dropdown", placeholder="attribute value", multi=True, clearable=True, style={"margin": "5px"}),
                    html.Button(id="events-object-attribute-button", children=["Filter"],
                                style={"display": "inline", "background": CHART_COLOURS[2], "color": "white",
                                       "fontSize": 14, "margin": "5px"})
                ])
        ]),
        html.Div(style={"display": "flex", "flexDirection": "row", "margin": "5px"}, children=[
            html.Div(style={"width": "50%", "border": "1px #bbb solid", "align": "center", "textAlign": "center"},
                     hidden=False, children=[
                    html.H4([
                        html.Div("Number of Objects per Object Type involved in Events", style={"display": "inline"}),
                    ]),
                    dcc.Loading(id="loading_events-objects-object-type-graph", style={"display": "block"}, type="circle", color='#0098A1',
                                target_components={"events-objects-object-type-graph": "figure"}, children=[
                            dcc.Graph(id="events-objects-object-type-graph")
                        ]),
                    html.Div("Only include events with the following number of objects of object type: "),
                    html.Div(style={"flexDirection": "row", "align": "center"}, children=[
                        dcc.Dropdown(id="events-objects-object-type-dropdown", placeholder="object type", clearable=True, style={"margin": "5px"}),
                        dcc.Input(id="events-objects-object-type-int", type="number", placeholder="no. objects (int)", style={"display": "inline", "margin": "5px"}),
                        html.Button(id=f"events-objects-object-type-button", children=["Filter"], style={"display": "inline", "background": CHART_COLOURS[2], "color": "white", "fontSize": 14, "margin": "5px"}),
                    ])
                ]),
            html.Div(style={"width": "50%", "border": "1px #bbb solid", "align": "center", "textAlign": "center"},
                     hidden=False, children=[
                    html.H4(children=[
                        html.Div("Iteration of Activity for single Object"),
                    ]),
                    html.Div("(Only counts events with exactly one object of selected object type)"),
                    dcc.Dropdown(id="events-execution-object-type-dropdown", style={"marginLeft": "25px", "marginRight": "25px"}, placeholder="object type"),
                    dcc.Loading(id="loading_events-execution-graph", style={"display": "block"}, type="circle", color='#0098A1',
                                target_components={"events-execution-graph": "figure"}, children=[
                            dcc.Graph(id="events-execution-graph")
                        ]),
                    html.Div("Only consider the xx-th iteration (specify below) of an activity regarding the same object of selected object type: "),
                    dcc.Input(id="events-execution-int", type="number", placeholder="execution instance", style={"display": "inline"}),
                    html.Button(id=f"events-objects-execution-button", children=["Filter"], style={"display": "inline", "background": CHART_COLOURS[2], "color": "white", "fontSize": 14, "margin": "5px"}),
                ]),
        ]),
        html.Div(style={"display": "flex", "flexDirection": "row", "margin": "5px"}, children=[
            html.Div(style={"width": "50%", "border": "1px #bbb solid", "align": "center", "textAlign": "center"},
                     hidden=False, children=[
                    html.H4(children=[
                        html.Div("Total Number of Objects involved in Event ", style={"display": "inline"}),
                    ]),
                    dcc.Loading(id="loading_events-total-objects-graph", style={"display": "block"}, type="circle", color='#0098A1',
                                target_components={"events-total-objects-graph": "figure"}, children=[
                            dcc.Graph(id="events-total-objects-graph")
                        ]),
                    html.Div("Only consider events with the following total number of objects: "),
                    dcc.Input(id="events-total-objects-int", type="number", placeholder="no. objects (int)", style={"display": "inline"}),
                    html.Button(id=f"events-total-objects-button", children=["Filter"], style={"display": "inline", "background": CHART_COLOURS[2], "color": "white", "fontSize": 14, "margin": "5px"}),
                ]),
            html.Div(style={"width": "50%", "border": "1px #bbb solid", "align": "center", "textAlign": "center"},
                     hidden=False, children=[
                html.H4("Active Events ", style={"display": "inline"}),
                dcc.Loading(id="loading_events-active-graph", style={"display": "block"}, type="circle",
                            color='#0098A1',
                            target_components={"events-active-graph": "figure"}, children=[
                        dcc.Graph(id="events-active-graph")
                    ]),
                html.Div(id="active-events-selection", children=[
                    html.Div("Include all events, only quantity active events or only quantity inactive events (if you change your mind you have to reset): "),
                    dcc.RadioItems(id="events-active-selection", options=[TERM_ALL, TERM_ACTIVE, TERM_INACTIVE],
                               value=TERM_ALL,
                               inline=True, style={"display": "inline"})
                ])
            ])
        ]),
        html.Div(id="sublog_cp-active", style={"border": "1px #bbb solid", "margin": "5px"}, children=[
            html.H4([
                html.Div("Collection-point-active Events", style={"display": "inline"}),
            ]),
            html.Div(id="cp-active-figures", children=[
                # returned by operations.charts_sublog_cp_active if qty data is available
            ]),
            html.Div("Only include events active for", style={"display": "inline", "fontSize": 14, "margin": "5px"}),
            dcc.RadioItems(id="events-cp-active-all-any", options=[{"label": "all", "value": TERM_ALL},
                                                                   {"label": "any", "value": TERM_ANY}],
                           value=TERM_ALL, inline=True, style={"display": "inline","fontSize": 14, "margin": "5px"}),
            html.Div("of the following collection points (no selection: any):", style={"display": "inline", "fontSize": 14, "margin": "5px"}),
            html.Div(style={"display": "flex", "flexDirection": "row"}, children=[
                dcc.Dropdown(id="events-cp-active-filter", multi=True, clearable=True, style={"margin": "10px", "width": "95%"}),
                html.Button(id="events-cp-active-filter-button", children=["Filter"], style={"display": "inline", "background": CHART_COLOURS[2], "color": "white", "fontSize": 14, "margin": "5px"}),
            ]),
        ]),
        html.Div(id="sublog_it-active", style={"border": "1px #bbb solid", "margin": "5px"}, children=[
            html.H4([
                html.Div("Item-type-active Events", style={"display": "inline"}),
            ]),
            html.Div(["Charts only depict <21 item types."], style={"fontSize": 14, "margin": "5px"}),
            html.Div(id="it-active-figures", children=[
                # returned by operations.charts_sublog_cp_active if qty data is available
            ]),
            html.Div("Only include events active for", style={"display": "inline", "fontSize": 14, "margin": "5px"}),
            dcc.RadioItems(id="events-it-active-all-any", options=[{"label": "all", "value": TERM_ALL},
                                                                   {"label": "any", "value": TERM_ANY}],
                           value=TERM_ALL, inline=True, style={"display": "inline","fontSize": 14, "margin": "5px"}),
            html.Div("of the following item types (no selection: any):", style={"display": "inline", "fontSize": 14, "margin": "5px"}),
            html.Div(style={"display": "flex", "flexDirection": "row"}, children=[
                dcc.Dropdown(id="events-it-active-filter", multi=True, clearable=True, style={"margin": "10px", "width": "95%"}),
                html.Button(id="events-it-active-filter-button", children=["Filter"], style={"display": "inline", "background": CHART_COLOURS[2], "color": "white", "fontSize": 14, "margin": "5px"}),
            ]),
        ]),
        html.Div(id="sublog_ilvl", style={"border": "1px #bbb solid", "margin": "5px"}, children=[
            html.H4([
                html.Div("Item Level Development", style={"display": "inline"}),
            ]),
            html.Div(["Chart only shows item levels of selected events and connects them to a step chart."], style={"fontSize": 14, "margin": "5px"}),
            html.Div(style={"display": "flex", "flexDirection": "row", "margin": "5px"}, children=[
                    html.Div(style={"width": "50%", "align": "center", "textAlign": "center"}, children=[
                        dcc.Dropdown(id="events-ilvl-cp-dropdown", placeholder="collection point", style={"margin": "5px"}),
                        ]),
                    html.Div(style={"width": "50%", "align": "center", "textAlign": "center"}, children=[
                        dcc.Dropdown(id="events-ilvl-item-type-dropdown", multi=True, placeholder="item type", style={"margin": "5px"}),
                        ])
                ]),
            html.Div(id="sublog_ilvl-figure", children=[
                # returned by operations.chart_ilvl_sublog_selection if qty data is available
            ]),
            html.Div(["If you only wish to consider events executed in a particular quantity state, please select the range to be considered."], style={"fontSize": 14, "margin": "5px"}),
            dcc.RangeSlider(id="events-ilvl-range", step=1, min=0, max = 100, value=[0, 100],
                            # vertical=True,
                            # tooltip={"placement": "bottom", "always_visible": True}
                            ),
            html.Button(id="events-ilvl-range-button", children=["Filter"],
                            style={"background": CHART_COLOURS[2], "color": "white",
                                   "fontSize": 14, "margin": "5px"}),
            html.Div(["If you only wish to consider events within a specific time period, please select the time period above (chart updates when entering dates but data is only filtered when initiated by button)."], style={"fontSize": 14, "margin": "5px"}),
        ]),
        ObjectTypeSelection
    ]),
])

ProjectionItemTypesCP = html.Div(id="sublog-qty-projection", style={"margin": "5px"}, children=[
    html.Div(style={"display": "flex", "flexDirection": "row", "margin": "5px"}, children=[
        html.Div(style={"width": "25%", "display": "block"}, children=[
            html.H3("Item Type Selection", style={"fontSize": 20}),
            html.Div(["If you only want to consider a subset of items for your analysis, "
                      "remove items you are not interested in."], style={"fontSize": 14, "margin": "5px"}),
        ]),
        html.Div(style={"width": "75%", "margin": "5px"}, children=[
            dcc.Dropdown(id="qel-item-type-projection", multi=True,
                         placeholder="Select item types to consider", clearable=True),
            html.Button("Select Item Types", id="qel-item-type-projection-button",
                        style={"background": CHART_COLOURS[0], "color": "white", "margin": "10px", "align": "right"})
        ]),
    ]),
    html.Div(style={"display": "flex", "flexDirection": "row", "margin": "5px"}, children=[
        html.Div(style={"width": "25%", "display": "block"}, children=[
            html.H3("Collection Point Selection", style={"fontSize": 20}),
            html.Div(["If your analysis of quantity data should only consider a subset of collection points remove items you are not interested in." ], style={"fontSize": 14, "margin": "5px","marginTop": None}),
        ]),
        html.Div(style={"width": "75%", "margin": "5px"}, children=[
            dcc.Dropdown(id="qel-collection-point-projection", multi=True,
                         placeholder="Select relevant collection points", clearable=True),
            html.Button("Select Collection Points", id="qel-collection-point-projection-button",
                        style={"background": CHART_COLOURS[0], "color": "white", "margin": "10px", "align": "right"})
        ])
    ])
])


QChangeSpecification = html.Div(style={"margin": "5px"}, children=[
    html.Div(style={"display": "flex", "flexDirection": "row", "margin": "5px", "verticalAlign": "middle", "marginBottom": "10px"}, children=[
        html.Div(style={"width": "33%", "display": "flex", "margin": "5px", "verticalAlign": "middle", "align": "left"}, children=[
                html.Div("Perspective", style={"fontSize": 16, "display": "block", "width": "30%"}),
                dcc.RadioItems(id="qop-type", options=[{"label": "Quantity Changes", "value": TERM_QUANTITY_CHANGES},
                                                        {"label": "Item Movements", "value": TERM_ITEM_MOVEMENTS}],
                               value=TERM_QUANTITY_CHANGES, inline=True, style={"margin": "5px", "display": "inline",
                                                                         "verticalAlign": "middle", "fontSize": 14})
        ]),
        html.Div(style={"width": "33%", "display": "flex", "margin": "5px", "verticalAlign": "middle"}, children=[
                html.Div("Adding/Removing (proj.)", style={"fontSize": 16, "display": "block", "width": "30%"}),
                dcc.RadioItems(id="qop-property", options=[{"label": "Any", "value": TERM_ALL},
                                                        {"label": "Adding", "value": TERM_ADDING},
                                                           {"label": "Removing", "value": TERM_REMOVING}],
                               value=TERM_ALL, inline=True, style={"margin": "5px", "display": "inline",
                                                                         "verticalAlign": "middle", "fontSize": 14}),
        ]),
        html.Div(style={"width": "33%", "display": "flex", "margin": "5px", "verticalAlign": "middle"}, children=[
                html.Div("Included Instances", style={"fontSize": 16, "display": "block", "width": "30%"}),
                dcc.RadioItems(id="qop-active", options=[{"label": "All", "value": TERM_ALL},
                                                        {"label": "Active Qty Operations", "value": TERM_ACTIVE_OPERATIONS},
                                                         {"label": "Active Qty Updates", "value": TERM_ACTIVE_UPDATES},],
                               value=TERM_ALL, inline=True, style={"margin": "5px", "display": "inline",
                                                                         "verticalAlign": "middle", "fontSize": 14}),
        ]),
    ]),
    html.Div(id="qop-it-agg-selection", style={"display": "flex", "flexDirection": "row", "margin": "5px", "marginBottom": "10px"}, children=[
        html.Div(style={"width": "50%", "display": "flex", "margin": "5px"}, children=[
            html.Div("Item Type Aggregation: ", style={"fontSize": 16, "display": "block", "width": "25%"}),
            dcc.RadioItems(id="qop-it-agg", options=[{"label": "No Item Type Aggregation", "value": False},
                                                     {"label": "Total", "value": True}],
                           value=False, inline=True, style={"display": "inline", "fontSize": 14, "margin": "5px",
                                                                "verticalAlign": "middle"}),
        ]),
        html.Div(id="qop-cp-agg-selection", style={"width": "50%", "display": "flex", "margin": "5px"}, children=[
                html.Div("Collection Point Aggregation: ", style={"fontSize": 16, "display": "block", "width": "25%"}),
                dcc.RadioItems(id="qop-cp-agg", options=[{"label": "No Item Type Aggregation", "value": False},
                                                          {"label": "Joint", "value": True}],
                               value=False, inline=True, style={"margin": "5px", "display": "inline", "fontSize": 14,
                                                                    "verticalAlign": "middle"}),
            ])
    ]),
    html.Div(style={"display": "flex", "flexDirection": "row", "margin": "5px"}, children=[
        html.Div(style={"width": "50%", "display": "block"}, children=[
            html.Div(["Item Types relevant for Quantity Operation Analysis"], style={"fontSize": 20}),
            html.Div(["Select the item types you want to consider for your analysis (subset of item types in sublog)."], style={"fontSize": 14, "margin": "5px"}),
            dcc.Dropdown(id="qop-item-type-projection", multi=True,
                         placeholder="Select item types to consider", clearable=True),
            # html.Button("Select Item Types", id="ilvl-item-type-projection-button",
            #             style={"background": CHART_COLOURS[0], "color": "white", "margin": "10px", "align": "right"})
        ]),
        html.Div(style={"width": "50%", "margin": "5px"}, children=[
            html.Div(["Collection Point relevant for Quantity Operation Analysis"], style={"fontSize": 20}),
            html.Div(["Select the collection points you want to consider for your analysis (subset of item types in sublog)."], style={"fontSize": 14, "margin": "5px","marginTop": None}),
            dcc.Dropdown(id="qop-collection-point-projection", multi=True,
                         placeholder="Select relevant collection points", clearable=True),
            # html.Button("Select Collection Points", id="ilvl-collection-point-projection-button",
            #             style={"background": CHART_COLOURS[0], "color": "white", "margin": "10px", "align": "right"})
        ]),
    ])
])

ActivityImpact = html.Div(style={"margin": "5px"}, children=[
    html.H5("Activity Impact on Collection Point's Item Levels"),
    html.Div("Display the number of quantity operations or the aggregated quantity updates:", style={"display": "inline", "fontSize": 14, "margin": "5px",
                                                            "verticalAlign": "middle"}),
    dcc.RadioItems(id="activity-impact-radio", options=[{"label": "Number of Quantity Operations", "value": True},
                   {"label": "Aggregated Quantity Updates", "value": False}], value=True, inline=True, style={"display": "inline", "fontSize": 14, "margin": "5px",
                                                            "verticalAlign": "middle"}),
    dcc.Loading(id="loading-activity-impact", style={"display": "block"}, type="circle",
                color='#0098A1',
                target_components={"activity-impact-graph": "figure"}, children=[
            dcc.Graph(id="activity-impact-graph", style={'height': '700px', 'width': '100%'})
        ]),
])

QuantityOperationsOverTime = html.Div(style={"margin": "5px", "border": "1px #bbb solid"}, children=[
    html.H5("Quantity Operations over Time", style={"margin": "5px"}),
    html.Div("Select time period you want to plot the executed Quantity Operations over. "
             "Too large periods lead to unreadable plots.", style={"margin": "5px"}),
    html.Div(style={"display": "flex", "flexDirection": "row", "margin": "5px"}, children=[
        dcc.DatePickerRange(id="qop-time-period", clearable=True, style={"margin": "5px"},
                            month_format='MMMM Y', display_format='D-M-Y', first_day_of_week = 1,
                            start_date_placeholder_text="First Date",
                            end_date_placeholder_text="Last Date"),
        html.Button(id="qop-time-period-button", children=["Filter"],
                        style={"display": "inline", "background": CHART_COLOURS[2], "color": "white",
                               "fontSize": 14, "margin": "5px"})
    ]),
    dcc.Loading(id="loading-quantity-operation-overview", style={"display": "block"},
                    type="circle", color='#0098A1',
                    target_components={"quantity-operation-overview-graph": "figure"}, children=[
                dcc.Graph(id="quantity-operation-overview-graph")
            ])
])

DescriptiveStatsQUPItemTypes = html.Div(style={"margin": "5px"}, children=[
    html.Div(style={"margin": "5px"}, children=[
        html.H5(["Quantity Updates per Item Type"]),
        create_simple_data_table("qop-stats-item-types"),
        html.Div(style={"align": "center", "textAlign": "center"}, children=[
            html.Div("Display Points in Boxplot: ", style={"fontSize": 16, "display": "inline", "margin": "5px"}),
            dcc.RadioItems(id="qop-boxplots-item-types-points",
                           options=[{"label": "All points", "value": True}, {"label": "Outliers", "value": False}],
                           value=False, inline=True,
                           style={"display": "inline", "fontSize": 16, "margin": "10px", "align": "center",
                                  "alignText": "center"}),
        ]),
        dcc.Loading(id="loading-qop-boxplots-item-types", style={"display": "block"}, type="circle", color='#0098A1',
                    target_components={"qop-boxplots-item-types": "figure"}, children=[
                dcc.Graph(id="qop-boxplots-item-types")
            ]),
    ]),
])
DescriptiveStatsFrequencyItemTypes = html.Div(style={"margin": "5px"}, children=[
    html.Div(style={"margin": "5px"}, children=[
        html.H5(["Time between Active Quantity Update per Item Type"]),
        # create_simple_data_table("qop-stats-freq-item-types"),
        dcc.Loading(id="loading-qop-boxplots-freq-item-types", style={"display": "block"}, type="circle", color='#0098A1',
                    target_components={"qop-boxplots-freq-item-types": "figure"}, children=[
                dcc.Graph(id="qop-boxplots-freq-item-types")
            ]),
    ]),
])

SingleQupData = html.Div(style={"margin": "5px"}, children=[
    html.Div(style={"display": "flex", "flexDirection": "row", "margin": "5px"}, children=[
        html.Div(style={"width": "50%", "align": "center", "textAlign": "center"},
                 hidden=False, children=[
                html.H5('Selected Quantity Updates'),
                dcc.Loading(id="loading-single-qup-executions", style={"display": "block"}, type="circle",
                            color='#0098A1',
                            target_components={"single-qup-executions-graph": "figure"}, children=[
                        dcc.Graph(id="single-qup-executions-graph", style={"height": "650px"}),
                    ]),
            ]),
        html.Div(style={"width": "50%","align": "center", "textAlign": "center"},
                 hidden=False, children=[
                html.H5(["Distribution Selected Quantity Updates"]),
                dcc.RadioItems(id="qup-view", options=[{"label": "Collection Point", "value": TERM_COLLECTION},
                                                    {"label": "Activity", "value": TERM_ACTIVITY}],
                           value=TERM_COLLECTION, inline=True, style={"display": "inline", "fontSize": 16, "margin": "10px"}),
                dcc.Loading(id="loading-qop-activity-qup-boxplots", style={"display": "block"},
                        type="circle", color='#0098A1',
                        target_components={"qop-activity-qup-boxplots": "figure"}, children=[
                    dcc.Graph(id="qop-activity-qup-boxplots", style={"height": "620px"})
                ]),
        ]),
    ]),
    html.Div(style={"display": "flex", "flexDirection": "row", "margin": "5px"}, children=[
        html.Div(style={"width": "50%", "align": "center", "textAlign": "center"},
                 hidden=False, children=[
                html.H5('Time between Active Quantity Updates'),
                dcc.Loading(id="loading-single-qup-freq", style={"display": "block"}, type="circle",
                            color='#0098A1',
                            target_components={"single-qup-freq-graph": "figure"}, children=[
                        dcc.Graph(id="single-qup-freq-graph", style={"height": "650px"}),
                    ]),
            ]),
        html.Div(style={"width": "50%","align": "center", "textAlign": "center"},
                 hidden=False, children=[
                html.H5(["Distribution Timedelta between active Quantity Updates"]),
                dcc.RadioItems(id="qup-freq-view", options=[{"label": "Collection Point", "value": TERM_COLLECTION},
                                                    {"label": "Activity", "value": TERM_ACTIVITY}],
                           value=TERM_COLLECTION, inline=True, style={"display": "inline", "fontSize": 16, "margin": "10px"}),
                dcc.Loading(id="loading-qup-freq-boxplots", style={"display": "block"},
                        type="circle", color='#0098A1',
                        target_components={"qup-freq-boxplots": "figure"}, children=[
                    dcc.Graph(id="qup-freq-boxplots", style={"height": "620px"})
                ]),
        ]),
    ]),
])

QuantityUpdateComponent = html.Div(style={"margin": "5px"}, children=[
    html.H4('Item Type Perspective'),
    html.Div("Find some information on the executed quantity updates of the selected entries."),
    dcc.Dropdown(id="qop-activity-qup-item-types-dropdown", placeholder="Select item type", clearable=True),
    SingleQupData,
    # html.Div(style={"display": "flex", "flexDirection": "row", "margin": "5px"}, children=[
    #     html.Div(style={"width": "50%", "align": "center", "textAlign": "center"},
    #                      hidden=False, children=[
    #     ]),
    #     html.Div(style={"width": "50%", "align": "center", "textAlign": "center"},
    #              hidden=False, children=[
    #             html.H5(["Activity Item Type Active Frequency"]),
    #             dcc.Loading(id="loading-qop-activity-it-active-graph", style={"display": "block"},
    #                         type="circle", color='#0098A1',
    #                         target_components={"qop-activity-it-active-graph": "figure"}, children=[
    #                     dcc.Graph(id="qop-activity-it-active-graph")
    #             ])
    #     ]),
    # ]),
])

SelectedElementsQuantityOperations = html.Div(style={"margin": "5px", "border": "1px #bbb solid"}, children=[
    html.H4(["Quantity Operations and Quantity Relations"]),
    html.Div("Select an activity, collection point, quantity relation (both) to analyse the corresponding "
             "quantity operations and updates.", style={"margin": "5px"}),
    html.Div(style={"display": "flex", "flexDirection": "row", "margin": "5px"}, children=[
        html.Div(style={"width": "50%", "margin": "5px"}, children=[
            dcc.Dropdown(id="qop-activity-dropdown", placeholder="Select activity", clearable=True, style={"margin": "5px"})
        ]),
        html.Div(style={"width": "50%", "margin": "5px"}, children=[
            dcc.Dropdown(id="qop-cp-dropdown", placeholder="Select collection point", clearable=True),
        ]),
    ]),
    QuantityOperationsOverTime,
    html.Div(style={"display": "flex", "flexDirection": "row", "margin": "5px"}, children=[
        html.Div(style={"width": "50%", "align": "center", "textAlign": "center"},
                 hidden=False, children=[
                html.H5("Item-type-active Quantity Operations"),
                    dcc.Loading(id="loading-it-active-distribution-graph", style={"display": "block"},
                                type="circle", color='#0098A1',
                                target_components={"qop-it-active-distribution-graph": "figure"}, children=[
                            dcc.Graph(id="qop-it-active-distribution-graph")
                    ])
            ]),
        html.Div(style={"width": "50%", "align": "center", "textAlign": "center"},
                 hidden=False, children=[
                html.H5("Frequency Active Item Type Combinations"),
                html.Div(
                "(Counts the full combination of active item types --Total number = total number of quantity operations in current selection.)"),
                dcc.Loading(id="loading-it-active-combination-graph", style={"display": "block"},
                        type="circle", color='#0098A1',
                        target_components={"qop-it-active-combination-graph": "figure"}, children=[
                    dcc.Graph(id="qop-it-active-combination-graph")
                ])
        ]),
    ]),
    DescriptiveStatsQUPItemTypes,
    DescriptiveStatsFrequencyItemTypes,
    html.Div(style={"display": "flex", "flexDirection": "row", "margin": "5px"}, children=[
        html.Div(style={"width": "50%", "align": "center", "textAlign": "center"},
                         hidden=False, children=[
                html.H5(["Mean Additions/Removals per Item Type and (Time) Unit"]),
                dcc.RadioItems(id="qop-average-qup-time-unit", options=[{"label": "Daily", "value": TERM_DAILY},
                                                                        {"label": "Monthly", "value": TERM_MONTHLY},
                                                                        {"label": "Event", "value": TERM_EVENT},
                                                                        {"label": "Addition/Removal", "value": TERM_ADDING},],
                               value=TERM_MONTHLY, inline=True,
                               style={"display": "inline", "fontSize": 16, "margin": "10px"}),
                dcc.Loading(id="loading-qop-mean-additions-removals-graph", style={"display": "block"},
                            type="circle", color='#0098A1',
                            target_components={"qop-mean-additions-removals-graph": "figure"}, children=[
                    dcc.Graph(id="qop-mean-additions-removals-graph")
                    ])
                ]),
        html.Div(style={"width": "50%", "align": "center", "textAlign": "center"},
                 hidden=False, children=[
            html.H5(["Mean time between Additions/Removals per Item Type"]),
            dcc.Loading(id="loading-qop-mean-frequency-qup-type-graph", style={"display": "block"},
                        type="circle", color='#0098A1',
                        target_components={"qop-mean-frequency-qup-type-graph": "figure"}, children=[
                dcc.Graph(id="qop-mean-frequency-qup-type-graph")
            ])
        ]),
    ]),
    QuantityUpdateComponent,
])

QuantityOperationDescription = html.Div(style={"display": "block", "margin": "5px"}, children=[
    html.H4("Overview Quantity Operations"),
    html.Div("Find an overview of the processed quantity operations for the selected events."),
    ActivityImpact,
    html.Div(style={"display": "flex", "flexDirection": "row", "margin": "5px"}, children=[
        html.Div(style={"width": "50%", "align": "center", "textAlign": "center"},
                 hidden=False, children=[
                html.H5([
                    html.Div("Active Quantity Operations (Activity & Collection Point)", style={"display": "inline"}),
                ]),
                dcc.Loading(id="loading-active-instances-cp", style={"display": "block"},
                            type="circle", color='#0098A1',
                            target_components={"active-instances-cp-graph": "figure"}, children=[
                        dcc.Graph(id="active-instances-cp-graph")
                    ]),
                ]),
        html.Div(style={"width": "50%", "align": "center", "textAlign": "center"},
                 hidden=False, children=[
                html.H5("Direction of Quantity Changes"),
                dcc.Loading(id="loading-direction-changes", style={"display": "block"}, type="circle",
                            color='#0098A1',
                            target_components={"direction-changes-graph": "figure"}, children=[
                        dcc.Graph(id="direction-changes-graph")
                    ]),
            ]),
    ]),
    SelectedElementsQuantityOperations,
])

QuantityOperationComponent = html.Div(style={"margin": "5px"}, children=[
    html.H3('Quantity Operation Processing and Analysis'),
    html.Div(["Overview of the quantity operations for selected events"], style={"fontSize": 14}),
    QChangeSpecification,
    html.Details([html.Summary("View Data", style={"margin": "5px","fontSize": 16}),
                     create_data_table("qop-data-table")], style={"margin": "5px","fontSize": 16}),
    QuantityOperationDescription,
])

ProjectionQState = html.Div(style={"margin": "5px"}, children=[
    html.Div(style={"display": "flex", "flexDirection": "row", "margin": "5px"}, children=[
        html.Div(style={"width": "50%", "display": "block"}, children=[
            html.Div(["Item Types relevant for Quantity State"], style={"fontSize": 20}),
            html.Div(["Select the item types you want to consider for the quantity state analysis (subset of item types in sublog)."], style={"fontSize": 14, "margin": "5px"}),
            dcc.Dropdown(id="ilvl-item-type-projection", multi=True,
                         placeholder="Select item types to consider", clearable=True),
            # html.Button("Select Item Types", id="ilvl-item-type-projection-button",
            #             style={"background": CHART_COLOURS[0], "color": "white", "margin": "10px", "align": "right"})
        ]),
        html.Div(style={"width": "50%", "margin": "5px"}, children=[
            html.Div(["Collection Point relevant for Quantity State"], style={"fontSize": 20}),
            html.Div(["Select the collection points you want to consider for the quantity state (subset of item types in sublog)."], style={"fontSize": 14, "margin": "5px","marginTop": None}),
            dcc.Dropdown(id="ilvl-collection-point-projection", multi=True,
                         placeholder="Select relevant collection points", clearable=True),
            # html.Button("Select Collection Points", id="ilvl-collection-point-projection-button",
            #             style={"background": CHART_COLOURS[0], "color": "white", "margin": "10px", "align": "right"})
        ]),
    ]),
])

QStateSpecification = html.Div([
    html.Div(style={"display": "flex", "flexDirection": "row", "margin": "5px", "verticalAlign": "middle", "marginBottom": "10px"}, children=[
        html.Div(style={"width": "50%", "display": "flex", "margin": "5px", "verticalAlign": "middle", "align": "left"}, children=[
                html.Div("Perspective", style={"fontSize": 16, "display": "block", "width": "30%"}),
                dcc.RadioItems(id="ilvl-perspective", options=[{"label": "Item Levels", "value": TERM_ITEM_LEVELS},
                                                        {"label": "Item Associations", "value": TERM_ITEM_ASSOCIATION}],
                               value=TERM_ITEM_LEVELS, inline=True, style={"margin": "5px", "display": "inline",
                                                                         "verticalAlign": "middle", "fontSize": 14})
        ]),
        html.Div(style={"width": "50%", "display": "flex", "margin": "5px", "verticalAlign": "middle"}, children=[
            html.Div("Pre/Post Event Item Level", style={"fontSize": 16, "display": "block", "width": "30%"}),
            dcc.RadioItems(id="ilvl-type", options=[{"label": "Pre Event", "value": PRE_EVENT_ILVL},
                                                    {"label": "Post Event", "value": POST_EVENT_ILVL}],
                           value=PRE_EVENT_ILVL, inline=True, style={"margin": "5px", "display": "inline",
                                                                     "verticalAlign": "middle", "fontSize": 14}),
        ]),
    ]),
    html.Div(style={"display": "flex", "flexDirection": "row", "margin": "5px", "verticalAlign": "middle", "marginBottom": "10px"}, children=[
        html.Div(style={"width": "50%", "display": "flex", "margin": "5px", "verticalAlign": "middle"}, children=[
                html.Div("Property", style={"fontSize": 16, "display": "block", "width": "30%"}),
                dcc.RadioItems(id="ilvl-property", options=[{"label": "Any", "value": TERM_ALL},
                                                        {"label": "Available", "value": ILVL_AVAILABLE},
                                                           {"label": "Required", "value": ILVL_REQUIRED}],
                               value=TERM_ALL, inline=True, style={"margin": "5px", "display": "inline",
                                                                         "verticalAlign": "middle", "fontSize": 14}),
        ]),
        html.Div(style={"width": "50%", "display": "flex", "margin": "5px", "verticalAlign": "middle"}, children=[
                html.Div("Quantity State Development Display (Graph)", style={"fontSize": 16, "display": "block", "width": "30%"}),
                dcc.RadioItems(id="ilvl-graph-display", options=[{"label": "Full Log", "value": TERM_ALL},
                                                        {"label": "Sublog", "value": TERM_SUBLOG}],
                               value=TERM_ALL, inline=True, style={"margin": "5px", "display": "inline",
                                                                         "verticalAlign": "middle", "fontSize": 14}),
        ]),
    ]),
])

QStateAggregationProjection = html.Div([
    html.Div(id="ilvl-it-agg-selection", style={"display": "flex", "flexDirection": "row", "margin": "5px", "marginBottom": "10px"}, children=[
        html.Div(style={"width": "50%", "display": "flex", "margin": "5px"}, children=[
            html.Div("Item Type Aggregation", style={"fontSize": 16, "display": "block", "width": "25%"}),
            dcc.RadioItems(id="ilvl-it-agg", options=[{"label": "No Item Type Aggregation", "value": False},
                                                     {"label": "Total", "value": True}],
                           value=False, inline=True, style={"display": "inline", "fontSize": 14, "margin": "5px",
                                                                "verticalAlign": "middle"}),
        ]),
        html.Div(id="ilvl-cp-agg-selection", style={"width": "50%", "display": "flex", "margin": "5px"}, children=[
                html.Div("Collection Point Aggregation ", style={"fontSize": 16, "display": "block", "width": "25%"}),
                dcc.RadioItems(id="ilvl-cp-agg", options=[{"label": "No Item Type Aggregation", "value": False},
                                                          {"label": "Overall", "value": True}],
                               value=False, inline=True, style={"margin": "5px", "display": "inline", "fontSize": 14,
                                                                    "verticalAlign": "middle"}),
            ])
    ]),
])

QStateDescriptiveStatistics = html.Div([
    html.H5("Descriptive Statistics selected Item Levels"),
    html.Div(style={"margin": "5px", "display": "flex", "flexDirection": "row"}, children=[
                html.Div("Compare Distribution Stats (Descriptive Stats and Boxlpots): ", style={"fontSize": 16, "display": "inline"}),
                dcc.RadioItems(id="ilvl-view", options=[{"label": "Collection Point", "value": TERM_COLLECTION},
                                                          {"label": "Item Type", "value": TERM_ITEM_TYPES},
                                                        {"label": "Activity", "value": TERM_ACTIVITY}],
                               value=TERM_COLLECTION, inline=True, style={"display": "inline", "fontSize": 16, "margin": "10px"}),
    ]),
    create_simple_data_table("ilvl-stats"),
    html.Div(id="ilvl-boxplots")
])

QuantityStateExecution = html.Div(style={"margin": "5px", "border": "1px #bbb solid"}, children=[
    html.H4([
            html.Div("Quantity State at Execution", style={"display": "inline"}),
    ]),
    html.Div("(Select at least one activity, collection point or item type for plots)", style={"margin": "5px"}),
    html.Div(style={"width": "50%", "margin": "5px"}),
    html.Div(style={"display": "flex", "flexDirection": "row", "margin": "5px"}, children=[
        html.Div(style={"width": "50%", "margin": "5px"}, children=[
            dcc.Dropdown(id="qstate-execution-activity-dropdown", placeholder="All activities", clearable=True, style={"margin": "5px"})
        ]),
        html.Div(style={"width": "50%", "margin": "5px"}, children=[
            dcc.Dropdown(id="qstate-execution-collection-point-dropdown", placeholder="All collection points", clearable=True, style={"margin": "5px"})
        ]),
    ]),
    html.Div(style={"display": "flex", "flexDirection": "row", "margin": "5px"}, children=[
        html.Div(style={"width": "50%", "margin": "5px"}, children=[
            dcc.Dropdown(id="qstate-execution-item-type-dropdown", placeholder="Select item type",
                         clearable=True, style={"margin": "5px"}),
        ]),
        html.Div(id="qstate-display-item_type-active-selection", style={"margin": "5px", "display": "flex", "flexDirection": "row"},
                 children=[
                     html.Div("Display Events/item types: ", style={"fontSize": 16, "display": "inline"}),
                     dcc.RadioItems(id="qstate_display_item_type_active", options=[{"label": "All", "value": TERM_ALL},
                                                      {"label": "Only active item type(s)", "value": TERM_ITEM_TYPE_ACTIVE}],
                           value=TERM_ALL, inline=True, style={"display": "inline", "fontSize": 16, "margin": "10px"}),
        ])
    ]),
    # html.H5("Quantity State at Execution over Time"),
    # dcc.Loading(id="loading-qstate-execution", style={"display": "block"},
    #                 type="circle", color='#0098A1',
    #                 target_components={"qstate-execution-graph": "figure"}, children=[
    #             dcc.Graph(id="qstate-execution-graph")
    #         ]),
    QStateDescriptiveStatistics,
    html.Div(style={"display": "flex", "flexDirection": "row", "margin": "5px"}, children=[
        html.Div(style={"width": "50%", "margin": "5px"}, children=[
            html.H5("Item Levels at Event Executions",style={"margin": "5px"}),
            dcc.Loading(id="loading-qstate-execution-bar-chart", style={"display": "block"},
                    type="circle", color='#0098A1',
                    target_components={"qstate-execution-bar-chart": "figure"}, children=[
                dcc.Graph(id="qstate-execution-bar-chart")
            ]),
        ]),
        html.Div(style={"width": "50%", "margin": "5px"}, children=[
            html.H5("Frequency of Item Level at Execution of Collection Point", style={"margin": "5px"}),
            html.Div("(Select a collection point above)",style={"width": "50%", "margin": "5px"}),
            dcc.Loading(id="loading-qstate-execution-histogram", style={"display": "block"},
                    type="circle", color='#0098A1',
                    target_components={"qstate-execution-hist": "figure"}, children=[
                dcc.Graph(id="qstate-execution-hist")
            ])
        ]),
    ]),
    html.Div(id="ilvl-pre-post-component", children = [
        html.H5("Item Levels before and after Event Execution per Item Type", style={"margin": "5px"}),
        html.Div(style={"align": "center", "textAlign": "center"}, children=[
        html.Div("Chart Type: ", style={"fontSize": 16, "display": "inline", "margin": "5px"}),
        dcc.RadioItems(id="qstate-pre-post", options=[{"label": "Boxplots", "value": False},
                                                               {"label": "Bar Chart", "value": True}],
                        value=False, inline=True, style={"margin": "5px", "display": "inline", "fontSize": 14}),
        ]),
        dcc.Loading(id="loading-ilvl-pre-post", style={"display": "block"}, type="circle", color='#0098A1',
                            target_components={"ilvl-pre-post": "figure"}, children=[
                        dcc.Graph(id="ilvl-pre-post", style={"height": 700})
                    ]),
    ])


    # html.Div(style={"display": "flex", "flexDirection": "row", "margin": "5px"}, children=[
    #     html.Div(style={"width": "50%", "margin": "5px"}, children=[
    #         dcc.Loading(id="loading-qstate-execution-time-bar-chart", style={"display": "block"},
    #                 type="circle", color='#0098A1',
    #                 target_components={"qstate-execution-bar-chart": "figure"}, children=[
    #             dcc.Graph(id="qstate-execution-bar-chart")
    #         ])
    #     ]),
    #     html.Div(style={"width": "50%", "margin": "5px"}, children=[
    #         dcc.Loading(id="loading-qstate-execution-histogram", style={"display": "block"},
    #                 type="circle", color='#0098A1',
    #                 target_components={"qstate-execution-hist": "figure"}, children=[
    #             dcc.Graph(id="qstate-execution-hist")
    #         ])
    #     ]),
    # ]),

])

QStateDevelopment = html.Div(id="qstate-overview", style={"margin": "5px"}, children=[
    html.H4("Quantity State Development"),
    html.Div(style={"align": "center", "textAlign": "center"}, children=[
        html.Div("Display collection points: ", style={"fontSize": 16, "display": "inline", "margin": "5px"}),
        dcc.RadioItems(id="qstate-development-radio", options=[{"label": "Separately", "value": False},
                                                               {"label": "Jointly", "value": True}],
                        value=False, inline=True, style={"margin": "5px", "display": "inline", "fontSize": 14}),
    ]),
    html.Div(id="qstate-dev-component"),
    create_simple_data_table("cp-stats")
])


QuantityStateComponent = html.Div(style={"margin": "5px"}, children=[
    html.H3('Quantity State Data Processing And Analysis'),
    html.Div(["Overview of the quantity state for selected events"], style={"fontSize": 14}),
    QStateSpecification,
    QStateAggregationProjection,
    ProjectionQState,
    html.Details([html.Summary("View Data", style={"margin": "5px","fontSize": 16}),
                     create_data_table("ilvl-data-table")], style={"margin": "5px","fontSize": 16}),
    QStateDevelopment,
    QuantityStateExecution
])


SubLogCreationComponent = html.Div(id="sublog-creation", style={"display": "block", "margin": "5px", "border": "1px #bbb solid"}, children=[
    html.Div(style={"verticalAlign": "middle", "display": "flex", "flexDirection": "row"},
            children=[
                html.Div(style={"width": "25%"}, children=[
                    html.H2("Sublog Selection", style={"margin": "5px", "marginTop": "10px"})
                ]),
                html.Div(style={"width": "75%"}, children=[
                    html.Button("Reset QEL", id="event-selection-reset", style={"background": CHART_COLOURS[1], "color": "white", "margin": "5px"}),
                    html.Div("Default: Full event log.", style={"fontSize": 14, "margin": "5px"}),
                ])
            ]),
    EventSelection,
    ProjectionItemTypesCP,
    ])

QuantityAnalysis = html.Div(id="analysis", children=[
    html.H2('Quantity Data Overview', style={"margin": "5px", "marginTop": "10px"}),
    dcc.Tabs(id="tabs-quantity-analysis", style={"margin": "5px", "marginTop": "10px"}, children=[
        dcc.Tab(label='Quantity State', children=[
            QuantityStateComponent,
        ]),
        dcc.Tab(label='Quantity Operations', children=[
            QuantityOperationComponent
        ]),
    ]),
])

QRPMComponent = html.Div(id="data-overview", children=[
    SubLogCreationComponent,
    QuantityAnalysis
])





