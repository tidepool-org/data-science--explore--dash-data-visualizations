# Import Packages
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

import pandas as pd
import numpy as np


# Read and Format Data File
file_path = input("Enter file path : ")

user_stats_df = pd.read_csv(file_path)

import plotly.express as px
df = px.data.tips()
fig = px.box(df, x="time", y="total_bill", points="all")
fig.show()