#get_default_color
import dash
#pip install dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html

#import necessary libraries
from plotly import tools
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import plotly.express as px
import plotly.graph_objects as go #for calling graph objects from plotly library.
import pandas as pd
import numpy as np 
import requests
#!pip install wget
from datetime import datetime
from scipy.interpolate import interp1d


def global_animation(covid_df = pd.read_csv('COVID-19-time-series-clean-complete.csv')):
    fig = px.scatter_mapbox(covid_df,
                            lat="Lat", 
                            lon="Long",                       
                            color="Confirmed", 
                            size=covid_df['Confirmed']**0.5*50,
                            template='seaborn',
                            color_continuous_scale="rainbow", 
                            size_max=50, 
                            animation_frame='Date',
                            center=dict({'lat': 32, 'lon': 4}), 
                            zoom=0.7, 
                            hover_data= ['Country/Region'])
    
    fig.update_layout(
        mapbox_style="carto-positron",width=900, height=700,
        margin={"r":1,"t":1,"l":1,"b":1})
    #update frame speed
    fig.layout.updatemenus[0].buttons[0].args[1]["frame"]["duration"] = 200
    #update different layouts
    fig.layout.sliders[0].currentvalue.xanchor="left"
    fig.layout.sliders[0].currentvalue.offset=-100
    fig.layout.sliders[0].currentvalue.prefix=""
    fig.layout.sliders[0].len=.9
    fig.layout.sliders[0].currentvalue.font.color="black"
    fig.layout.sliders[0].currentvalue.font.size=24
    fig.layout.sliders[0].y= 1.1
    fig.layout.sliders[0].x= 0.1
    fig.layout.updatemenus[0].y=1.27
    return fig



   
