# %% REQUIRED LIBRARIES

import dash
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd


# %% EXAMPLE APPLICATION

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

data = [{'a': 1, 'b': 2, 'c':3}, {'a':10, 'b': 20, 'c': 30}]

df = pd.DataFrame(data)

def generate_table(dataframe, max_rows=10):
    return html.Table([
        html.Thead(
            html.Tr([html.Th(col) for col in dataframe.columns])
        ),
        html.Tbody([
            html.Tr([
                html.Td(dataframe.iloc[i][col]) for col in dataframe.columns
            ]) for i in range(min(len(dataframe), max_rows))
        ])
    ])

app.layout = html.Div(children=[
    html.H4(children='US Agriculture Exports (2011)'),
    generate_table(df)
])


if __name__ == '__main__':
    app.run_server(debug=True)