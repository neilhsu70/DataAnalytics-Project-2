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

#data

#headings

tally_heading = html.H2(children='World Cases Tally', className='mt-5 py-4 pb-3 text-center')
global_map_heading = html.H2(children='World outbreaks of COVID-19 across time', className='mt-5 py-4 pb-3 text-left')
us_heading =  html.H2(children='US Cases: Confirmed and Deaths', className='mt-5 py-4 pb-3 text-left')
# Initialize the app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.JOURNAL])


#Define the app
app.layout = html.Div([

    dbc.Container([
        html.H1(children='COVID-19 Pandemic Analysis Dashboard', className='mt-5 py-4 pb-3 text-center')
    ]),

    dbc.Row(
        [
        dbc.Col(html.Div("Confirmed", className='mt-5 py-4 pb-3 text-center')),
        dbc.Col(html.Div("Deaths", className='mt-5 py-4 pb-3 text-center')),
        dbc.Col(html.Div("Active", className='mt-5 py-4 pb-3 text-center')),
        dbc.Col(html.Div("Recoverd", className='mt-5 py-4 pb-3 text-center')),   
        ]
    ),

    dbc.Container(
    [
        html.Div([
            html.H2('What is COVID-19?', className='mt-5 py-4 pb-3 text-left'),
            html.P("A coronavirus is a kind of common virus that can cause respiratory infections. Most coronaviruses aren't dangerous."),
            html.P("COVID-19 is a disease that can cause respiratory tract infections and can affect upper respiratory tract (sinuses, nose, and throat) or lower respiratory tract (windpipe and lungs). It's caused by a coronavirus named SARS-CoV-2."),
            html.P("It spreads mainly through person-to-person contact. Infections range from mild to serious.")
        ])
    ]),
    
    dbc.Container([global_map_heading,
        html.Div(id='global-total'), 
            dcc.Graph(
                id='global-viz',
                figure=global_animation()
            )           
        ]
    ),                                 

    dbc.Container([us_heading, 
        html.Div(id='us-total'),
            dcc.Graph(
                id='us-viz',
                figure=us_bar()  
            )
        ]
    ),  
]
)   

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)