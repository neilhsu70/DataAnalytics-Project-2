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
#get navbar from navbar.py

#get heading and what is covid from heading.py
from tally import world_tally
#get plots from plots.py file
from plots import global_animation, us_bar

#headings
global_map_heading = html.H2(children='World', className='mt-5 py-4 pb-3 text-center')
us_heading =  html.H2(children='US', className='mt-5 py-4 pb-3 text-center')
# Initialize the app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.JOURNAL])


#Define the app
app.layout = html.Div([
    html.Div(children= [global_map_heading, 
        dcc.Graph(
            id='global',
            figure=global_animation()           
            )
        ]
    ),
        dbc.Container([us_heading, 
                html.Div(id='us-total'),
        dcc.Graph(
            id='us',
            figure=us_bar()  
            )
        ]
    ),   
  
     ]
)   

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)