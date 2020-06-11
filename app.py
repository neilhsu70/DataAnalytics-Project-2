import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output

import plotly

import pandas as pd
import numpy as np
from datetime import datetime
import plotly.graph_objects as go
import plotly.express as px
#from scipy.interpolate import interp1d
from datetime import datetime
from plots import global_animation 
# Initialize the app
app = dash.Dash(__name__)



# Define the app

#HTML code
app.layout = html.Div(children=[
    dcc.Graph(
        id='global',
        figure=global_animation()           
        ),

])   

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)