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

from plotly.subplots import make_subplots
import requests
from sqlalchemy import create_engine
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, inspect



from plotly import tools
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import plotly.express as px
import plotly.graph_objects as go #for calling graph objects from plotly library.

from scipy.interpolate import interp1d


####Connect to cloud database and read in data

user = "postgres"
password = "zaFUa6XbhxjRQKp3nEKd"
host = "dataviz-project2.cx41ow9tqpnq.us-east-2.rds.amazonaws.com"
port = "5432"
db = "postgres"
uri = f"postgresql://{user}:{password}@{host}:{port}/{db}"
engine = create_engine(uri)
conn = engine.connect()
# Reflect Database into ORM classes
Base = automap_base()
Base.prepare(engine, reflect=True)
Base.classes.keys()
# create classes for tables
us_confirmed = Base.classes.us_confirmed
us_deaths= Base.classes.us_deaths
# us_recovered = Base.classes.us_recovered
global_confirmed = Base.classes.global_confirmed
global_deaths= Base.classes.global_deaths
global_recovered = Base.classes.global_recovered
country = Base.classes.country
#create session and read tables into dataframes
session= Session(engine)
result = session.query(us_confirmed).statement
# us_confirmed_df = pd.read_sql_query(result, session.bind)
# us_confirmed_df = us_confirmed_df.drop(labels="id", axis =1)
us_confirmed = pd.read_sql_query(result, session.bind)
us_confirmed = us_confirmed.drop(labels="id", axis =1)


result = session.query(us_deaths).statement
# us_deaths_df = pd.read_sql_query(result, session.bind)
# us_deaths_df= us_deaths_df.drop(labels="id", axis =1)
us_deaths = pd.read_sql_query(result, session.bind)
us_deaths= us_deaths.drop(labels="id", axis =1)

result = session.query(global_confirmed).statement
# global_confirmed_df = pd.read_sql_query(result, session.bind)
# global_confirmed_df = global_confirmed_df.drop(labels="id", axis =1)
confirmed_df = pd.read_sql_query(result, session.bind)
confirmed_df = confirmed_df.drop(labels="id", axis =1)


result = session.query(global_deaths).statement
# global_deaths_df = pd.read_sql_query(result, session.bind)
# global_deaths_df=global_deaths_df.drop(labels="id", axis =1)
death_df = pd.read_sql_query(result, session.bind)
death_df=death_df.drop(labels="id", axis =1)

result = session.query(global_recovered).statement
# global_recovered_df = pd.read_sql_query(result, session.bind)
# global_recovered_df= global_recovered_df.drop(labels="id", axis =1)
recovered_df = pd.read_sql_query(result, session.bind)
recovered_df= recovered_df.drop(labels="id", axis =1)

result = session.query(country).statement
country_df = pd.read_sql_query(result, session.bind)
country_df= country_df.drop(labels="id", axis =1)



#Data
death_df = pd.read_csv('https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_deaths_global.csv')
confirmed_df = pd.read_csv('https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_global.csv')
recovered_df = pd.read_csv('https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_recovered_global.csv')
country_df = pd.read_csv('https://raw.githubusercontent.com/CSSEGISandData/COVID-19/web-data/data/cases_country.csv')

dates = confirmed_df.columns[4:]
confirmed_df_long = confirmed_df.melt(
    id_vars=['Province/State', 'Country/Region', 'Lat', 'Long'], 
    value_vars=dates, 
    var_name='Date', 
    value_name='Confirmed'
)
death_df_long = death_df.melt(
    id_vars=['Province/State', 'Country/Region', 'Lat', 'Long'], 
    value_vars=dates, 
    var_name='Date', 
    value_name='Deaths'
)
recovered_df_long = recovered_df.melt(
    id_vars=['Province/State', 'Country/Region', 'Lat', 'Long'], 
    value_vars=dates, 
    var_name='Date', 
    value_name='Recovered'
)

recovered_df_long = recovered_df_long[recovered_df_long['Country/Region']!='Canada']

full_table = confirmed_df_long.merge(
  right=death_df_long, 
  how='left',
  on=['Province/State', 'Country/Region', 'Date', 'Lat', 'Long']
)
# Merging full_table and recovered_df_long
full_table = full_table.merge(
  right=recovered_df_long, 
  how='left',
  on=['Province/State', 'Country/Region', 'Date', 'Lat', 'Long']
)

full_table['Date'] = pd.to_datetime(full_table['Date'])
full_table['Recovered'] = full_table['Recovered'].fillna(0)

ship_rows = full_table['Province/State'].str.contains('Grand Princess') | full_table['Province/State'].str.contains('Diamond Princess') | full_table['Country/Region'].str.contains('Diamond Princess') | full_table['Country/Region'].str.contains('MS Zaandam')
full_ship = full_table[ship_rows]
full_table = full_table[~(ship_rows)]
full_table['Active'] = full_table['Confirmed'] - full_table['Deaths'] - full_table['Recovered']
full_grouped = full_table.groupby(['Date', 'Country/Region', 'Lat', 'Long'])['Confirmed', 'Deaths', 'Recovered', 'Active'].sum().reset_index()

temp = full_grouped.groupby(['Country/Region', 'Date', ])['Confirmed', 'Deaths', 'Recovered']
temp = temp.sum().diff().reset_index()
mask = temp['Country/Region'] != temp['Country/Region'].shift(1)
temp.loc[mask, 'Confirmed'] = np.nan
temp.loc[mask, 'Deaths'] = np.nan
temp.loc[mask, 'Recovered'] = np.nan
# renaming columns
temp.columns = ['Country/Region', 'Date', 'New cases', 'New deaths', 'New recovered']
# merging new values
full_grouped = pd.merge(full_grouped, temp, on=['Country/Region', 'Date'])
# filling na with 0
full_grouped = full_grouped.fillna(0)
# fixing data types
cols = ['New cases', 'New deaths', 'New recovered']
full_grouped[cols] = full_grouped[cols].astype('int')
# 
full_grouped['New cases'] = full_grouped['New cases'].apply(lambda x: 0 if x<0 else x)
full_grouped["Date"] = full_grouped["Date"].dt.strftime('%Y/%m/%d')


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

def global_animation():
    fig = px.scatter_mapbox(full_grouped,
                            lat="Lat", 
                            lon="Long",                       
                            color="Confirmed", 
                            size=full_grouped['Confirmed']**0.5*50,
                            template='seaborn',
                            color_continuous_scale="spectral", 
                            size_max=50, 
                            animation_frame='Date',
                            #center=dict({'lat': 32, 'lon': 4}), 
                            zoom=0.7, 
                            hover_data= ['Country/Region'])
    
    fig.update_layout(
        mapbox_style="carto-positron", #width=700, height=500, 
        margin={"r":1,"t":1,"l":1,"b":1})
    #update frame speed
    fig.layout.updatemenus[0].buttons[0].args[1]["frame"]["duration"] = 200
    #update different layouts
    #fig.layout.sliders[0].currentvalue.xanchor="center"
    #fig.layout.sliders[0].currentvalue.offset=-100
    fig.layout.sliders[0].currentvalue.prefix=""
    fig.layout.sliders[0].len=.9
    fig.layout.sliders[0].currentvalue.font.color="black"
    fig.layout.sliders[0].currentvalue.font.size=18
    #fig.layout.sliders[0].y= 1.1
    #fig.layout.sliders[0].x= 0.1
    #fig.layout.updatemenus[0].y=1.27
    return fig

#get plots from plots.py file


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
    dbc.Card([
        dbc.CardBody([
            dbc.Container([
            html.H1(children='COVID-19 Pandemic Analysis Dashboard', className='mt-5 py-4 pb-3 text-center'),
            html.P("Dashboard contributors: Bianca A. Hernandez, Ningning Du, Neil Hsu, Youngjung Choi", style = {'font-weight': 'bold'}, className='mt-3 py-2 pb-1 text-center'),
    ])])]),
    
    html.Br(),

    dbc.Row([dbc.Col(first_card), dbc.Col(second_card), dbc.Col(third_card), dbc.Col(fourth_card)], className='justify-content-center',),
    html.Br(),
    dbc.Card([
       dbc.CardBody([
            dbc.Row([
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
    ) ]) ]), 
    html.Br(),       
    dbc.Card([
        dbc.CardBody([
            dbc.Container([world_heading, 
            html.Div(id='us-total'),
            dcc.Graph(
                id='us-viz',
                figure=plot_cases_for_country('World'))]),

        ])

    ]),
    html.Br(),
    dbc.Card([
        dbc.CardBody([
            dbc.Container([us_heading, 
            html.Div(id='us-total2'),
            dcc.Graph(
                id='us-viz2',
                figure=plot_cases_for_country('US') 
            )
        ]
    )])]),

    html.Br(),

    dbc.Container([
        html.P('Data Source: COVID-19 Data Repository by the Center for Systems Science and Engineering (CSSE) at Johns Hopkins University', style = {'font-weight': 'bold'}, className='mt-3 py-2 pb-1 text-center'),
    ]),

]
)   

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)