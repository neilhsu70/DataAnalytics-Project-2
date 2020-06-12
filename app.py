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

bubble_fig = px.scatter(country_df.head(10), 
    x = 'Country', 
    y ='Confirmed', 
    size = 'Confirmed', 
    color = 'Country', 
    hover_name = 'Country',
    size_max = 50)
           
#get heading and what is covid from heading.py


df_list = [confirmed_df, recovered_df, death_df]

def plot_cases_for_country(ad):
    labels = ['Confirmed', 'Recoverd', 'Deaths']
    colors = ['#5e4fa2', '#66c2a5', '#d53e50']
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

#cards for tally
first_card=dbc.Card([
    dbc.CardBody(children=[html.H4('Confirmed', style = {'padding-top': '5px','font-weight':'bold', 'color':'#5e4fa2'}),
        html.Div([dbc.Button(country_df['Confirmed'].sum(), color="#5e4fa2", size = "lg")])],
        className='text-center')
                    ]),
second_card=dbc.Card([
    dbc.CardBody(children = [html.H4('Recovered', style = {'padding-top': '5px', 'font-weight':'bold', 'color':'#66c2a5'}),
        html.Div([dbc.Button(country_df['Recovered'].sum(), color="#66c2a5", size = "lg")])],
        className='text-center'),
                    ]),
third_card=dbc.Card([
    dbc.CardBody(children = [html.H4('Deaths', style = {'padding-top': '5px', 'font-weight':'bold', 'color':'#d53e50'}),
        html.Div([dbc.Button(country_df['Deaths'].sum(), color="#d53e50", size = "lg")])],
        className='text-center'),
                    ]),
fourth_card=dbc.Card([
    dbc.CardBody(children = [html.H4('Active', style = {'padding-top': '5px', 'font-weight':'bold', 'color':'#f46d43',}),
        html.Div([dbc.Button(country_df['Active'].sum(), color="#f46d43", size = "lg")])],
        className='text-center'),
])

#headings

tally_heading = html.H2(children='World Cases Tally', className='mt-5 py-4 pb-3 text-center')
global_map_heading = html.H2(children='World outbreaks of COVID-19 across time', className='mt-5 py-4 pb-3 text-center')
us_heading =  html.H2(children='US Cases: Confirmed, recovered and deaths', className='mt-3 py-2 pb-1 text-center')
world_heading =  html.H2(children='World Cases: Confirmed, recovered and deaths', className='mt-3 py-2 pb-1 text-center')

# Initialize the app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.JOURNAL])


#Define the app
app.layout = html.Div([

    dbc.Container([
        html.H1(children='COVID-19 Pandemic Analysis Dashboard', className='mt-5 py-4 pb-3 text-center'),
        html.P("Dashboard contributors: Bianca A. Hernandez, Ningning Du, Neil Hsu, Youngjung Choi", style = {'font-weight': 'bold'}, className='mt-3 py-2 pb-1 text-center'),
    ]),
    dbc.Row([dbc.Col(first_card), dbc.Col(second_card), dbc.Col(third_card), dbc.Col(fourth_card)], className='justify-content-center',),

   dbc.Row(
       [
          dbc.Col(
              dbc.Container([
                html.Div([
                html.H2('What is COVID-19?', className='mt-5 py-4 pb-3 text-center'),
                html.P("COVID-19 is a disease caused by a new strain of coronavirus. 'CO' stands for corona, 'VI' for virus, and 'D' for disease."),
                html.P("Symptoms can include fever, cough and shortness of breath. In more severe cases, infection can cause pneumonia or breathing difficulties. More rarely, the disease can be fatal."),
                html.P("The virus is transmitted through direct contact with respiratory droplets of an infected person (generated through coughing and sneezing)."),
                html.H4("Countries with most confirmed COVID-19 cases", style = {'font-weight': 'bold'}, className='mt-3 py-2 pb-1 text-center'),
                html.Div(dcc.Graph(
                    id='top-ten',
                    figure=bubble_fig))    
                ])])),

          dbc.Col(
              dbc.Container([global_map_heading,
                html.Div(id='global-total'), 
                dcc.Graph(
                    id='global-viz',
                    figure=global_animation()
                    ),
                html.Div([
                    dbc.Container([
                        html.H4("To prevent infection and to slow transmission of COVID-19, do the following:", style = {'font-weight': 'bold'}, className='mt-3 py-2 pb-1 text-center'),
                    ]),
                
                html.P("Wash your hands regularly with soap and water, or clean them with alcohol-based hand rub. Avoid touching your face. Stay home if you feel unwell."),
                html.P("Practice physical distancing by avoiding unnecessary travel and staying away from large groups of people."),
                html.P("Cover your mouth and nose when coughing or sneezing."),    
                ])           
                ]
              )    
            )
        ]
    ),        
                          

    dbc.Container([world_heading, 
        html.Div(id='us-total'),
            dcc.Graph(
                id='us-viz',
                figure=plot_cases_for_country('World') 
            )
        ]
    ),

    dbc.Container([us_heading, 
        html.Div(id='us-total2'),
            dcc.Graph(
                id='us-viz2',
                figure=plot_cases_for_country('US') 
            )
        ]
    ),
    dbc.Container([
        html.P('Data Source: COVID-19 Data Repository by the Center for Systems Science and Engineering (CSSE) at Johns Hopkins University', style = {'font-weight': 'bold'}, className='mt-3 py-2 pb-1 text-center'),
    ]),

]
)   

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)