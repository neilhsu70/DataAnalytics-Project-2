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

#Data
death_df = pd.read_csv('https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_deaths_global.csv')
confirmed_df = pd.read_csv('https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_global.csv')
recovered_df = pd.read_csv('https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_recovered_global.csv')
country_df = pd.read_csv('https://raw.githubusercontent.com/CSSEGISandData/COVID-19/web-data/data/cases_country.csv')

death_df.drop('Province/State', axis=1, inplace=True)
confirmed_df.drop('Province/State', axis=1, inplace=True)
recovered_df.drop('Province/State', axis=1, inplace=True)
country_df.drop(['People_Tested', 'People_Hospitalized'], axis=1, inplace=True)

death_df.rename(columns={'Country/Region': 'Country'}, inplace=True)
confirmed_df.rename(columns={'Country/Region': 'Country'}, inplace=True)
recovered_df.rename(columns={'Country/Region': 'Country'}, inplace=True)
country_df.rename(columns={'Country_Region': 'Country', 'Long_': 'Long'}, inplace=True)
country_df.sort_values('Confirmed', ascending=False, inplace=True)

bubble_fig = px.scatter(country_df.head(10), x = 'Country', y ='Confirmed', size = 'Confirmed', color = 'Country', hover_name = 'Country',size_max = 60)
           

#get heading and what is covid from heading.py


df_list = [confirmed_df, recovered_df, death_df]

def plot_cases_for_country(ad):
    labels = ['Confirmed', 'Recoverd', 'Deaths']
    colors = ['blue', 'green', 'red']
    mode_size = [4,4,4]
    line_size = [4,4,4]



    fig = go.Figure()
    
    for i, df in enumerate (df_list):
        if ad =='world' or ad =='World':
            x_data = np.array(list (df.iloc[:,5:].columns))
            y_data = np.sum(np.asarray(df.iloc[:,5:]),axis = 0)
        
        else:
            x_data = np.array(list (df.iloc[:,5:].columns))
            y_data = np.sum(np.asarray(df[df['Country']==ad].iloc[:,5:]),axis = 0)
                        
        fig.add_trace(go.Scatter(x=x_data, y=y_data, mode='lines+markers',name=labels[i],
            line=dict(color=colors[i], width=line_size[i]),
            connectgaps=True,
            text = "Total " +str(labels[i]+ ":" +str(y_data[-1]))
         )) 
    return fig






#get plots from plots.py file
from plots import global_animation, us_bar

#data

#headings

tally_heading = html.H2(children='World Cases Tally', className='mt-5 py-4 pb-3 text-center')
global_map_heading = html.H2(children='World outbreaks of COVID-19 across time', className='mt-5 py-4 pb-3 text-center')
us_heading =  html.H2(children='US Cases: Confirmed, recovered and Deaths', className='mt-5 py-4 pb-3 text-center')
world_heading =  html.H2(children='World Cases: Confirmed, recovered and Deaths', className='mt-5 py-4 pb-3 text-center')

# Initialize the app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.JOURNAL])


#Define the app
app.layout = html.Div([

    dbc.Container([
        html.H1(children='COVID-19 Pandemic Analysis Dashboard', className='mt-5 py-4 pb-3 text-center')
    ]),

    dbc.Row(
            [
                dbc.Col(children = [html.H4('Confirmed', style = {'padding-top': '5px'}),
                        html.Div([dbc.Button(country_df['Confirmed'].sum(), color="danger", size = "lg")])],
                        width=3, className='text-center'),
                
                dbc.Col(children = [html.H4('Recovered', style = {'padding-top': '5px'}),
                        html.Div([dbc.Button(country_df['Recovered'].sum(), color="success", size = "lg")])],
                        width=3, className='text-center'),
                
                dbc.Col(children = [html.H4('Death', style = {'padding-top': '5px'}),
                        html.Div([dbc.Button(country_df['Deaths'].sum(), color="primary", size = "lg")])],
                        width=3, className='text-center'),
                
                dbc.Col(children = [html.H4('Active', style = {'padding-top': '5px'}),
                        html.Div([dbc.Button(country_df['Active'].sum(), color="info", size = "lg")])],
                        width=3, className='text-center'),
            ], className='justify-content-center'),
    
   dbc.Row(
       [
          dbc.Col(
              dbc.Container([
                html.Div([
                html.H2('What is COVID-19?', className='mt-5 py-4 pb-3 text-center'),
                html.P("COVID-19 is a disease caused by a new strain of coronavirus. 'CO' stands for corona, 'VI' for virus, and 'D' for disease."),
                html.P("Symptoms can include fever, cough and shortness of breath. In more severe cases, infection can cause pneumonia or breathing difficulties. More rarely, the disease can be fatal."),
                html.P("The virus is transmitted through direct contact with respiratory droplets of an infected person (generated through coughing and sneezing)."),
                html.P("Dashboard contributed by: Bianca Hernandez, Ningning Du, Neil Hsu, Youngjung Choi", style = {'font-weight': 'bold'}),
                html.Div(dcc.Graph(figure=bubble_fig))    
                ])])),

          dbc.Col(
              dbc.Container([global_map_heading,
                html.Div(id='global-total'), 
                dcc.Graph(
                    id='global-viz',
                    figure=global_animation()
                    )           
                ]
            )
          ) 
       ]
   ), 
                          

    dbc.Container([us_heading, 
        html.Div(id='us-total'),
            dcc.Graph(
                id='us-viz',
                figure=plot_cases_for_country('US') 
            )
        ]
    ),

    dbc.Container([world_heading, 
        html.Div(id='us-total2'),
            dcc.Graph(
                id='us-viz2',
                figure=plot_cases_for_country('World') 
            )
        ]
    ),

]
)   

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)