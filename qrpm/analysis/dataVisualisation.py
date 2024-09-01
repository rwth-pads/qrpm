import itertools
from typing import Iterable

import numpy as np
import pandas as pd
import plotly
import plotly.express as px
import plotly.graph_objects as go
import plotly.subplots as sp

import qrpm.analysis.quantityState as ilvvl
from qrpm.analysis.ocelOperations import get_total_count_of_objects, event_object_type_count, \
    get_execution_number, filter_events_for_time, add_time_since_last_instance
from qrpm.analysis.generalDataOperations import split_instance_and_variable_entries, convert_numeric_columns, convert_to_timestamp
from qrpm.analysis.generalDataOperations import remove_empty_columns
from qrpm.analysis.quantityOperations import create_quantity_updates, get_direction_quantity_instances
from qrpm.analysis.counterOperations import get_enhanced_quantity_instances, get_active_instances, \
    create_item_quantities, cp_projection, item_type_projection
from qrpm.GLOBAL import CHART_COLOURS, TERM_ITEM_TYPES, TERM_ITEM_QUANTITY, TERM_ITEM_LEVELS, TERM_TIME, TERM_EVENT, \
    TERM_ACTIVITY, TERM_COLLECTION, TERM_EVENTS, \
    TERM_OBJECT, TERM_OBJECT_TYPE, \
    TERM_OBJECT_COUNT, TERM_OBJECT_TYPE_COUNT, TERM_EXECUTION_COUNT, TERM_ACTIVE, TERM_INACTIVE, TERM_CP_ACTIVE, \
    EVENT_COUNT, TERM_ITEM_TYPE_ACTIVE, TERM_ALL, TERM_VALUE, TERM_DIRECTION, \
    TERM_INSTANCE_COUNT, QOP_ID, QOP_COUNT, TERM_OBJECT_TYPE_COMBINATION, TERM_OBJECT_TYPE_COMBINATION_FREQUENCY, \
    TERM_REMOVING, TERM_COUNT, TERM_DAILY, TERM_MONTHLY, TERM_QUP_TYPE, TERM_TIME_SINCE_LAST_EXECUTION, TERM_ADDING
import datetime


# wierd dash plotly bug: Figures are not displayed correctly but not changing anything about the code or the data but releading fixed the issue.
# Identified hot fix: try and except with the same figure leads to correct display


def get_mondays(data: pd.DataFrame) -> (pd.DatetimeIndex, pd.Series):
    """
    Generate the dates for every Monday
    :param data:
    :return:
    """

    if TERM_TIME in data.columns:
        pass
    else:
        raise ValueError("Data does not contain a time column.")

    # Generate the dates for every Monday
    mondays = pd.date_range(start=data[TERM_TIME].min(),
                            end=data[TERM_TIME].max(),
                            freq='W-MON')

    # Format the dates as strings in the format 'DD/MM'
    mondays_str = mondays.strftime('%d/%m')

    return mondays, mondays_str

def item_level_development_single_cp(ilvl: pd.DataFrame, cp: str, post_ilvl: bool = False) -> go.Figure:

    if isinstance(cp, str):
        cp = {cp}
    elif isinstance(cp, set):
        if len(cp) == 1:
            pass
        else:
            raise ValueError("Only one collection point can be displayed.")
    elif isinstance(cp, Iterable):
        if len(cp) == 1:
            pass
        else:
            raise ValueError("Only one collection point can be displayed.")
        cp = set(cp)
    else:
        raise ValueError("Collection point must be a string.")


    ilvl = cp_projection(qty=ilvl, cps=cp)

    ilvl = remove_empty_columns(ilvl)

    non_item_types, item_types = split_instance_and_variable_entries(set(ilvl.columns))

    ilvl = ilvl.melt(id_vars=non_item_types, var_name=TERM_ITEM_TYPES, value_name=TERM_ITEM_LEVELS)

    # format timestamps and sort data
    ilvl.loc[:, TERM_TIME] = pd.to_datetime(ilvl[TERM_TIME])
    ilvl = ilvl.sort_values(by=[TERM_TIME], ascending=True)

    # Generate the dates for each Monday
    mondays, mondays_str = get_mondays(ilvl)

    if post_ilvl:
        line_shape = "hv"
    else:
        line_shape = "vh"

    # Create the step chart
    fig = px.line(ilvl, x=TERM_TIME, y=TERM_ITEM_LEVELS, color=TERM_ITEM_TYPES,
                  line_shape=line_shape,
                  hover_data=[TERM_EVENT, TERM_ACTIVITY, TERM_ITEM_LEVELS, TERM_TIME], color_discrete_sequence=CHART_COLOURS)

    # Set the title and labels
    fig.update_layout(
                      xaxis_title='Time',
                      yaxis_title='Item Level',
                      xaxis=dict(tickangle=45),
        font=dict(
            size=14,
        ),
        legend=dict(
            orientation="h",
            y=1.01,
            xanchor="left",
            x=0,
            font=dict(
                size=12,
            ),
            yanchor="bottom"
        ),
    )



    # Update the x-axis tick values and labels
    fig.update_xaxes(tickvals=mondays, ticktext=mondays_str)

    return fig

def item_level_development_multiple_cps(ilvl: pd.DataFrame, cps: Iterable[str] = None, post_ilvl: bool = False) -> go.Figure:

    if cps:
        if isinstance(cps, str):
            cps = {cps}
        elif isinstance(cps, set):
            pass
        elif isinstance(cps, Iterable):
            cps = set(cps)
        else:
            raise ValueError("Collection points must be a string or an iterable of strings.")
    else:
        cps = set(ilvl[TERM_COLLECTION])

    non_item_types, item_types = split_instance_and_variable_entries(set(ilvl.columns))

    ilvl.loc[:, TERM_TIME] = pd.to_datetime(ilvl[TERM_TIME])
    ilvl = ilvl.sort_values(by=[TERM_TIME], ascending=True)

    if len(cps) > 1:
        pass
    else:
        return item_level_development_single_cp(ilvl=ilvl, cp=cps.pop(), post_ilvl=post_ilvl)

    row_heights = [5 for _ in range(len(cps))]

    fig = sp.make_subplots(rows=len(cps), cols=1, shared_xaxes=True, row_heights=row_heights)

    if post_ilvl:
        line_shape = "hv"
    else:
        line_shape = "vh"

    ilvl = ilvl.melt(id_vars=non_item_types, var_name=TERM_ITEM_TYPES, value_name=TERM_ITEM_LEVELS)

    item_type_colours = dict()
    for i, cp in enumerate(cps):
        if isinstance(cp, str):
            pass
        else:
            raise ValueError("Collection points must be strings.")

        ilvl_cp = ilvl.loc[ilvl[TERM_COLLECTION] == cp, :]

        for item_type in ilvl_cp[TERM_ITEM_TYPES].unique():

            if item_type in item_type_colours.keys():
                colour = item_type_colours[item_type]
                show_legend = False
            else:
                colour = CHART_COLOURS[len(item_type_colours) % len(CHART_COLOURS)]
                item_type_colours[item_type] = colour
                show_legend = True

            fig.add_trace(go.Scatter(x=ilvl_cp.loc[ilvl_cp[TERM_ITEM_TYPES] == item_type, TERM_TIME], y=ilvl_cp.loc[ilvl_cp[TERM_ITEM_TYPES] == item_type, TERM_ITEM_LEVELS],
                                     name=item_type, mode="lines", line=dict(shape=line_shape, color=colour),  showlegend=show_legend), row=i+1, col=1)

        fig.update_yaxes(title_text=f"{cp}", row=i+1, col=1)

    # Set the title and labels
    fig.update_layout(title=f"Item Level Development",
                      xaxis_title='Time',
                      font=dict(
                          size=14,
                      ),
                      xaxis=dict(tickangle=45))

    # Generate the dates for each Monday
    mondays, mondays_str = get_mondays(ilvl)
    fig.update_xaxes(tickvals=mondays, ticktext=mondays_str)

    return fig

def multiple_item_levels_single_chart(ilvl: pd.DataFrame, post_ilvl: bool = False, events: Iterable[str]=None) -> go.Figure:

    ilvl = remove_empty_columns(ilvl, keep_zeros=False)

    non_item_types, item_types = split_instance_and_variable_entries(set(ilvl.columns))

    ilvl = ilvl.melt(id_vars=non_item_types, var_name=TERM_ITEM_TYPES, value_name=TERM_ITEM_LEVELS)

    # format timestamps and sort data
    ilvl.loc[:, TERM_TIME] = pd.to_datetime(ilvl[TERM_TIME])
    ilvl = ilvl.sort_values(by=[TERM_TIME], ascending=True)

    # Generate the dates for each Monday
    mondays, mondays_str = get_mondays(ilvl)

    if post_ilvl:
        line_shape = "hv"
    else:
        line_shape = "vh"

    default_line_dash_sequence = ['solid', 'dot', 'dash', 'dashdot', 'longdash', 'longdashdot']

    # Create the step chart
    fig_ilvls = px.line(ilvl, x=TERM_TIME, y=TERM_ITEM_LEVELS, color=TERM_ITEM_TYPES,
                        line_shape=line_shape,
                        line_dash=TERM_COLLECTION,
                        line_dash_sequence=default_line_dash_sequence,
                        color_discrete_sequence=CHART_COLOURS)

    unique_collections = ilvl[TERM_COLLECTION].unique()
    first_collection = unique_collections[0]

    for trace in fig_ilvls.data:
        collection = trace.name.split(', ')[1]
        trace.name = trace.name.split(', ')[0]
        trace.legendgroup = trace.name
        if collection == first_collection:
            pass
        else:
            trace.showlegend = False

    if len(unique_collections) > 1:

        # Dummy traces for unique patterns
        for i, pattern in enumerate(unique_collections):
            fig_ilvls.add_trace(go.Scatter(
                x=[None], y=[None],
                line=dict(dash=default_line_dash_sequence[i % len(default_line_dash_sequence)], color="black"),
                mode="lines",
                name=pattern,
                showlegend=True
            ))

    else:
        pass

    if events is not None and len(events) > 0:

        fig = sp.make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.02, row_heights=[1, 3])

        for trace in fig_ilvls.data:
            fig.add_trace(trace, row=2, col=1)

        fig.update_yaxes(title_text='Item Level', row=2, col=1)

        event_ilvls = ilvl.loc[ilvl[TERM_EVENT].isin(events), :]
        activities = event_ilvls[TERM_ACTIVITY].unique()
        for activity in activities:
            activity_data = event_ilvls.loc[event_ilvls[TERM_ACTIVITY] == activity, :]
            fig.add_trace(go.Scatter(x=activity_data[TERM_TIME],
                                     y=activity_data[TERM_ACTIVITY],
                                     mode='markers',
                                     name=activity,
                                     showlegend=False,
                                     marker=dict(color=CHART_COLOURS[2])),
                          row=1, col=1)

    else:
        fig = fig_ilvls
        fig.update_layout(yaxis_title='Item Level')

    # Set the title and labels
    fig.update_layout(
        xaxis=dict(tickangle=45),
        title=None,
        font=dict(
            size=14,
        ),
        legend=dict(
            orientation="h",
            y=1.01,
            xanchor="left",
            x=0,
            font=dict(
                size=12,
            ),
            yanchor="bottom",
            title=TERM_ITEM_TYPES + ", Collection Points",
        ),
        )
    fig.update_xaxes(title_text=f"Time", row=2, col=1)

    # Update the x-axis tick values and labels
    fig.update_xaxes(tickvals=mondays, ticktext=mondays_str)

    return fig

def item_level_development_activity_executions(ilvl: pd.DataFrame, events: Iterable[str] = None, cps: Iterable[str] = None,
                                               item_types: Iterable[str]=None, post_ilvl: bool = False, joint_display: bool = False) -> go.Figure:

    non_item_types, item_type_cols = split_instance_and_variable_entries(set(ilvl.columns))

    if cps:
        if cps == TERM_ALL:
            cps = set(ilvl[TERM_COLLECTION])
        elif isinstance(cps, str):
            cps = {cps}
        elif isinstance(cps, set):
            pass
        elif isinstance(cps, Iterable):
            cps = set(cps)
        else:
            raise ValueError("Collection points must be a string or an iterable of strings.")

        if len(cps) == 0:
            return plotly.graph_objects.Figure()
        else:
            pass
    else:
        cps = set(ilvl[TERM_COLLECTION])

    if item_types:

        if item_types == TERM_ALL:
            item_types = set(item_type_cols)
        elif isinstance(item_types, str):
            item_types = {item_types}
        elif isinstance(item_types, set):
            pass
        elif isinstance(item_types, Iterable):
            item_types = set(item_types)
        else:
            raise ValueError("Item types must be a string or an iterable of strings.")

        if len(item_types) == 0:
            return plotly.graph_objects.Figure()
        else:
            pass

        item_types = item_types.intersection(set(item_type_cols))

    else:
        item_types = set(item_type_cols)


    if events is not None and len(events) > 0:
        if isinstance(events, str):
            events = [events]
        elif isinstance(events, list):
            pass
        elif isinstance(events, Iterable):
            events = list(events)
        else:
            raise ValueError("Activities must be a string or an iterable of strings.")

        if set(events).issubset(ilvl[TERM_EVENT]):
            pass
        else:
            raise ValueError("Events must be a subset of the events in the data.")

        if set(events) == set(ilvl.loc[:, TERM_EVENT]):
            events = []
        else:
            pass
    else:
        events = []

    if post_ilvl:
        line_shape = "hv"
    else:
        line_shape = "vh"

    ilvls_to_drop = list(set(item_type_cols).difference(item_types))
    ilvl_filtered = ilvl.drop(columns=ilvls_to_drop)

    ilvl_filtered.loc[:, TERM_TIME] = pd.to_datetime(ilvl_filtered[TERM_TIME])
    ilvl_filtered = ilvl_filtered.sort_values(by=[TERM_TIME], ascending=True)

    if joint_display:
        return multiple_item_levels_single_chart(ilvl=ilvl_filtered, post_ilvl=post_ilvl, events=events)
    else:
        pass

    if len(events) > 0:
        number_sub_plots = len(cps) + 1
        specs = [1] + [3 for _ in range(number_sub_plots - 1)]
    else:
        number_sub_plots = len(cps)
        specs = [3 for _ in range(number_sub_plots)]

    # format timestamps and sort data
    ilvl_filtered.loc[:, TERM_TIME] = pd.to_datetime(ilvl_filtered[TERM_TIME])
    ilvl_filtered = ilvl_filtered.sort_values(by=[TERM_TIME], ascending=True)

    if number_sub_plots > 1:
        pass
    else:
        return item_level_development_single_cp(ilvl=ilvl_filtered, cp=cps.pop(), post_ilvl=post_ilvl)

    fig = sp.make_subplots(rows=number_sub_plots, cols=1, shared_xaxes=True, vertical_spacing=0.02, row_heights=specs)

    ilvl_filtered = ilvl_filtered.melt(id_vars=non_item_types, var_name=TERM_ITEM_TYPES, value_name=TERM_ITEM_LEVELS)

    item_type_colours = dict()
    for i, cp in enumerate(cps):
        if isinstance(cp, str):
            pass
        else:
            raise ValueError("Collection points must be strings.")

        if len(events) > 0:
            fig_number = i + 2
        else:
            fig_number = i + 1

        ilvl_cp = ilvl_filtered.loc[ilvl_filtered[TERM_COLLECTION] == cp, :]

        for item_type in ilvl_cp[TERM_ITEM_TYPES].unique():

            if item_type in item_type_colours.keys():
                colour = item_type_colours[item_type]
                show_legend = False
            else:
                colour = CHART_COLOURS[len(item_type_colours) % len(CHART_COLOURS)]
                item_type_colours[item_type] = colour
                show_legend = True

            fig.add_trace(go.Scatter(x=ilvl_cp.loc[ilvl_cp[TERM_ITEM_TYPES] == item_type, TERM_TIME],
                                     y=ilvl_cp.loc[ilvl_cp[TERM_ITEM_TYPES] == item_type, TERM_ITEM_LEVELS],
                                     name=item_type, mode="lines", line=dict(shape=line_shape, color=colour),
                                     showlegend=show_legend, legendgroup=item_type), row=fig_number, col=1)

            fig.update_yaxes(title_text=f"{cp}", row=fig_number, col=1)

    if len(events) > 0:
        event_ilvls = ilvl_filtered.loc[ilvl_filtered[TERM_EVENT].isin(events), :]
        activities = event_ilvls[TERM_ACTIVITY].unique()
        for activity in activities:
            activity_data = event_ilvls.loc[event_ilvls[TERM_ACTIVITY] == activity, :]
            fig.add_trace(go.Scatter(x=activity_data[TERM_TIME],
                                     y=activity_data[TERM_ACTIVITY],
                                     mode='markers',
                                     name=activity,
                                     showlegend=False,
                                     marker=dict(color=CHART_COLOURS[2])),
                          row=1, col=1)
    else:
        pass
    # Set the title and labels
    fig.update_layout(xaxis=dict(tickangle=45),
                      title=None,
    font = dict(
        size=14,
    ),
                      legend=dict(
                          orientation="h",
                          font=dict(
                              size=12,
                          ),
                          y=1.01,
                          xanchor="left",
                          x=0,
                          yanchor="bottom",
                          title=None,
                      ),
                      )
    # Generate the dates for each Monday
    mondays, mondays_str = get_mondays(ilvl)
    fig.update_xaxes(tickvals=mondays, ticktext=mondays_str)
    fig.update_xaxes(title_text=f"Time", row=number_sub_plots, col=1)

    fig.update_layout(height=700,
                      title=None
    )

    return fig

def plot_activity_distribution(data: pd.DataFrame):
    """
    Pass event data and plot the distribution of the activities of the involved events.
    :param data: Dataframe with columns 'event' and 'activity'
    :return: Plotly figure Pi Chart showing activities
    """

    if not {TERM_EVENT, TERM_ACTIVITY}.issubset(data.columns):
        raise ValueError(f"DataFrame must contain columns '{TERM_EVENT}' and '{TERM_ACTIVITY}'")
    else:
        pass

    # group by event and activity
    events = data.loc[:, [TERM_EVENT, TERM_ACTIVITY]].drop_duplicates()

    # count the number of events for each activity
    event_counts = events[TERM_ACTIVITY].value_counts().reset_index()
    event_counts.columns = [TERM_ACTIVITY, TERM_EVENTS]

    # wierd dash plotly bug - no other solution found, this seems consensus of 'the internet'
    try:
        fig = px.pie(event_counts, names=TERM_ACTIVITY, values=TERM_EVENTS,
                     color_discrete_sequence=CHART_COLOURS)
    except:
        fig = px.pie(event_counts, names=TERM_ACTIVITY, values=TERM_EVENTS,
                     color_discrete_sequence=CHART_COLOURS)



    return fig


def plot_involved_objects_per_type(data: pd.DataFrame):
    """
    Pass e2o data and plot the distribution of the object types of the involved objects.
    :param data: Dataframe with columns 'object' and 'object type'
    :return: Plotly figure Pi Chart showing object distribution
    """

    if not {TERM_OBJECT, TERM_OBJECT_TYPE}.issubset(data.columns):
        raise ValueError(f"DataFrame must contain columns '{TERM_OBJECT}' and '{TERM_OBJECT_TYPE}'")
    else:
        pass

    objects = data.loc[:, [TERM_OBJECT, TERM_OBJECT_TYPE]].drop_duplicates()

    # count the number of events for each activity
    object_counts = objects[TERM_OBJECT_TYPE].value_counts().reset_index()
    object_counts.columns = [TERM_OBJECT_TYPE, TERM_OBJECT]

    # plot the distribution of activities
    fig = px.pie(object_counts, names=TERM_OBJECT_TYPE, values=TERM_OBJECT,
                 color_discrete_sequence=CHART_COLOURS)


    return fig


def plot_number_of_involved_objects(e2o: pd.DataFrame, events: pd.DataFrame):
    """
    Pass e2o data and get the number of objects involved in each event.
    :param data: e2o dataframe
    :return: Plotly Histogram showing the number of objects involved in each event
    """
    object_counts = get_total_count_of_objects(e2o)
    events = events.loc[:, [TERM_EVENT, TERM_ACTIVITY]].drop_duplicates()

    enhanced_e2o = events.merge(object_counts, on=TERM_EVENT, how='left')

    # wierd dash plotly bug - no other solution found, this seems consensus of 'the internet'
    try:
        fig = px.histogram(enhanced_e2o, x=TERM_OBJECT_COUNT, color=TERM_ACTIVITY, color_discrete_sequence=CHART_COLOURS)
    except:
        fig = px.histogram(enhanced_e2o, x=TERM_OBJECT_COUNT, color=TERM_ACTIVITY,
                           color_discrete_sequence=CHART_COLOURS)

    fig.update_layout(
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.1,
            xanchor="left",
            x=0,
            font=dict(
                size=10,
            )
        )
    )

    return fig


def plot_objects_per_object_type_in_events(e2o: pd.DataFrame):
    """
    Pass e2o data and get the number of objects involved in each event.
    :param data: e2o dataframe
    :return: Plotly Sunburst showing the number of objects involved in each event
    """

    object_counts = event_object_type_count(e2o)

    # Melt the DataFrame to have one row per event-object type pair
    data_melted = object_counts.melt(id_vars=TERM_EVENT, var_name=TERM_OBJECT_TYPE, value_name=TERM_OBJECT_TYPE_COUNT)

    # wierd dash plotly bug - no other solution found, this seems consensus of 'the internet'
    try:
        fig = px.sunburst(data_melted, path=[TERM_OBJECT_TYPE, TERM_OBJECT_TYPE_COUNT],
                          color_discrete_sequence=CHART_COLOURS)
    except:
        fig = px.sunburst(data_melted, path=[TERM_OBJECT_TYPE, TERM_OBJECT_TYPE_COUNT],
                          color_discrete_sequence=CHART_COLOURS)

    return fig


def plot_activity_executions_for_object_of_object_type(e2o: pd.DataFrame, events: pd.DataFrame, object_type: str):
    """
    Pass e2o data and get the number of objects involved in each event.
    :param data: e2o dataframe
    :return: Plotly Sunburst showing the number of objects involved in each event
    """

# try:
    if object_type not in e2o[TERM_OBJECT_TYPE].unique():
        return plotly.graph_objects.Figure()
    else:
        pass

    object_executions = get_execution_number(e2o, events, object_type=object_type)
    object_executions = object_executions.dropna(subset=[TERM_EXECUTION_COUNT])
    chart_data = object_executions.groupby([TERM_ACTIVITY, TERM_EXECUTION_COUNT]).size().reset_index(name=TERM_COUNT)
    chart_data[TERM_EXECUTION_COUNT] = chart_data[TERM_EXECUTION_COUNT].astype(str)

    fig = px.bar(chart_data, x=TERM_ACTIVITY, y=TERM_COUNT, color=TERM_EXECUTION_COUNT, color_discrete_sequence=CHART_COLOURS)

    fig.update_layout(
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.01,
            xanchor="left",
            font=dict(
                size=10,
            )
        )
    )
# except:
#     fig = plotly.graph_objects.Figure()

    return fig

def show_active_events(qop: pd.DataFrame):

    qop_active = get_active_instances(qop)
    active_events = qop_active[TERM_EVENT].unique()

    qop_data = qop.loc[:,[TERM_EVENT, TERM_ACTIVITY]].drop_duplicates()

    qop_data.loc[qop_data[TERM_EVENT].isin(active_events), TERM_ACTIVE] = TERM_ACTIVE

    qop_data[TERM_ACTIVE] = qop_data[TERM_ACTIVE].replace(np.nan, TERM_INACTIVE)

    fig = px.sunburst(qop_data, path=[TERM_ACTIVE, TERM_ACTIVITY], color_discrete_sequence=CHART_COLOURS)

    return fig

def truncate_label(label):
    # Split the label into individual values
    values = label.split(', ')

    result = []

    for value in values:
        words = value.split()  # Split the string into words
        truncated_words = [word[:2].capitalize() for word in words]  # Get the first two letters and capitalize
        result.append(''.join(truncated_words))  # Join the words back together

    # Join full label
    return ', '.join(result)


def show_active_collection_point_combinations(qop: pd.DataFrame):
    qop_new = qop.copy()
    qop_new[QOP_ID] = qop_new[TERM_EVENT] + ":" + qop_new[TERM_COLLECTION]

    # mark active qops
    qop_enhanced = get_active_instances(qop_new)
    qop_new.loc[qop_new[QOP_ID].isin(qop_enhanced[QOP_ID]), TERM_ACTIVE] = TERM_ACTIVE
    qop_new[TERM_ACTIVE] = qop_new[TERM_ACTIVE].replace("nan", TERM_INACTIVE)

    # mark active events as such
    cp_active = qop_new.loc[:, [TERM_EVENT, TERM_ACTIVITY, TERM_COLLECTION, TERM_ACTIVE]]

    # change shape
    cp_active = cp_active.pivot(index=[TERM_EVENT, TERM_ACTIVITY], columns=TERM_COLLECTION, values=TERM_ACTIVE)
    cp_active[TERM_CP_ACTIVE] = cp_active.apply(
        lambda row: ', '.join([f'{col}' for col in cp_active.columns if row[col] == "active"]), axis=1)

    cp_active[TERM_CP_ACTIVE] = cp_active[TERM_CP_ACTIVE].replace("", TERM_INACTIVE)

    # get numbers for chart
    cp_active_combinations = cp_active.groupby([TERM_ACTIVITY, TERM_CP_ACTIVE]).size().reset_index(name=EVENT_COUNT)

    cp_active_combinations["Collection Points (abbrev.)"] = cp_active_combinations[TERM_CP_ACTIVE].apply(truncate_label)

    # wierd dash plotly bug - no other solution found, this seems consensus of 'the internet'
    try:
        fig = px.bar(cp_active_combinations, x=EVENT_COUNT, y="Collection Points (abbrev.)", color=TERM_ACTIVITY,
                 orientation='h',
                 hover_data=[TERM_CP_ACTIVE, TERM_ACTIVITY, EVENT_COUNT],
                 color_discrete_sequence=CHART_COLOURS)
    except:
        fig = px.bar(cp_active_combinations, x=EVENT_COUNT, y="Collection Points (abbrev.)", color=TERM_ACTIVITY,
                     orientation='h',
                     hover_data=[TERM_CP_ACTIVE, TERM_ACTIVITY, EVENT_COUNT],
                     color_discrete_sequence=CHART_COLOURS)

    fig.update_layout(
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.7,
            xanchor="left",
            x=-0.3,
            font=dict(
                size=10,
            )
        )
    )
    fig.update_layout(xaxis_title='Number of Events')

    return fig

def objects_activity_execution_frequency(e2o: pd.DataFrame, events: pd.DataFrame, object_type: str):
    """
    Pass e2o data and get the number of objects involved in each event.
    :param data: e2o dataframe
    :return: Plotly Sunburst showing the number of objects involved in each event
    """

    if object_type not in e2o[TERM_OBJECT_TYPE].unique():
        return plotly.graph_objects.Figure()
    else:
        pass

    extended_e2o = e2o.merge(events[[TERM_EVENT, TERM_ACTIVITY]], on=TERM_EVENT, how="left")
    e2o_filtered = extended_e2o.loc[extended_e2o[TERM_OBJECT_TYPE] == object_type, :]
    object_executions = e2o_filtered.groupby([TERM_OBJECT, TERM_ACTIVITY]).size().reset_index(name=TERM_EXECUTION_COUNT)

    fig = px.sunburst(object_executions, path=[TERM_ACTIVITY, TERM_EXECUTION_COUNT], color=TERM_ACTIVITY,
                      color_discrete_sequence=CHART_COLOURS)


    return fig


def show_active_collection_point_distribution_event(qop: pd.DataFrame):

    active_qop = get_active_instances(qop)

    active_qop = active_qop.loc[:, [TERM_EVENT, TERM_ACTIVITY, TERM_COLLECTION]]
    counts = active_qop.groupby([TERM_COLLECTION, TERM_ACTIVITY]).size().reset_index(name=TERM_CP_ACTIVE)

    # wierd dash plotly bug - no other solution found, this seems consensus of 'the internet'
    try:
        fig = px.bar(counts, x=TERM_CP_ACTIVE, y=TERM_COLLECTION, color=TERM_ACTIVITY,
                     orientation='h', color_discrete_sequence=CHART_COLOURS)
    except:
        fig = px.bar(counts, x=TERM_CP_ACTIVE, y=TERM_COLLECTION, color=TERM_ACTIVITY,
                     orientation='h', color_discrete_sequence=CHART_COLOURS)

    fig.update_layout(
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.01,
            xanchor="left",
            x=0,
            font=dict(
                size=10,
            )
        )
    )

    return fig

def show_object_type_combination_for_events(events: pd.DataFrame, e2o: pd.DataFrame):

    object_count = event_object_type_count(e2o)
    object_count = object_count.set_index(TERM_EVENT)
    object_count[TERM_OBJECT_TYPE_COMBINATION] = object_count.apply(
        lambda row: ', '.join([f'{col}' for col in object_count.columns if row[col] == True]), axis=1)
    object_count = object_count.merge(events[[TERM_EVENT, TERM_ACTIVITY]], on=TERM_EVENT, how="left")
    object_combinations = object_count.groupby([TERM_OBJECT_TYPE_COMBINATION, TERM_ACTIVITY]).size().reset_index(
        name=TERM_OBJECT_TYPE_COMBINATION_FREQUENCY)

    object_combinations["Object Types (abbrev.)"] = object_combinations[TERM_OBJECT_TYPE_COMBINATION].apply(truncate_label)

    # wierd dash plotly bug - no other solution found, this seems consensus of 'the internet'
    try:
        fig = px.bar(object_combinations, x=TERM_OBJECT_TYPE_COMBINATION_FREQUENCY, y="Object Types (abbrev.)",
                     color=TERM_ACTIVITY, orientation='h',
                     hover_data=[TERM_OBJECT_TYPE_COMBINATION, TERM_ACTIVITY, TERM_OBJECT_TYPE_COMBINATION_FREQUENCY],
                     color_discrete_sequence=CHART_COLOURS)
    except:
        fig = px.bar(object_combinations, x=TERM_OBJECT_TYPE_COMBINATION_FREQUENCY, y="Object Types (abbrev.)",
                     color=TERM_ACTIVITY, orientation='h',
                     hover_data=[TERM_OBJECT_TYPE_COMBINATION, TERM_ACTIVITY, TERM_OBJECT_TYPE_COMBINATION_FREQUENCY],
                     color_discrete_sequence=CHART_COLOURS)

    fig.update_layout(
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.01,
            xanchor="left",
            x=0,
            font=dict(
                size=10,
            )
        )
    )

    return fig


def show_active_item_type_combinations_and_frequencies_per_event(qop: pd.DataFrame):
    non_item_type, item_types = split_instance_and_variable_entries(set(qop.columns))

    it_active = qop.loc[:, [TERM_EVENT] + item_types]
    it_active = it_active.groupby(TERM_EVENT).any()
    it_active[TERM_ITEM_TYPE_ACTIVE] = it_active[item_types].apply(
        lambda row: ', '.join([f'{col}' for col in it_active.columns if row[col] == True]), axis=1)

    it_active[TERM_ITEM_TYPE_ACTIVE] = it_active[TERM_ITEM_TYPE_ACTIVE].replace("", TERM_INACTIVE)

    # get numbers for chart
    it_active_combinations = it_active.merge(qop[[TERM_EVENT, TERM_ACTIVITY]].drop_duplicates(), on=TERM_EVENT, how="left")
    it_active_combinations = it_active_combinations.groupby([TERM_ACTIVITY, TERM_ITEM_TYPE_ACTIVE]).size().reset_index(
        name=EVENT_COUNT)

    it_active_combinations["Item types (abbrev.)"] = it_active_combinations[TERM_ITEM_TYPE_ACTIVE].apply(truncate_label)

    fig = px.bar(it_active_combinations, x=EVENT_COUNT, y="Item types (abbrev.)", color=TERM_ACTIVITY, orientation='h',
                 hover_data=[TERM_ITEM_TYPE_ACTIVE, TERM_ACTIVITY, EVENT_COUNT], color_discrete_sequence=CHART_COLOURS)

    fig.update_layout(
        legend=dict(
            orientation="h",
            yanchor="top",
            y=-0.2,
            xanchor="left",
            x=-0.2,
            title=None,
            font=dict(
                size=10,
            )
        )
    )
    fig.update_layout(xaxis_title='Number of Events')

    return fig


def show_active_item_type_combinations_and_frequencies_qop(qop: pd.DataFrame, cp: str = None):

    if cp:
        qop = qop.loc[qop[TERM_COLLECTION] == cp, :]
    else:
        pass

    qop = qop.fillna(0)

    non_item_type, item_types = split_instance_and_variable_entries(set(qop.columns))
    it_active = qop.copy()
    it_active[TERM_ITEM_TYPE_ACTIVE] = it_active[item_types].apply(
        lambda row: ', '.join([f'{col}' for col in it_active[item_types].columns if row[col] != 0]), axis=1)

    it_active[TERM_ITEM_TYPE_ACTIVE] = it_active[TERM_ITEM_TYPE_ACTIVE].replace("", TERM_INACTIVE)

    # get numbers for chart
    it_active_combinations = it_active.groupby([TERM_ACTIVITY, TERM_ITEM_TYPE_ACTIVE]).size().reset_index(
        name=QOP_COUNT)

    it_active_combinations["Item types (abbrev.)"] = it_active_combinations[TERM_ITEM_TYPE_ACTIVE].apply(truncate_label)

    fig = px.bar(it_active_combinations, x=QOP_COUNT, y="Item types (abbrev.)", color=TERM_ACTIVITY, orientation='h',
                 hover_data=[TERM_ITEM_TYPE_ACTIVE, TERM_ACTIVITY, QOP_COUNT], color_discrete_sequence=CHART_COLOURS)

    fig.update_layout(
        legend=dict(
            orientation="h",
            yanchor="top",
            y=-0.2,
            xanchor="left",
            x=-0.2,
            title=None,
            font=dict(
                size=10,
            )
        )
    )
    fig.update_layout(xaxis_title='Number of Quantity Operations')
    return fig


def show_active_item_type_distribution_per_qop(qop: pd.DataFrame, cp: str = None):

    if cp:
        qop = qop.loc[qop[TERM_COLLECTION] == cp, :]
    else:
        pass

    qop = qop.fillna(0)

    non_item_type, item_types = split_instance_and_variable_entries(set(qop.columns))

    it_active = qop.melt(id_vars=non_item_type, value_vars=item_types, var_name=TERM_ITEM_TYPES, value_name=TERM_VALUE)

    it_active.loc[it_active[TERM_VALUE] == 0, TERM_ITEM_TYPES] = TERM_INACTIVE

    it_active = it_active[[TERM_EVENT, TERM_COLLECTION, TERM_ITEM_TYPES, TERM_VALUE]].groupby(
        [TERM_EVENT, TERM_ITEM_TYPES, TERM_COLLECTION]).any()
    it_active = it_active.reset_index()
    it_active = it_active.merge(qop[[TERM_EVENT, TERM_ACTIVITY]].drop_duplicates(), on=TERM_EVENT, how="left")

    counts = it_active.groupby([TERM_ITEM_TYPES, TERM_ACTIVITY, TERM_COLLECTION]).size().reset_index(
        name=TERM_ITEM_TYPE_ACTIVE)

    fig = px.bar(counts, x=TERM_ITEM_TYPE_ACTIVE, y=TERM_ITEM_TYPES, color=TERM_ACTIVITY, pattern_shape=TERM_COLLECTION,
                 orientation="h", color_discrete_sequence=CHART_COLOURS,
                 hover_data=[TERM_ACTIVITY, TERM_COLLECTION, TERM_ITEM_TYPE_ACTIVE])

    unique_collections = counts[TERM_COLLECTION].unique()
    first_collection = unique_collections[0]

    for trace in fig.data:
        collection = trace.name.split(', ')[1]
        trace.name = trace.name.split(', ')[0]
        trace.legendgroup = trace.name
        if collection == first_collection:
            pass
        else:
            trace.showlegend = False

    # Update the existing traces to not show in legend
    if len(unique_collections) > 1:

        # Dummy traces for unique patterns
        default_patterns = ['', '/', '\\', 'x', '-', '|', '+', '.']
        for i, pattern in enumerate(unique_collections):
            fig.add_trace(go.Bar(
                x=[None], y=[None],
                marker=dict(color="black", pattern_shape=default_patterns[i % len(default_patterns)]),
                name=pattern,
                showlegend=True,
                orientation='h'
            ))

    else:
        pass

    fig.update_layout(
        legend=dict(
            orientation="h",
            font=dict(
                size=10,
            ),
            yanchor="top",
            y=-0.2,
            xanchor="left",
            x=-0.1,
            title=None,
        ),
        xaxis_title="Number of Quantity Operations"
    )

    return fig


def show_active_item_type_distribution_per_event(qop: pd.DataFrame):
    non_item_type, item_types = split_instance_and_variable_entries(set(qop.columns))

    if len(item_types) > 20:
        item_types = item_types[:20]
    else:
        pass

    it_active = qop.melt(id_vars=non_item_type, value_vars=item_types, var_name=TERM_ITEM_TYPES, value_name=TERM_VALUE)

    it_active.loc[it_active[TERM_VALUE] == 0, TERM_ITEM_TYPES] = TERM_INACTIVE

    it_active = it_active[[TERM_EVENT, TERM_ITEM_TYPES, TERM_VALUE]].groupby([TERM_EVENT, TERM_ITEM_TYPES]).any()
    it_active = it_active.reset_index()
    it_active = it_active.merge(qop[[TERM_EVENT, TERM_ACTIVITY]].drop_duplicates(), on=TERM_EVENT, how="left")
    # it_active = it_active.reset_index()
    #
    counts = it_active.groupby([TERM_ITEM_TYPES, TERM_ACTIVITY]).size().reset_index(name=TERM_ITEM_TYPE_ACTIVE)
    #
    fig = px.bar(counts, x=TERM_ITEM_TYPE_ACTIVE, y=TERM_ITEM_TYPES, color=TERM_ACTIVITY, orientation="h",
                 color_discrete_sequence=CHART_COLOURS)

    fig.update_layout(
        legend=dict(
            orientation="h",
            yanchor="top",
            y=-0.2,
            xanchor="left",
            x=-0.1,
            font=dict(
                size=10,
            )
        )
    )
    fig.update_layout(xaxis_title='Number of Events')

    return fig

def show_active_qops(qop: pd.DataFrame):
    qop = qop.fillna(0)
    qop_enhanced = get_enhanced_quantity_instances(qop)

    fig = px.sunburst(qop_enhanced, path=[TERM_ACTIVITY, TERM_ACTIVE, TERM_COLLECTION], color_discrete_sequence=CHART_COLOURS)

    return fig


def show_instance_directions(qop: pd.DataFrame):
    qop_enhanced = get_direction_quantity_instances(qop)

    fig = px.sunburst(qop_enhanced, path=[TERM_DIRECTION, TERM_ACTIVITY, TERM_COLLECTION], color_discrete_sequence=CHART_COLOURS)

    return fig


def boxplots_of_distribution(data: pd.DataFrame, view: str = None, display_points: bool = False) -> go.Figure:

    if view in [TERM_ITEM_TYPES, TERM_COLLECTION, TERM_ACTIVITY]:
        pass
    else:
        raise ValueError("View must be one of 'item_types', 'collections', or 'activity'.")

    filtered_data = remove_empty_columns(data)

    non_item_types, item_types = split_instance_and_variable_entries(set(filtered_data.columns))

    if TERM_ITEM_TYPES in filtered_data.columns:
        data_melted = filtered_data
    else:
        data_melted = filtered_data.melt(id_vars=non_item_types, var_name=TERM_ITEM_TYPES, value_name=TERM_VALUE)

    if display_points:
        points = "all"
    else:
        points = "outliers"

    if view == TERM_ITEM_TYPES:
        fig = px.box(data_melted, x=TERM_ITEM_TYPES, y=TERM_VALUE, color=TERM_ITEM_TYPES, color_discrete_sequence=CHART_COLOURS, points=points)
    elif view == TERM_COLLECTION:
        fig = px.box(data_melted, x=TERM_COLLECTION, y=TERM_VALUE, color=TERM_COLLECTION, color_discrete_sequence=CHART_COLOURS, points=points)
    else:
        fig = px.box(data_melted, x=TERM_ACTIVITY, y=TERM_VALUE, color=TERM_ACTIVITY, color_discrete_sequence=CHART_COLOURS, points=points)

    if display_points:
        for trace in fig.data:
            trace.jitter = 0.3
    else:
        pass

    fig.update_layout(showlegend=False)

    return fig

# def boxplots_of_qstate_distribution(data: pd.DataFrame, view: str = None) -> go.Figure:
#
#     if view in [TERM_ITEM_TYPES, TERM_COLLECTION, TERM_ACTIVITY]:
#         pass
#     else:
#         raise ValueError("View must be one of 'item_types', 'collections', or 'activity'.")
#
#     filtered_data = remove_empty_columns(data)
#
#     non_item_types, item_types = get_column_separation(set(filtered_data.columns))
#
#     if TERM_ITEM_TYPES in filtered_data.columns:
#         data_melted = filtered_data
#     else:
#         data_melted = filtered_data.melt(id_vars=non_item_types, var_name=TERM_ITEM_TYPES, value_name=TERM_VALUE)
#
#     if view == TERM_ITEM_TYPES:
#         fig = px.box(data_melted, x=TERM_ITEM_TYPES, y=TERM_VALUE, color=TERM_ITEM_TYPES, color_discrete_sequence=CHART_COLOURS)
#     elif view == TERM_ACTIVITY:
#         fig = px.box(data_melted, x=TERM_ACTIVITY, y=TERM_VALUE, color=TERM_ACTIVITY, color_discrete_sequence=CHART_COLOURS)
#     else:
#         fig = go.Figure()
#         for i, cp in enumerate(filtered_data[TERM_COLLECTION].unique()):
#             df = data.loc[data[TERM_COLLECTION] == cp]
#             df = remove_empty_columns(df, keep_zeros=False)
#             df = df.melt(id_vars=non_item_types, var_name=TERM_ITEM_TYPES, value_name=TERM_VALUE)
#             df = df.reset_index()
#             fig.add_trace(go.Box(y=df[TERM_VALUE], marker_color=CHART_COLOURS[i], boxmean=True, name=cp))
#
#     fig.update_layout(legend=dict(
#         orientation="h",
#         yanchor="bottom",
#         y=1.01,
#         x=0,
#         xanchor="left",
#         font=dict(
#             size=10,
#         ),
#         title=""
#     )
#     )
#
#     return fig

def boxplots_per_item_level(data: pd.DataFrame, title: str = None) -> go.Figure:

    non_item_types, item_types = split_instance_and_variable_entries(set(data.columns))

    data = remove_empty_columns(data)

    data_melted = data.melt(id_vars=non_item_types, var_name=TERM_ITEM_TYPES, value_name=TERM_ITEM_QUANTITY)

    fig = px.box(data_melted, x=TERM_ITEM_TYPES, y=TERM_ITEM_QUANTITY, color=TERM_ITEM_TYPES, color_discrete_sequence=CHART_COLOURS)

    if title:
        pass
    else:
        title = "Distribution per Item Type"
    fig.update_layout(legend=dict(
        orientation="h",
        yanchor="bottom",
        xanchor="left",
        font=dict(
            size=10,
        ),
        title=title
    )
    )

    return fig

def histogram_distribution_quantity_changes(data: pd.DataFrame, view: str = None) -> go.Figure:

    if view in [TERM_ITEM_TYPES, TERM_COLLECTION, TERM_ACTIVITY]:
        pass
    else:
        raise ValueError("View must be one of 'item_types', 'collections', or 'activity'.")

    filtered_data = remove_empty_columns(data)

    non_item_types, item_types = split_instance_and_variable_entries(set(filtered_data.columns))

    if TERM_ITEM_TYPES in filtered_data.columns:
        data_melted = filtered_data
    else:
        data_melted = filtered_data.melt(id_vars=non_item_types, var_name=TERM_ITEM_TYPES, value_name=TERM_VALUE)

    if view == TERM_ITEM_TYPES:
        fig = px.histogram(data_melted, x=TERM_VALUE, color=TERM_ITEM_TYPES, color_discrete_sequence=CHART_COLOURS,
                           barmode='overlay')
    elif view == TERM_COLLECTION:
        fig = px.histogram(data_melted, x=TERM_VALUE, color=TERM_COLLECTION, color_discrete_sequence=CHART_COLOURS,
                           barmode='overlay')
    else:
        fig = px.histogram(data_melted, x=TERM_VALUE, color=TERM_ACTIVITY, color_discrete_sequence=CHART_COLOURS,
                           barmode='overlay')

    return fig

def boxplots_for_single_columns(data: pd.DataFrame, column_names: Iterable, title: str = None, y_axis: str = None) -> go.Figure:

    if isinstance(column_names, str):
        column_names = [column_names]
    elif isinstance(column_names, Iterable):
        column_names = set(column_names)
        if column_names.issubset(set(data.columns)):
            pass
        else:
            raise ValueError("Column names are not in the data.")
        column_names = list(column_names)
    else:
        raise ValueError("Column names must be iterable.")

    fig = go.Figure()

    for i, column_name in enumerate(column_names):
        fig.add_trace(go.Box(y=data[column_name], name=column_name, boxpoints='all', boxmean=True, fillcolor=CHART_COLOURS[i]))

    if title:
        pass
    else:
        title = "Distribution for Selected Data"

    if y_axis:
        pass
    else:
        y_axis = "Values"

    fig.update_layout(title=title,
                      yaxis_title=y_axis)

    return fig


def show_event_attribute_values(events: pd.DataFrame, attribute: str):
    # try:
    if attribute:
        pass
    else:
        return plotly.graph_objects.Figure()


    non_attributes, attributes = split_instance_and_variable_entries(events.columns)
    if attribute in attributes:
        pass
    else:
        return plotly.graph_objects.Figure()

    events = convert_numeric_columns(events)
    events = convert_to_timestamp(events)

    # wierd dash plotly bug - no other solution found, this seems consensus of 'the internet'
    try:
        fig = px.histogram(events, x=attribute, color_discrete_sequence=CHART_COLOURS)
    except:
        fig = px.histogram(events, x=attribute, color_discrete_sequence=CHART_COLOURS)

    return fig


def show_object_attribute_values(objects: pd.DataFrame, attribute: str):
    """ If object attribute value of the same attribute changes, it appears multiple times"""
    # try:
    if attribute:
        pass
    else:
        return plotly.graph_objects.Figure()

    non_attributes, attributes = split_instance_and_variable_entries(objects.columns)
    if attribute in attributes:
        pass
    else:
        return plotly.graph_objects.Figure()

    objects = convert_numeric_columns(objects)
    objects = convert_to_timestamp(objects)

    fig = px.histogram(objects, x=attribute, color=TERM_OBJECT_TYPE, color_discrete_sequence=CHART_COLOURS, histnorm='percent')
    # except:
    #     fig = plotly.graph_objects.Figure()


    return fig


def plot_quantity_data_over_time(qop, start_time, end_time):

    if start_time and end_time:
        pass
    else:
        return plotly.graph_objects.Figure()

    active_qop = get_active_instances(qop)

    active_qop = active_qop.replace(0, np.nan)

    qop_filtered = filter_events_for_time(active_qop, start_time, end_time)

    # sort by time
    qop_filtered.loc[:, TERM_TIME] = pd.to_datetime(qop_filtered[TERM_TIME])
    qop_filtered = qop_filtered.sort_values(by=[TERM_TIME], ascending=True)

    # drop only 0 item types
    non_item_types, item_types = split_instance_and_variable_entries(qop_filtered.columns)

    qop_filtered = qop_filtered.loc[:, [TERM_EVENT, TERM_TIME, TERM_ACTIVITY, TERM_COLLECTION] + list(item_types)]
    qop_melted = qop_filtered.melt(id_vars=[TERM_EVENT, TERM_TIME, TERM_ACTIVITY,TERM_COLLECTION], var_name=TERM_ITEM_TYPES, value_name=TERM_VALUE)
    qop_melted = qop_melted.loc[qop_melted[TERM_VALUE] != 0, :]

    fig = px.bar(qop_melted, x=TERM_TIME, y=TERM_VALUE, color=TERM_ITEM_TYPES,
                 hover_data=[TERM_EVENT, TERM_TIME, TERM_ACTIVITY, TERM_ITEM_TYPES, TERM_VALUE],
                 color_discrete_sequence=CHART_COLOURS)

    fig.update_layout(
        legend=dict(
            orientation="h",
            yanchor="bottom",
            xanchor="right",
            y=1.01,
            x=1,
            font=dict(
                size=10,
            )
        )
    )

    return fig


def collection_point_interaction_overview(qop, collection_point=None, item_type=None):
    if item_type:
        pass
    else:
        return go.Figure()

    non_item_types, item_types = split_instance_and_variable_entries(qop.columns)

    if collection_point:
        qop = qop.loc[qop[TERM_COLLECTION] == collection_point, :]
    else:
        pass

    qop = qop.drop(columns=list(set(item_types) - {item_type}))

    activity_removal = qop[[TERM_ACTIVITY, item_type]].groupby(TERM_ACTIVITY).count()
    activities_to_remove = activity_removal.loc[activity_removal[item_type] == 0, :].index

    qop = qop.loc[~qop[TERM_ACTIVITY].isin(activities_to_remove), :]
    qop = qop.fillna(0)

    fig = px.histogram(qop, x=item_type, color=TERM_ACTIVITY, barmode='overlay',
                       color_discrete_sequence=CHART_COLOURS)

    fig.update_layout(
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.01,
            xanchor="left",
            x=0,
            font=dict(
                size=10,
            ),
            title="Item Type Active Activities"
        ),
        title = f"Quantity updates of {item_type}"
    )

    return fig

def quantity_state_activity_execution_over_time(ilvl):

    # sort by time
    ilvl.loc[:, TERM_TIME] = pd.to_datetime(ilvl[TERM_TIME])
    ilvl = ilvl.sort_values(by=[TERM_TIME], ascending=True)

    # create chart
    ilvl_melted = ilvl.melt(id_vars=[TERM_EVENT, TERM_TIME, TERM_ACTIVITY, TERM_COLLECTION], var_name=TERM_ITEM_TYPES,
                                     value_name=TERM_ITEM_LEVELS)

    fig = px.bar(ilvl_melted, x=TERM_TIME, y=TERM_ITEM_LEVELS, color=TERM_ITEM_TYPES, pattern_shape=TERM_COLLECTION,
                 hover_data=[TERM_EVENT, TERM_TIME, TERM_COLLECTION, TERM_ACTIVITY, TERM_ITEM_LEVELS],
                 color_discrete_sequence=CHART_COLOURS)

    unique_collections = ilvl_melted[TERM_COLLECTION].unique()
    first_collection = unique_collections[0]

    for trace in fig.data:
        collection = trace.name.split(', ')[1]
        trace.name = trace.name.split(', ')[0]
        trace.legendgroup = trace.name
        if collection == first_collection:
            pass
        else:
            trace.showlegend = False

    # Update the existing traces to not show in legend
    if len(unique_collections) > 1:

        # Dummy traces for unique patterns
        default_patterns = ['', '/', '\\', 'x', '-', '|', '+', '.']
        for i, pattern in enumerate(unique_collections):
            fig.add_trace(go.Bar(
                x=[None], y=[None],
                marker=dict(color="black", pattern_shape=default_patterns[i % len(default_patterns)]),
                name=pattern,
                showlegend=True,
                orientation='h'
            ))

    else:
        pass

    fig.update_layout(
        legend=dict(
            orientation="h",
            font=dict(
                size=10,
            ),
            title="",
            y=1.01,
            xanchor="left",
            x=0,
        )
    )

    return fig

def quantity_state_activity_execution_bar_chart(ilvl):

    ilvl = ilvl.drop(columns=[TERM_TIME])
    # ilvl = remove_empty_columns(ilvl, keep_zeros=False)
    # create chart
    ilvl_melted = ilvl.melt(id_vars=[TERM_EVENT, TERM_ACTIVITY, TERM_COLLECTION], var_name=TERM_ITEM_TYPES,
                                     value_name=TERM_ITEM_LEVELS)

    ilvl_melted = ilvl_melted.dropna(subset=[TERM_ITEM_LEVELS])


    fig = px.bar(ilvl_melted, x=TERM_ITEM_LEVELS, y=TERM_EVENT, color=TERM_ITEM_TYPES, pattern_shape=TERM_COLLECTION,
                 hover_data=[TERM_EVENT, TERM_COLLECTION, TERM_ACTIVITY, TERM_ITEM_LEVELS],
                 color_discrete_sequence=CHART_COLOURS,
                 orientation="h")

    unique_collections = ilvl_melted[TERM_COLLECTION].unique()
    first_collection = unique_collections[0]

    for trace in fig.data:
        collection = trace.name.split(', ')[1]
        trace.name = trace.name.split(', ')[0]
        trace.legendgroup = trace.name
        if collection == first_collection:
            pass
        else:
            trace.showlegend = False

    # Update the existing traces to not show in legend
    if len(unique_collections) > 1:

        # Dummy traces for unique patterns
        default_patterns = ['', '/', '\\', 'x', '-', '|', '+', '.']
        for i, pattern in enumerate(unique_collections):
            fig.add_trace(go.Bar(
                x=[None], y=[None],
                marker=dict(color="black", pattern_shape=default_patterns[i % len(default_patterns)]),
                name=pattern,
                showlegend=True,
                orientation='h'
            ))

    else:
        pass

    fig.update_layout(
        legend=dict(
            orientation="h",
            font=dict(
                size=10,
            ),
            title="",
            y=-0.2,
            xanchor="left",
            x=-0.01,
        ),
        yaxis=dict(
            showticklabels=False
        )
    )

    return fig

def quantity_state_activity_execution_histogram(ilvl):

    ilvl = remove_empty_columns(ilvl, keep_zeros=False)

    ilvl_melted = ilvl.melt(id_vars=[TERM_EVENT, TERM_TIME, TERM_ACTIVITY, TERM_COLLECTION], var_name=TERM_ITEM_TYPES,
                                     value_name=TERM_ITEM_LEVELS)

    ilvl_melted = ilvl_melted.dropna(subset=[TERM_ITEM_LEVELS])

    unique = list(ilvl_melted[TERM_ITEM_LEVELS].unique())
    if len(unique) < 21:
        fig = px.histogram(ilvl_melted, x=TERM_ITEM_LEVELS, color=TERM_ITEM_TYPES,
                 hover_data=[TERM_COLLECTION, TERM_ACTIVITY, TERM_ITEM_TYPES, TERM_ITEM_LEVELS],
                 color_discrete_sequence=CHART_COLOURS, barmode='overlay', nbins=len(unique)+2)
    else:
        fig = px.histogram(ilvl_melted, x=TERM_ITEM_LEVELS, color=TERM_ITEM_TYPES,
                 hover_data=[TERM_COLLECTION, TERM_ACTIVITY, TERM_ITEM_TYPES, TERM_ITEM_LEVELS],
                 color_discrete_sequence=CHART_COLOURS, barmode='overlay')


    fig.update_layout(
        legend=dict(
            orientation="h",
            font=dict(
                size=10,
            ),
            title="",
            y=-0.2,
            xanchor="left",
            x=0,
        )
    )

    return fig

def activity_cp_item_type_impact(qop, number_quantity_operations: bool = True):

    # get active quantity updates
    qop = qop.drop(columns=[TERM_TIME, TERM_EVENT])
    qop_qup = create_quantity_updates(qop)
    qop_qup = qop_qup.dropna(subset=[TERM_VALUE])
    qop_qup = qop_qup.loc[qop_qup[TERM_VALUE] != 0, :]

    if number_quantity_operations:
        aggregated_data = qop_qup.groupby(
            [TERM_ITEM_TYPES, TERM_COLLECTION, TERM_ACTIVITY, qop_qup[TERM_VALUE] > 0]).size().reset_index(
            name=TERM_COUNT)
    else: # sum of quantity updates
        aggregated_data = qop_qup.groupby([TERM_ITEM_TYPES, TERM_COLLECTION, TERM_ACTIVITY, qop_qup[TERM_VALUE] > 0]).sum().abs()
        aggregated_data = aggregated_data.rename(columns={TERM_VALUE: TERM_COUNT}).reset_index()

    aggregated_data[TERM_VALUE] = aggregated_data[TERM_VALUE].apply(lambda x: TERM_ADDING if x else TERM_REMOVING)

    # Factorize the categorical data
    aggregated_data['Collection Point Code'], collection_point_uniques = pd.factorize(aggregated_data[TERM_COLLECTION])
    aggregated_data['Item Type Code'], item_type_uniques = pd.factorize(aggregated_data[TERM_ITEM_TYPES])

    # Add jitter
    def add_jitter(value, jitter_amount=0.05):
        return value + np.random.uniform(-jitter_amount, jitter_amount)

    aggregated_data['Jittered Collection Point'] = aggregated_data['Collection Point Code'].apply(
        lambda x: add_jitter(x))
    aggregated_data['Jittered Item Type'] = aggregated_data['Item Type Code'].apply(lambda x: add_jitter(x))

    fig = px.scatter(aggregated_data,
                     x='Jittered Collection Point',
                     y='Jittered Item Type',
                     size=TERM_COUNT,
                     color=TERM_ACTIVITY,
                     symbol=TERM_VALUE,
                     hover_data={TERM_COLLECTION: True, TERM_ITEM_TYPES: True, TERM_ACTIVITY: True, TERM_COUNT: True,
                                 'Jittered Collection Point': False, 'Jittered Item Type': False},
                     color_discrete_sequence=CHART_COLOURS)

    # Update axis labels to reflect the original categories
    fig.update_layout(
        xaxis=dict(
            tickmode='array',
            tickvals=np.arange(len(collection_point_uniques)),
            ticktext=collection_point_uniques,
            title='Collection Point'
        ),
        yaxis=dict(
            tickmode='array',
            tickvals=np.arange(len(item_type_uniques)),
            ticktext=item_type_uniques,
            title='Item Type'
        )
    )

    fig.update_layout(
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.01,
            xanchor="left",
            x=0,
            font=dict(
                size=10,
            ),
            title=""
        )
    )

    fig.update_traces(marker=dict(sizemode='area'))

    return fig

def activities_object_type_involvement(e2o: pd.DataFrame, events: pd.DataFrame, object_type: str) -> go.Figure:

    all_activities = pd.Series(0, index=events[TERM_ACTIVITY].unique())

    # merge data
    extended_e2o = e2o.merge(events[[TERM_EVENT, TERM_ACTIVITY]], on=TERM_EVENT, how="left")

    # filter e2o for objects of passed object type
    extended_e2o = extended_e2o.loc[extended_e2o[TERM_OBJECT_TYPE] == object_type, :]

    # get numbers for chart
    quantified_a2ot = extended_e2o[TERM_ACTIVITY].value_counts()

    all_activities.update(quantified_a2ot)
    all_activities.name = TERM_COUNT
    all_activities.index = all_activities.index.rename(TERM_ACTIVITY)

    all_activities = all_activities.reset_index()

    try:
        fig = px.bar(all_activities, x=TERM_COUNT, y=TERM_ACTIVITY, color=TERM_ACTIVITY, orientation='h',
                 hover_data=[TERM_ACTIVITY, TERM_COUNT], color_discrete_sequence=CHART_COLOURS)
    except:
        fig = px.bar(all_activities, x=TERM_COUNT, y=TERM_ACTIVITY, color=TERM_ACTIVITY, orientation='h',
                     hover_data=[TERM_ACTIVITY, TERM_COUNT], color_discrete_sequence=CHART_COLOURS)

    fig.update_layout(
        showlegend=False
    )
    fig.update_layout(xaxis_title='Number of Events')

    return fig


def average_adding_removing_quantity_updates_per_time_unit(qop, time_unit):

    if TERM_VALUE in qop.columns:
        pass
    else:
        qop = create_quantity_updates(qop)

    qop.loc[:, TERM_TIME] = pd.to_datetime(qop[TERM_TIME])
    qop[TERM_VALUE] = qop[TERM_VALUE].fillna(0)

    # Separate adding and removing quantity updates
    qop.loc[:, TERM_ADDING] = qop[TERM_VALUE].apply(lambda x: x if x >= 0 else np.nan)
    qop.loc[:, TERM_REMOVING] = qop[TERM_VALUE].apply(lambda x: x if x <= 0 else np.nan)

    # Set Time as index for resampling
    plot_data = qop.set_index(TERM_TIME)

    if time_unit in {"day", "D", TERM_DAILY}:
        # Resample and aggregate data separately for positive and negative updates
        positive_resampled = plot_data.groupby(TERM_ITEM_TYPES).resample("D", origin="start_day", label="left")[
            TERM_ADDING].sum().reset_index()
        negative_resampled = plot_data.groupby(TERM_ITEM_TYPES).resample("D", origin="start_day", label="left")[
            TERM_REMOVING].sum().reset_index()
        positive_resampled = positive_resampled.set_index([TERM_ITEM_TYPES, TERM_TIME])
        negative_resampled = negative_resampled.set_index([TERM_ITEM_TYPES, TERM_TIME])

        date_range = pd.date_range(start=qop[TERM_TIME].min(), end=qop[TERM_TIME].max(), inclusive="both", freq="D")
        date_range = [entry.date() for entry in date_range]
        complete_index = pd.MultiIndex.from_product([qop[TERM_ITEM_TYPES].unique(), date_range],
                                                    names=[TERM_ITEM_TYPES, TERM_TIME])
        positive_resampled = positive_resampled.reindex(complete_index)
        negative_resampled = negative_resampled.reindex(complete_index)
        title = "Average Quantity Updates per Day"
    elif time_unit in {"month", "M", TERM_MONTHLY}:
        # Resample and aggregate data separately for positive and negative updates
        positive_resampled = plot_data.groupby(TERM_ITEM_TYPES).resample("MS", label="left")[
            TERM_ADDING].sum().reset_index()
        negative_resampled = plot_data.groupby(TERM_ITEM_TYPES).resample("MS", label="left")[
            TERM_REMOVING].sum().reset_index()
        positive_resampled = positive_resampled.set_index([TERM_ITEM_TYPES, TERM_TIME])
        negative_resampled = negative_resampled.set_index([TERM_ITEM_TYPES, TERM_TIME])

        date_range = pd.date_range(start=qop[TERM_TIME].min(), end=qop[TERM_TIME].max(), inclusive="both", freq="MS")
        date_range = [entry.date() for entry in date_range]
        complete_index = pd.MultiIndex.from_product([qop[TERM_ITEM_TYPES].unique(), date_range],
                                                    names=[TERM_ITEM_TYPES, TERM_TIME])
        positive_resampled = positive_resampled.reindex(complete_index)
        negative_resampled = negative_resampled.reindex(complete_index)
        title = "Average Quantity Updates per Month"
    elif time_unit in {"event", "e", TERM_EVENT}:
        positive_resampled = qop.loc[:, [TERM_ITEM_TYPES, TERM_ADDING]]
        negative_resampled = qop.loc[:, [TERM_ITEM_TYPES, TERM_REMOVING]]
        title = "Average Quantity Updates per Event"
    else:
        positive_resampled = qop.replace(0, np.nan)
        positive_resampled = positive_resampled.loc[
            ~positive_resampled[TERM_ADDING].isna(), [TERM_ITEM_TYPES, TERM_ADDING]]

        negative_resampled = qop.replace(0, np.nan)
        negative_resampled = negative_resampled.loc[
            ~negative_resampled[TERM_REMOVING].isna(), [TERM_ITEM_TYPES, TERM_REMOVING]]
        title = "Average Quantity Updates per Addition/Removal"

    # Group by Item type and calculate the mean for positive and negative updates
    positive_grouped = positive_resampled.groupby(TERM_ITEM_TYPES)[TERM_ADDING].mean()
    negative_grouped = negative_resampled.groupby(TERM_ITEM_TYPES)[TERM_REMOVING].mean()
    joint_item_types = list(set(positive_grouped.index).union(set(negative_grouped.index)))
    positive_grouped = positive_grouped.reindex(joint_item_types).reset_index()
    negative_grouped = negative_grouped.reindex(joint_item_types).reset_index()
    df_grouped = pd.merge(positive_grouped, negative_grouped, on=TERM_ITEM_TYPES)

    # Melt the dataframe for plotting
    df_melted = df_grouped.melt(id_vars=TERM_ITEM_TYPES, value_vars=[TERM_ADDING, TERM_REMOVING],
                                var_name='Update Type', value_name='Average Quantity Update')

    # Plot
    fig = px.bar(df_melted,
                 x='Average Quantity Update',
                 y=TERM_ITEM_TYPES,
                 color='Update Type',
                 barmode='group',
                 orientation='h',
                 color_discrete_sequence=CHART_COLOURS,
                 hover_data=[TERM_ITEM_TYPES, 'Average Quantity Update', 'Update Type'])


    fig.update_layout(title=title,
                      legend=dict(
                          orientation="h",
                          yanchor="bottom",
                          y=1.01,
                          xanchor="left",
                          x=0,
                          font=dict(
                              size=10,
                          ),
                          title=""
                      )
                  )

    return fig


def average_time_between_typed_qups_per_item_type(qop: pd.DataFrame):
    if TERM_VALUE in qop.columns:
        pass
    else:
        qop = create_quantity_updates(qop)

    qop = qop.dropna(subset=[TERM_VALUE])
    qop = qop.loc[qop[TERM_VALUE] != 0, :]

    # Separate adding and removing quantity updates
    if len(qop) == 0:
        return go.Figure()
    else:
        pass

    qop.loc[qop[TERM_VALUE] > 0, TERM_QUP_TYPE] = TERM_ADDING
    qop.loc[qop[TERM_VALUE] < 0, TERM_QUP_TYPE] = TERM_REMOVING

    qop_enhanced = add_time_since_last_instance(qop, instance_identification=[TERM_ITEM_TYPES, TERM_QUP_TYPE])
    qop_enhanced = qop_enhanced.dropna(subset=[TERM_TIME_SINCE_LAST_EXECUTION])
    qop_enhanced["Average Timedelta [Days]"] = qop_enhanced[TERM_TIME_SINCE_LAST_EXECUTION] / datetime.timedelta(days=1)
    plot_data = qop_enhanced.loc[:, [TERM_QUP_TYPE, TERM_ITEM_TYPES, "Average Timedelta [Days]", TERM_VALUE]]
    plot_data = plot_data.groupby([TERM_QUP_TYPE, TERM_ITEM_TYPES]).mean().reset_index()

    fig = px.bar(plot_data,
                 x="Average Timedelta [Days]",
                 y=TERM_ITEM_TYPES,
                 color=TERM_QUP_TYPE,
                 barmode='group',
                 orientation='h',
                 color_discrete_sequence=CHART_COLOURS,
                 hover_data=[TERM_ITEM_TYPES, "Average Timedelta [Days]", TERM_QUP_TYPE, TERM_VALUE])
    fig.update_layout(legend=dict(
        orientation="h",
        yanchor="bottom",
        y=1.01,
        xanchor="left",
        x=0,
        font=dict(
            size=10,
        ),
        title=""
    )
    )

    return fig


def time_between_it_active_qups_distribution(qop: pd.DataFrame, view: str, item_type: str = None):

    if isinstance(item_type, list):
        item_type = item_type[0]
    else:
        pass

    if view in [TERM_ITEM_TYPES, TERM_COLLECTION, TERM_ACTIVITY]:
        pass
    else:
        raise ValueError(f"View must be one of {TERM_ACTIVITY}, {TERM_COLLECTION}, {TERM_ITEM_TYPES}.")

    if TERM_VALUE in qop.columns:
        if item_type:
            qop = qop.loc[qop[TERM_ITEM_TYPES] == item_type, :]
        else:
            pass
    else:
        if item_type:
            non_item_types, it = split_instance_and_variable_entries(qop.columns)
            qop = qop.loc[:, non_item_types + [item_type]]
        else:
            qop = remove_empty_columns(qop)
        qop = create_quantity_updates(qop)

    qop = qop.dropna(subset=[TERM_VALUE])
    qop = qop.loc[qop[TERM_VALUE] != 0, :]

    if view == TERM_ITEM_TYPES:
        instance_identification = [TERM_ITEM_TYPES]
        x = TERM_ITEM_TYPES
        y = "Timedelta [Days]"
        colour = TERM_ITEM_TYPES
    elif view == TERM_COLLECTION:
        instance_identification = [TERM_ITEM_TYPES, TERM_COLLECTION]
        x = TERM_COLLECTION
        y = "Timedelta [Days]"
        colour = TERM_COLLECTION
    else:
        instance_identification = [TERM_ITEM_TYPES, TERM_ACTIVITY]
        x = TERM_ACTIVITY
        y = "Timedelta [Days]"
        colour = TERM_ACTIVITY

    qop_enhanced = add_time_since_last_instance(qop, instance_identification=instance_identification)
    qop_enhanced = qop_enhanced.dropna(subset=[TERM_TIME_SINCE_LAST_EXECUTION])
    qop_enhanced["Timedelta [Days]"] = qop_enhanced[TERM_TIME_SINCE_LAST_EXECUTION] / datetime.timedelta(days=1)

    fig = px.box(qop_enhanced, x=x, y=y, color=colour, color_discrete_sequence=CHART_COLOURS)

    fig.update_layout(showlegend=False)

    return fig


def time_between_qups_item_type(qop: pd.DataFrame, item_type: str):

    if isinstance(item_type, list):
        item_type = item_type[0]
    elif isinstance(item_type, str):
        pass
    else:
        return plotly.graph_objects.Figure()

    if TERM_VALUE in qop.columns:
        qop = qop.loc[qop[TERM_ITEM_TYPES] == item_type, :]
    else:
        non_item_types, it = split_instance_and_variable_entries(qop.columns)
        qop = qop.loc[:, non_item_types + [item_type]]
        qop = create_quantity_updates(qop)

    qop = qop.dropna(subset=[TERM_VALUE])
    qop = qop.loc[qop[TERM_VALUE] != 0, :]

    qop_enhanced = add_time_since_last_instance(qop, instance_identification=[TERM_ITEM_TYPES])
    qop_enhanced = qop_enhanced.dropna(subset=[TERM_TIME_SINCE_LAST_EXECUTION])
    qop_enhanced["Timedelta last Event [Days]"] = qop_enhanced[TERM_TIME_SINCE_LAST_EXECUTION] / datetime.timedelta(
        days=1)
    qop_enhanced.loc[:, TERM_TIME] = pd.to_datetime(qop_enhanced[TERM_TIME])
    qop_enhanced = qop_enhanced.sort_values(by=[TERM_TIME], ascending=True)

    fig = px.bar(qop_enhanced, x="Timedelta last Event [Days]", y=TERM_EVENT, color=TERM_ACTIVITY,
                 color_discrete_sequence=CHART_COLOURS, pattern_shape=TERM_COLLECTION, orientation="h",
                 hover_data=[TERM_EVENT, TERM_ACTIVITY, TERM_COLLECTION,
                             TERM_ITEM_TYPES, TERM_VALUE, "Timedelta last Event [Days]"])

    unique_collections = qop_enhanced[TERM_COLLECTION].unique()
    first_collection = unique_collections[0]

    for trace in fig.data:
        collection = trace.name.split(', ')[1]
        trace.name = trace.name.split(', ')[0]
        trace.legendgroup = trace.name
        if collection == first_collection:
            pass
        else:
            trace.showlegend = False


    if len(unique_collections) > 1:

        # Dummy traces for unique patterns
        default_patterns = ['', '/', '\\', 'x', '-', '|', '+', '.']
        for i, pattern in enumerate(unique_collections):
            fig.add_trace(go.Bar(
                x=[None], y=[None],
                marker=dict(color="black", pattern_shape=default_patterns[i % len(default_patterns)]),
                name=pattern,
                showlegend=True,
                orientation='h'
            ))

    else:
        pass

    fig.update_layout(
        legend=dict(
            orientation="h",
            font=dict(
                size=10,
            ),
            title="",
            y=1.01
        ),
        yaxis=dict(
            showticklabels=False,  # Hide all x-axis labels
            title="Item-type-active-Events"
        )
    )

    return fig


def qups_for_item_type(qop: pd.DataFrame, item_type: str | Iterable):

    if isinstance(item_type, list):
        item_type = item_type[0]
    elif isinstance(item_type, str):
        pass
    else:
        return plotly.graph_objects.Figure()

    if TERM_VALUE in qop.columns:
        qop = qop.loc[qop[TERM_ITEM_TYPES] == item_type, :]
    else:
        non_item_types, it = split_instance_and_variable_entries(qop.columns)
        qop = qop.loc[:, non_item_types + [item_type]]
        qop = create_quantity_updates(qop)

    qop.loc[:, TERM_TIME] = pd.to_datetime(qop[TERM_TIME])
    qop = qop.sort_values(by=[TERM_TIME], ascending=True)

    fig = px.bar(qop, x=TERM_VALUE, y=TERM_EVENT, color=TERM_ACTIVITY, color_discrete_sequence=CHART_COLOURS,
                 pattern_shape=TERM_COLLECTION, orientation='h', hover_data=[TERM_EVENT, TERM_ACTIVITY, TERM_COLLECTION,
                                                                             TERM_ITEM_TYPES, TERM_VALUE])

    unique_collections = qop[TERM_COLLECTION].unique()
    first_collection = unique_collections[0]

    for trace in fig.data:
        collection = trace.name.split(', ')[1]
        trace.name = trace.name.split(', ')[0]
        trace.legendgroup = trace.name
        if collection == first_collection:
            pass
        else:
            trace.showlegend = False

    # Update the existing traces to not show in legend
    if len(unique_collections) > 1:

        # Dummy traces for unique patterns
        default_patterns = ['', '/', '\\', 'x', '-', '|', '+', '.']
        for i, pattern in enumerate(unique_collections):
            fig.add_trace(go.Bar(
                x=[None], y=[None],
                marker=dict(color="black", pattern_shape=default_patterns[i % len(default_patterns)]),
                name=pattern,
                showlegend=True,
                orientation='h'
            ))

    else:
        pass

    fig.update_layout(
        legend=dict(
            orientation="h",
            font=dict(
                size=10,
            ),
            y=1.01,
            xanchor="left",
            x=0,
        ),
        yaxis=dict(
            showticklabels=False,  # Hide all x-axis labels
            title="Item-type-active-Events"
        )
    )

    return fig

def quantity_state_pre_post_activity_execution_bar_chart(ilvl, qop, activity=None, cp=None, item_types=None):

    if cp:
        ilvl = cp_projection(qty=ilvl, cps=cp)
    else:
        pass

    if activity:
        ilvl = Analysis.eventObject.activity_selection(ilvl=ilvl, activities=activity)
    else:
        pass

    if item_types:
        ilvl = item_type_projection(qty=ilvl, item_types=item_types)
    else:
        pass

    ilvl_filtered = remove_empty_columns(ilvl, keep_zeros=False)

    if ilvl_filtered[TERM_COLLECTION].nunique() > 1:
        return go.Figure()
    else:
        pass

    _, item_types_remaining = split_instance_and_variable_entries(ilvl_filtered.columns)

    ilvl_filtered = ilvl_filtered.drop(columns=[TERM_TIME])

    ilvl_filtered = ilvl_filtered.set_index(TERM_EVENT)

    ilvl_post = ilvvl.transform_pre_event_to_post_event_qstate(ilvl=ilvl_filtered.reset_index(), qop=qop)
    ilvl_post = ilvl_post.set_index(TERM_EVENT)
    ilvl_post.loc[:, item_types_remaining] = ilvl_post.loc[:, item_types_remaining] - ilvl_filtered.loc[:, item_types_remaining]

    # add entries for pre and post
    ilvl_post.loc[:, "Pre-Post"] = "delta"
    ilvl_filtered.loc[:, "Pre-Post"] = "pre"

    # reset indexes
    ilvl_filtered = ilvl_filtered.reset_index()
    ilvl_post = ilvl_post.reset_index()

    ilvl_combined = pd.concat([ilvl_filtered, ilvl_post], axis=0, ignore_index=True)

    # create chart
    default_patterns = ['', '/', '\\', 'x', '-', '|', '+', '.']
    ilvl_melted = ilvl_combined.melt(id_vars=[TERM_EVENT, TERM_ACTIVITY, TERM_COLLECTION, "Pre-Post"], var_name=TERM_ITEM_TYPES,
                                     value_name=TERM_ITEM_LEVELS)

    ilvl_melted = ilvl_melted.dropna(subset=[TERM_ITEM_LEVELS])

    pre_post_order = list(ilvl_combined["Pre-Post"].unique())
    ilvl_melted.loc[:, "Chart Index"] = ilvl_melted[TERM_EVENT].astype(str) + "_" + ilvl_melted[TERM_ITEM_TYPES].astype(str)

    fig = px.bar(ilvl_melted, x=TERM_ITEM_LEVELS, y="Chart Index", color=TERM_ITEM_TYPES, pattern_shape="Pre-Post",
                 hover_data=[TERM_EVENT, "Pre-Post", TERM_ACTIVITY, TERM_ITEM_LEVELS, TERM_COLLECTION],
                 pattern_shape_sequence=default_patterns,
                 color_discrete_sequence=CHART_COLOURS,
                 orientation="h")

    for trace in fig.data:
        pre_post = trace.name.split(', ')[1]
        trace.name = trace.name.split(', ')[0]
        trace.legendgroup = trace.name
        if pre_post == pre_post_order[0]:
            pass
        else:
            trace.showlegend = False

    # Dummy traces for unique patterns
    for i, pattern in enumerate(pre_post_order):
        fig.add_trace(go.Bar(
            x=[None], y=[None],
            marker=dict(color="black", pattern_shape=default_patterns[i % len(default_patterns)]),
            name=pattern,
            showlegend=True,
            orientation='h'
        ))


    fig.update_layout(
            legend=dict(
                orientation="h",
                font=dict(
                    size=10,
                ),
                y=-0.18,
                xanchor="left",
                x=0,
                title=None,
            ),
            yaxis = dict(
                showticklabels=False,
                title="Event and Item Type"
            )
        )

    return fig

def quantity_state_pre_post_activity_execution_boxplots(ilvl, qop, activity=None, cp=None, item_types=None):

    if cp:
        ilvl = cp_projection(qty=ilvl, cps=cp)
    else:
        pass

    if activity:
        ilvl = Analysis.eventObject.activity_selection(ilvl=ilvl, activities=activity)
    else:
        pass

    if item_types:
        ilvl = item_type_projection(qty=ilvl, item_types=item_types)
    else:
        pass

    ilvl_filtered = remove_empty_columns(ilvl, keep_zeros=False)

    if ilvl_filtered[TERM_COLLECTION].nunique() > 1:
        return go.Figure()
    else:
        pass

    _, item_types_remaining = split_instance_and_variable_entries(ilvl_filtered.columns)

    ilvl_filtered = ilvl_filtered.dropna(subset=item_types_remaining, how="all")
    ilvl_filtered = ilvl_filtered.drop(columns=[TERM_TIME])

    ilvl_post = ilvvl.transform_pre_event_to_post_event_qstate(ilvl=ilvl_filtered, qop=qop)

    # add entries for pre and post
    ilvl_post.loc[:, "Pre-Post"] = "Post Event"
    ilvl_filtered.loc[:, "Pre-Post"] = "Pre Event"

    ilvl_combined = pd.concat([ilvl_filtered, ilvl_post], axis=0, ignore_index=True)

    # create chart
    ilvl_melted = ilvl_combined.melt(id_vars=[TERM_EVENT, TERM_ACTIVITY, TERM_COLLECTION, "Pre-Post"], var_name=TERM_ITEM_TYPES,
                                     value_name=TERM_ITEM_LEVELS)

    ilvl_melted = ilvl_melted.dropna(subset=[TERM_ITEM_LEVELS])

    fig = px.box(ilvl_melted, x=TERM_ITEM_TYPES, y=TERM_ITEM_LEVELS, color="Pre-Post",
                 hover_data=[TERM_EVENT, "Pre-Post", TERM_ACTIVITY, TERM_ITEM_LEVELS, TERM_COLLECTION],
                 color_discrete_sequence=CHART_COLOURS[1:], points="all")

    for trace in fig.data:
        trace.jitter = 0.3

    fig.update_layout(
            yaxis = dict(
                title="Item Level"
            )
        )
    fig.update_legends(title_text=None, orientation="h", xanchor="right", yanchor="top", y=1, x=1)

    return fig

def object_qty_impact(oqty, number_objects: bool = True):

    # get active quantity updates
    object_item_quantities = create_item_quantities(oqty)
    object_item_quantities = object_item_quantities.dropna(subset=[TERM_VALUE])
    object_item_quantities = object_item_quantities.loc[object_item_quantities[TERM_VALUE] != 0, :]

    if number_objects:
        aggregated_data = object_item_quantities.groupby(
            [TERM_ITEM_TYPES, TERM_COLLECTION, TERM_ACTIVITY, object_item_quantities[TERM_VALUE] > 0]).size().reset_index(
            name=TERM_COUNT)
    else: # sum of quantity updates
        aggregated_data = object_item_quantities.groupby([TERM_ITEM_TYPES, TERM_COLLECTION, TERM_ACTIVITY, object_item_quantities[TERM_VALUE] > 0]).sum().abs()
        aggregated_data = aggregated_data.rename(columns={TERM_VALUE: TERM_COUNT}).reset_index()

    aggregated_data[TERM_VALUE] = aggregated_data[TERM_VALUE].apply(lambda x: TERM_ADDING if x else TERM_REMOVING)

    # Factorize the categorical data
    aggregated_data['Collection Point Code'], collection_point_uniques = pd.factorize(aggregated_data[TERM_COLLECTION])
    aggregated_data['Item Type Code'], item_type_uniques = pd.factorize(aggregated_data[TERM_ITEM_TYPES])

    # Add jitter
    def add_jitter(value, jitter_amount=0.05):
        return value + np.random.uniform(-jitter_amount, jitter_amount)

    aggregated_data['Jittered Collection Point'] = aggregated_data['Collection Point Code'].apply(
        lambda x: add_jitter(x))
    aggregated_data['Jittered Item Type'] = aggregated_data['Item Type Code'].apply(lambda x: add_jitter(x))

    fig = px.scatter(aggregated_data,
                     x='Jittered Collection Point',
                     y='Jittered Item Type',
                     size=TERM_COUNT,
                     color=TERM_ACTIVITY,
                     symbol=TERM_VALUE,
                     hover_data={TERM_COLLECTION: True, TERM_ITEM_TYPES: True, TERM_ACTIVITY: True, TERM_COUNT: True,
                                 'Jittered Collection Point': False, 'Jittered Item Type': False},
                     color_discrete_sequence=CHART_COLOURS)

    # Update axis labels to reflect the original categories
    fig.update_layout(
        xaxis=dict(
            tickmode='array',
            tickvals=np.arange(len(collection_point_uniques)),
            ticktext=collection_point_uniques,
            title='Collection Point'
        ),
        yaxis=dict(
            tickmode='array',
            tickvals=np.arange(len(item_type_uniques)),
            ticktext=item_type_uniques,
            title='Item Type'
        )
    )

    fig.update_layout(
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.01,
            xanchor="left",
            x=0,
            font=dict(
                size=10,
            ),
            title=""
        )
    )

    fig.update_traces(marker=dict(sizemode='area'))

    return fig
