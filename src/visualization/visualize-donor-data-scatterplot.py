# Import Packages
import sys
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

import pandas as pd
import numpy as np

# Functions
def get_age_category(value):
    if pd.isnull(value):
        return np.nan
    elif value < 7:
        return 1
    elif value < 14:
        return 2
    elif value < 25:
        return 3
    elif value < 50:
        return 4
    else:
        return 5


def get_age_label(value):
    if value == 1:
        return "0 - 7"
    elif value == 2:
        return "7 - 14"
    elif value == 3:
        return "14 - 25"
    elif value == 4:
        return "25 - 50"
    elif value == 5:
        return "> 50 "
    else:
        return np.NaN


def read_and_format_data(file_path):
    df = pd.read_csv(file_path)

    df['Age Category'] = df['age'].apply(get_age_category)

    df = df[df['category'] == "age-ylw"]

    df = df.melt(id_vars=["Age Category", "age"],
                 var_name="Indicator Name",
                 value_name="Value")

    return df


# Read and Format Data File
file_path = sys.argv[1] # './data/2019-07-17-aggregate-cgm-stats.csv'

df = read_and_format_data(file_path)

# Create Dash App
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']


def create_scatter_app(stylesheets):
    app = dash.Dash(__name__, external_stylesheets=stylesheets)

    available_indicators = df["Indicator Name"].unique()

    app.layout = html.Div([
        html.Div([

            html.Div([
                dcc.Dropdown(
                    id='xaxis-column',
                    options=[{'label': i, 'value': i} for i in available_indicators],
                    value='mean'
                ),
                dcc.RadioItems(
                    id='xaxis-type',
                    options=[{'label': i, 'value': i} for i in ['Linear', 'Log']],
                    value='Linear',
                    labelStyle={'display': 'inline-block'}
                )
            ],
                style={'width': '48%', 'display': 'inline-block'}),

            html.Div([
                dcc.Dropdown(
                    id='yaxis-column',
                    options=[{'label': i, 'value': i} for i in available_indicators],
                    value='gmi'
                ),
                dcc.RadioItems(
                    id='yaxis-type',
                    options=[{'label': i, 'value': i} for i in ['Linear', 'Log']],
                    value='Linear',
                    labelStyle={'display': 'inline-block'}
                )
            ], style={'width': '48%', 'float': 'right', 'display': 'inline-block'})
        ]),

        dcc.Graph(id='indicator-graphic'),

        dcc.Slider(
            id='age--slider',
            min=df['Age Category'].min(),
            max=df['Age Category'].max(),
            value=df['Age Category'].max(),
            marks={int(age_category): get_age_label(age_category) for age_category in
                   df['Age Category'].dropna().unique()},
            step=None
        )
    ])

    return app


app = create_scatter_app(external_stylesheets)


# Define Interactivity
@app.callback(
    Output('indicator-graphic', 'figure'),
    [Input('xaxis-column', 'value'),
     Input('yaxis-column', 'value'),
     Input('xaxis-type', 'value'),
     Input('yaxis-type', 'value'),
     Input('age--slider', 'value')])

def update_graph(xaxis_column_name, yaxis_column_name,
                 xaxis_type, yaxis_type,
                 age_value):
    dff = df[df['Age Category'] == age_value]

    return {
        'data': [dict(
            x=dff[dff['Indicator Name'] == xaxis_column_name]['Value'],
            y=dff[dff['Indicator Name'] == yaxis_column_name]['Value'],
            text=dff[dff['Indicator Name'] == yaxis_column_name]['age'],
            mode='markers',
            marker={
                'size': 10,
                'opacity': 0.5,
                'line': {'width': 0.5, 'color': 'white'}
            }
        )],
        'layout': dict(
            xaxis={
                'title': xaxis_column_name,
                'type': 'linear' if xaxis_type == 'Linear' else 'log'
            },
            yaxis={
                'title': yaxis_column_name,
                'type': 'linear' if yaxis_type == 'Linear' else 'log'
            },
            margin={'l': 40, 'b': 40, 't': 10, 'r': 0},
            hovermode='closest'
        )
    }


if __name__ == '__main__':
    app.run_server(host='0.0.0.0', debug=True)
