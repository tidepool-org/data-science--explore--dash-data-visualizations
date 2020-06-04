
# Example of creating visualizations in plotly and just
# using Dash as a wrapper
#
# See this reference for example: https://plotly.com/python/bar-charts/#what-about-dash
#
# The code for creating this figure is pulled directly from this
# Google Colab https://colab.research.google.com/drive/1JYn4B0Smc2l7H7_uF6gXeFOPpwkDi_8m?authuser=2#scrollTo=96Z-nEkblH2n
#
# This code needs some refactoring (cleaning up and splitting into fucntions, etc.),
# so this is meant primarily as an example of using Dash this way.


# Import Packages
import numpy as np
import pandas as pd

import plotly.graph_objs as go

import dash
import dash_core_components as dcc
import dash_html_components as html

# Read in Data

file_path = '/Users/anneevered/Desktop/2019-07-17-aggregate-cgm-stats.csv.gz'

user_stats_df = pd.read_csv(file_path)

#### Helper Functions ####
def get_age_category(value):
    if pd.isnull(value):
        return np.nan
    elif value < 7:
        return 5
    elif value < 14:
        return 4
    elif value < 25:
        return 3
    elif value < 50:
        return 2
    else:
        return 1


def get_age_label(value):
    if value == 5:
        return "0 - 7  "
    elif value == 4:
        return "7 - 14 "
    elif value == 3:
        return "14 - 25 "
    elif value == 2:
        return "25 - 50 "
    elif value == 1:
        return "> 50  "
    else:
        return np.NaN


def get_ylw_category(value):
    if pd.isnull(value):
        return np.nan
    elif value < 1:
        return 3
    elif value < 5:
        return 2
    else:
        return 1


def get_ylw_label(value):
    if value == 3:
        return "0 - 1"
    elif value == 2:
        return "1 - 5"
    elif value == 1:
        return "> 5 "
    else:
        return np.NaN


def get_ylw_age_label(value):
    if np.isnan(value):
        return np.nan
    else:
        age_label = str(get_age_label(round(value / 10)))
        ylw_label = str(get_ylw_label(value % 10))
        return age_label + " & " + ylw_label


user_stats_df["cv"] = user_stats_df["cv"].apply(lambda x: 1/x)

##### Set up initial variables ####

# Rename columns (with what want to show up on the graph)
user_stats_df.rename(columns={'age':'Age (Years)',
                          'ylw':'Years Living With',
                          'mean': 'Average',
                          'std' : 'Standard Deviation',
                          'cv': 'Coefficient of Variation',
                          '50%': 'Median',
                          'percent.cgm < 54':'Percent below 54',
                          'percent.70 <= cgm <= 180':'Percent in range (70-180)',
                          'percent.180 < cgm <= 250':'Percent between 180-250',
                          'percent.cgm > 250':'Percent above 250',
                          'gmi': "Glucose Management Index",
                          'percent.cgm < 40': "Percent below 40",
                          'percent.cgm < 70': "Percent below 70",
                          'percent.cgm > 140': "Percent above 140",
                          'percent.cgm > 180': "Percent above 180",
                          'percent.cgm > 300': "Percent above 300",
                          'percent.cgm > 400': "Percent above 400",
                          'percent.40 <= cgm < 54':'Percent between 40-54',
                          'percent.54 <= cgm < 70':'Percent between 54-70',
                          'percent.70 <= cgm <= 140':'Percent between 70-140',
                          'percent.250 < cgm <= 400':'Percent between 250-400',
                          'avgDuration.episode.cgm < 40': 'Episodes < 40, Average Duration',
                          'avgDuration.episode.cgm < 54': 'Episodes < 54, Average Duration',
                          'avgDuration.episode.cgm < 70': 'Episodes < 70, Average Duration'
                          },
                          inplace=True)

#Add columns to metrics_df for age category and years living with category and age/years living with category
user_stats_df['Age Category'] = user_stats_df['Age (Years)'].apply(get_age_category)
user_stats_df['Years Living With Category'] = user_stats_df['Years Living With'].apply(get_ylw_category)
user_stats_df['Age and Years Living With Category'] = user_stats_df['Age Category']*10 + user_stats_df['Years Living With Category']

#Add Labels
user_stats_df['Age'] = user_stats_df['Age Category'].apply(get_age_label)
user_stats_df['dAge (years since diagnosis)'] = user_stats_df['Years Living With Category'].apply(get_ylw_label)
user_stats_df = user_stats_df.sort_values(by=['Age and Years Living With Category', 'Years Living With Category', 'Age Category'], ascending = True)

#### Helper Functions ####
def add_metric(initial_table, categories, field):
  #For each field want to add it on to the right
  metric_table = user_stats_df.groupby([categories])[field].describe(percentiles = [.10, .25, .5, .75, .90])
  metric_table.rename(columns={'count': field +'.count',
                          'mean': field + '.mean',
                          'std': field + '.std',
                          'min': field + '.min',
                          '10%': field + '.10%',
                          '25%': field + '.25%',
                          '50%': field + '.50%',
                          '75%': field + '.75%',
                          '90%': field + '.90%',
                          'max': field + '.max',},
                 inplace=True)
  metric_table = pd.merge(initial_table, metric_table, how="left", on=categories)
  return metric_table


#Create initial metric table
age_metric_table = pd.DataFrame({'Age Category': [1, 2, 3, 4, 5], 'Years Living With Category': ['NaN', 'NaN', 'NaN', 'NaN', 'NaN']})
ylw_metric_table = pd.DataFrame({'Age Category': ['NaN', 'NaN', 'NaN'],'Years Living With Category': [1, 2, 3]})
age_ylw_metric_table = pd.DataFrame({'Age and Years Living With Category' : user_stats_df['Age and Years Living With Category'].unique()
                                     ,'Age Category': ['NaN']*len(user_stats_df['Age and Years Living With Category'].unique())
                                     ,'Years Living With Category': ['NaN']*len(user_stats_df['Age and Years Living With Category'].unique())})

#List of metrics to include
metrics = ['Percent below 54'
           , 'Percent in range (70-180)'
           , 'Percent between 180-250'
           , 'Percent above 250'
           , 'Average'
           , 'Standard Deviation'
           , "Coefficient of Variation"
           , "Glucose Management Index"
           , "Percent below 40"
           , "Percent below 70"
           , "Percent above 140"
           , "Percent above 180"
           , "Percent above 300"
           , "Percent above 400"
           , 'Percent between 40-54'
           , 'Percent between 54-70'
           , 'Percent between 70-140'
           , 'Percent between 250-400'
           , 'Episodes < 40, Average Duration'
           , 'Episodes < 54, Average Duration'
           , 'Episodes < 70, Average Duration']


#Add each of metrics to table
for metric in metrics:
  age_metric_table = add_metric(age_metric_table,'Age Category', metric)
  ylw_metric_table = add_metric(ylw_metric_table,'Years Living With Category', metric)
  age_ylw_metric_table = add_metric(age_ylw_metric_table,'Age and Years Living With Category', metric)

#Combine the tables
summary_metrics_table = pd.concat([age_metric_table, ylw_metric_table])
summary_metrics_table = pd.concat([summary_metrics_table, age_ylw_metric_table])

#Add Labels
summary_metrics_table['Age'] = summary_metrics_table['Age Category'].apply(get_age_label)
summary_metrics_table['dAge (years since diagnosis)'] = summary_metrics_table['Years Living With Category'].apply(get_ylw_label)
summary_metrics_table['Age & dAge'] = summary_metrics_table['Age and Years Living With Category'].apply(get_ylw_age_label)

def place_value(number):
    return ("{:,}".format(float(number)))

summary_metrics_table['Glucose Management Index.count'] = summary_metrics_table['Glucose Management Index.count'].apply(place_value).astype(str).apply(lambda x: x.split('.')[0])


summary_metrics_table['Age'] = "<b>" + summary_metrics_table['Age'] + " </b><br>(n=" + summary_metrics_table['Glucose Management Index.count'].astype(str) +')'
summary_metrics_table['dAge (years since diagnosis)'] = "<b>" + summary_metrics_table['dAge (years since diagnosis)'] + "   </b><br>(n=" + summary_metrics_table['Glucose Management Index.count'].astype(str) +')'
summary_metrics_table['Age & dAge'] ="<b>" +  summary_metrics_table['Age & dAge'] + "   </b>    (n=" + summary_metrics_table['Glucose Management Index.count'].astype(str) +')'

# Round all values to two decimals
summary_metrics_table = summary_metrics_table.round(1)

# Create Visualization

# Metrics
y_metrics = ['Age'
    , 'dAge (years since diagnosis)'
    , 'Age & dAge']

x_metrics = ['Percent in range (70-180)'
    , 'Percent below 54'
    , "Percent below 70"
    , "Percent above 180"
    , 'Percent above 250'
    , 'Average'
    , 'Standard Deviation'
             # , "Coefficient of Variation"
    , "Glucose Management Index"
    , "Percent below 40"
    , "Percent above 140"
    , "Percent above 300"
    , "Percent above 400"
    , 'Percent between 40-54'
    , 'Percent between 54-70'
    , 'Percent between 70-140'
    , 'Percent between 180-250'
    , 'Percent between 250-400'
    , 'Episodes < 40, Average Duration'
    , 'Episodes < 54, Average Duration'
    , 'Episodes < 70, Average Duration']

# Set values for x-axis max based on metrics
x_axis_range = pd.DataFrame({'metric': x_metrics,
                             'x_axis_range': [(0, 105)
                                 , (0, 3.1)
                                 , (0, 10.1)
                                 , (0, 105)
                                 , (0, 105)
                                 , (99, 241)
                                 , (0, 105)
                                              # , (0, 10.1)
                                 , (4, 10.1)
                                 , (0, 1.1)
                                 , (0, 105)
                                 , (0, 32)
                                 , (0, 4.1)
                                 , (0, 5.1)
                                 , (0, 10.1)
                                 , (0, 105)
                                 , (0, 61)
                                 , (0, 61)
                                 , (0, 40.1)
                                 , (0, 40.1)
                                 , (0, 62)]})

# Set values for x-axis max based on metrics
x_axis_label = pd.DataFrame({'metric': x_metrics,
                             'x_axis_label': ['Percent of Time (%)'
                                 , 'Percent of Time (%)'
                                 , 'Percent of Time (%)'
                                 , 'Percent of Time (%)'
                                 , 'Percent of Time (%)'
                                 , 'mg/dl'
                                 , 'mg/dl'
                                              # , ''
                                 , ''
                                 , 'Percent of Time (%)'
                                 , 'Percent of Time (%)'
                                 , 'Percent of Time (%)'
                                 , 'Percent of Time (%)'
                                 , 'Percent of Time (%)'
                                 , 'Percent of Time (%)'
                                 , 'Percent of Time (%)'
                                 , 'Percent of Time (%)'
                                 , 'Percent of Time (%)'
                                 , 'Minutes'
                                 , 'Minutes'
                                 , 'Minutes']})

# Starting Metrics (i.e. which metrics are pre-selected)
y_starting_metric = 'Age'
x_starting_metric = 'Percent in range (70-180)'

# Move starting metrics to beginning of list
y_metrics.insert(0, y_metrics.pop(y_metrics.index(y_starting_metric)))
x_metrics.insert(0, x_metrics.pop(x_metrics.index(x_starting_metric)))

# Dimensions
graph_width = 1000
graph_height = 550

# Colors
median_dot_color = '#9886cf'
color_iqr = "#ccc3e8"
color_10_to_90 = '#e6e2f4'
color_min_max = '#f6f3fb'
background_color = 'white'

# Font
font_color = "#281946"
font_name = 'Raleway'
font_size = 14

# Median Dot Size
median_dot_sizes = [17, 21, 4]

width = [.3, .25, .3]
starting_width = width[0]

# Traces
traces = []

# Buttons
x_buttons = []
y_buttons = []


#### Create Helper Functions ####
def get_visibility(metric):
    if metric == x_starting_metric:
        return True
    else:
        return False


# def create_min(metric):
#     bar_trace = go.Bar(
#       showlegend = False,
#       visible = get_visibility(metric),
#       x = summary_metrics_table[metric + ".min"],
#       y = summary_metrics_table[y_starting_metric],
#       hoverinfo="skip",
#       orientation = 'h',
#       width = starting_width,
#       textposition = 'inside',
#       marker = dict(
#          color='white'
#       ),
#       opacity=0
#     )
#     bar_trace.yaxis = "y"
#     bar_trace.xaxis = "x"
#     return bar_trace

def create_10(metric):
    bar_trace = go.Bar(
        showlegend=False,
        name="100% of Data",
        legendgroup="legend2",
        visible=get_visibility(metric),
        x=summary_metrics_table[metric + ".10%"],
        y=summary_metrics_table[y_starting_metric],
        hoverinfo='skip',
        orientation='h',
        width=starting_width,
        textposition='inside',
        marker=dict(
            color='white'
        ),
        opacity=0
    )
    bar_trace.yaxis = "y"
    bar_trace.xaxis = "x"
    return bar_trace


def create_25(metric):
    bar_trace = go.Bar(
        showlegend=True,
        legendgroup="legend2",
        name="80% of Data",
        visible=get_visibility(metric),
        x=summary_metrics_table[metric + ".25%"] - summary_metrics_table[metric + ".10%"],
        y=summary_metrics_table[y_starting_metric],
        hoverinfo="skip",
        orientation='h',
        width=starting_width,
        textposition='inside',
        marker=dict(
            color=color_10_to_90
        )
    )
    bar_trace.yaxis = "y"
    bar_trace.xaxis = "x"
    return bar_trace


def create_median(metric):
    scatter_trace = go.Scatter(
        legendgroup="legend1",
        name="Median",
        showlegend=True,
        visible=get_visibility(metric),
        x=summary_metrics_table[metric + ".50%"],
        y=summary_metrics_table[y_starting_metric],
        hoverinfo="x",
        mode='markers',
        marker=dict(
            color=median_dot_color,
            size=median_dot_sizes[0],
            symbol='square',
        )
    )
    scatter_trace.yaxis = "y"
    scatter_trace.xaxis = "x"
    return scatter_trace


def create_75(metric):
    bar_trace = go.Bar(
        legendgroup="legend2",
        name="50% of Data",
        showlegend=True,
        visible=get_visibility(metric),
        x=summary_metrics_table[metric + ".75%"] - summary_metrics_table[metric + ".25%"],
        y=summary_metrics_table[y_starting_metric],
        hoverinfo="skip",
        orientation='h',
        width=starting_width,
        textposition='inside',
        marker=dict(
            color=color_iqr
        )
    )
    bar_trace.yaxis = "y"
    bar_trace.xaxis = "x"
    return bar_trace


def create_90(metric):
    bar_trace = go.Bar(
        legendgroup="legend2",
        name="75%-90%",
        showlegend=False,
        visible=get_visibility(metric),
        x=summary_metrics_table[metric + ".90%"] - summary_metrics_table[metric + ".75%"],
        y=summary_metrics_table[y_starting_metric],
        hoverinfo="skip",
        orientation='h',
        width=starting_width,
        textposition='inside',
        marker=dict(
            color=color_10_to_90
        )
    )
    bar_trace.yaxis = "y"
    bar_trace.xaxis = "x"
    return bar_trace


# def create_max(metric):
#     bar_trace=go.Bar(
#       legendgroup= "legend2",
#       name = "100% of Data",
#       showlegend=False,
#       visible= get_visibility(metric),
#       x = summary_metrics_table[metric+ ".max"] - summary_metrics_table[metric+ ".90%"],
#       y = summary_metrics_table[y_starting_metric],
#       hoverinfo="skip",
#       orientation = 'h',
#       width = starting_width,
#       textposition = 'inside',
#       marker = dict(
#                 color = color_min_max
#       )
#     )
#     bar_trace.yaxis = "y"
#     bar_trace.xaxis = "x"
#     return bar_trace


def get_x_axis_attributes(metric):
    attributes = dict(rangemode='tozero',
                      range=x_axis_range.loc[x_axis_range['metric'] == metric, 'x_axis_range'].iloc[0],
                      tickfont=dict(family=font_name, size=font_size, color=font_color),
                      showgrid=True,
                      gridwidth=1.5,
                      gridcolor="#EDEDED",
                      domain=[0, 1],
                      zeroline=True,
                      title=x_axis_label.loc[x_axis_label['metric'] == metric, 'x_axis_label'].iloc[0],
                      showline=False,
                      zerolinecolor="#EDEDED",
                      zerolinewidth=1.5,
                      ticks='',
                      showticklabels=True,
                      side='bottom'
                      )
    return attributes


def get_y_axis_attributes(domain_start, domain_end):
    attributes = dict(
        tickfont=dict(family=font_name, size=font_size, color=font_color),
        domain=[domain_start, domain_end],
        autorange=True,
        showgrid=False,
        zeroline=False,
        showline=False,
        ticks='',
        showticklabels=True,
        overlaying="y"
    )
    return attributes


def create_x_button(metric):
    visibility_list = [False] * (len(x_metrics))
    true_index = x_metrics.index(metric)
    visibility_list[true_index] = True
    button = dict(label=metric,
                  method='update',
                  args=[{'visible': visibility_list * 6},
                        {"xaxis": get_x_axis_attributes(metric)}])
    return button


def create_y_button(metric, marker_size, width):
    # print([summary_metrics_table[metric]])
    button = dict(args=[{"y": [summary_metrics_table[metric]], "marker.size": marker_size, "width": width}],
                  label=metric,
                  method='restyle'
                  )
    return button


#### Set-up Layout ####
layout = go.Layout(
    title=dict(
        text="CGM Distributions",
        x=.6,
        y=.85,
    ),
    # yaxis_title="Years", #I think this looked cluttered, but could add back in as needed
    width=graph_width,
    font=dict(family='Raleway', size=font_size, color=font_color),
    # Nunito is what is used on Tidepool website; this is close
    height=graph_height,
    margin=dict(
        pad=20
    ),
    autosize=False,
    barmode='stack',
    dragmode=False,
    legend=go.layout.Legend(
        x=1.1,
        y=.8,
        traceorder="reversed",
        font=dict(
            family="Raleway",
            size=12,
            color="black"
        ),
        bgcolor="white",
        bordercolor="white",
        borderwidth=2
    ),
    plot_bgcolor=background_color,
    xaxis=get_x_axis_attributes(x_starting_metric),
    yaxis=get_y_axis_attributes(0, .8),
    yaxis2=get_y_axis_attributes(0, .8)
)

#### Create Buttons ####

# y buttons
for index in range(0, len(y_metrics)):
    y_buttons.append(create_y_button(y_metrics[index], median_dot_sizes[index], width[index]))

# x buttons
for metric in x_metrics:
    x_buttons.append(create_x_button(metric))

#### Add Traces for Various Elements ####

# Min bar
# for metric in x_metrics:
#   traces.append(create_min(metric))

# 10% bar
for metric in x_metrics:
    traces.append(create_10(metric))

# 25% bar
for metric in x_metrics:
    traces.append(create_25(metric))

# 75% bar
for metric in x_metrics:
    traces.append(create_75(metric))

# 90% bar
for metric in x_metrics:
    traces.append(create_90(metric))

#  #for metric in x_metrics:
# for metric in x_metrics:
#   traces.append(create_max(metric))

# Median Point
for metric in x_metrics:
    traces.append(create_median(metric))

#### Create Update Menus ####
updatemenus = list([
    dict(
        active=0,
        buttons=y_buttons,
        direction='down',
        pad={'r': 8, 't': 10},
        showactive=True,
        x=-.7,
        xanchor='left',
        y=.5,
        yanchor='top'
    ),
    dict(
        active=0,
        buttons=x_buttons,
        direction='down',
        pad={'r': 0, 't': 0},
        showactive=True,
        x=0.29,
        xanchor='left',
        y=.96,
        yanchor='top'
    ),
])

layout['updatemenus'] = updatemenus

#### Plot Figures ####
fig = dict(data=traces, layout=layout)

app = dash.Dash()
app.layout = html.Div([
    dcc.Graph(figure=fig)
])

app.run_server(debug=True, use_reloader=False)  # Turn off reloader if inside Jupyter




