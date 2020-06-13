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

# Data cleaning and prepare data for plots

# #loading global COVID-19 datasets
# death_df =  pd.read_csv('https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_deaths_global.csv')
# confirmed_df = pd.read_csv('https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_global.csv')
# recovered_df = pd.read_csv('https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_recovered_global.csv')
# country_df = pd.read_csv('https://raw.githubusercontent.com/CSSEGISandData/COVID-19/web-data/data/cases_country.csv')

#transpose all date columns into values (use melt to unpivot dataframes from wide to long format)
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

#Canada recovered data is counted by country vs province/state
#remove recovered data for Canada for above mismatch issue
recovered_df_long = recovered_df_long[recovered_df_long['Country/Region']!='Canada']

#merge the dataframes
# Merging confirmed_df_long and deaths_df_long
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

#convert dataframe from string to datetime 
full_table['Date'] = pd.to_datetime(full_table['Date'])

#many countries are reporting only country-wise data so Province/State NANs make sense
#lots of NANs in recovered (replace with 0)
full_table['Recovered'] = full_table['Recovered'].fillna(0)

#cruise ship corona vireus cases for Grand Princess, Diamond Princess and MS Zaandam
#should probably be extracted 
ship_rows = full_table['Province/State'].str.contains('Grand Princess') | full_table['Province/State'].str.contains('Diamond Princess') | full_table['Country/Region'].str.contains('Diamond Princess') | full_table['Country/Region'].str.contains('MS Zaandam')
full_ship = full_table[ship_rows]

#get rid of cruise ship cases from full_table
full_table = full_table[~(ship_rows)]

#need to aggregate data and create an active cases column 
# Active Case = confirmed - deaths - recovered
full_table['Active'] = full_table['Confirmed'] - full_table['Deaths'] - full_table['Recovered']

#aggregate data into Country/Region and group them by Data and Country/Region
#get total count for Confirmed, Deaths, Recovered, Active
full_grouped = full_table.groupby(['Date', 'Country/Region', 'Lat', 'Long'])['Confirmed', 'Deaths', 'Recovered', 'Active'].sum().reset_index()

#add day wise New cases, New deaths and New recovered 
# new cases 
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

# full_grouped.to_csv('COVID-19-time-series-clean-complete.csv')

# figure_df=pd.read_csv('COVID-19-time-series-clean-complete.csv')
figure_df = full_grouped
#from plots.py
full_grouped["Date"] = full_grouped["Date"].dt.strftime('%Y/%m/%d')

# us_confirmed = pd.read_csv('https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_US.csv')
# # death_df =  pd.read_csv('https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_deaths_global.csv')
# us_deaths = pd.read_csv('https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_deaths_US.csv')

dates = us_confirmed.columns[10:]
us_confirmed_long = us_confirmed.melt(
    id_vars=['UID', 'iso2', 'iso3', 'code3', 'FIPS', 'Admin2', 'Province_State','Country_Region', 'Lat', 'Long_'], 
    value_vars=dates, 
    var_name='Date', 
    value_name='Confirmed'
)
us_deaths_long = us_deaths.melt(
    id_vars=['UID', 'iso2', 'iso3', 'code3', 'FIPS', 'Admin2', 'Province_State','Country_Region', 'Lat', 'Long_'], 
    value_vars=dates, 
    var_name='Date', 
    value_name='Deaths'
)

dates = us_confirmed.columns[11:]
confirmed_us_long = us_confirmed.melt(
    id_vars=['Province_State', 'Country_Region', 'Lat', 'Long_'], 
    value_vars=dates, 
    var_name='Date', 
    value_name='Confirmed'
)
deaths_us_long = us_deaths.melt(
    id_vars=['Province_State', 'Country_Region', 'Lat', 'Long_'], 
    value_vars=dates, 
    var_name='Date', 
    value_name='Deaths'
)

#merge confirmed_us_long and deaths_us_long, "left"
us_full_table = confirmed_us_long.merge(
  right=deaths_us_long, 
  how='left',
  on=['Province_State', 'Country_Region', 'Date', 'Lat', 'Long_', "Date"]
)

#convert date values from string to datetime
us_full_table['Date'] = pd.to_datetime(us_full_table['Date'])

#aggregate data into State_Province wise and group them by Date and State_Province
us_grouped = us_full_table.groupby(['Province_State', 'Country_Region', 'Lat', 'Long_', 'Date'])['Confirmed', 'Deaths', ].sum().reset_index()
#for bar chart
us_fig_data = us_grouped.groupby(['Province_State', 'Date'])['Confirmed', 'Deaths'].sum().reset_index().sort_values('Date', ascending=True)
#make csv
# us_covid=us_fig_data.to_csv('US-COVID-19-time-series-clean-complete.csv')
# #US Covid 
# us_covid=pd.read_csv('US-COVID-19-time-series-clean-complete.csv')
us_covid = us_fig_data
us_covid_day = us_fig_data.groupby(['Date']).sum().reset_index()
# us_covid_day



#Data
# death_df = pd.read_csv('https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_deaths_global.csv')
# confirmed_df = pd.read_csv('https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_global.csv')
# recovered_df = pd.read_csv('https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_recovered_global.csv')
# country_df = pd.read_csv('https://raw.githubusercontent.com/CSSEGISandData/COVID-19/web-data/data/cases_country.csv')

death_df.drop('Province/State', axis=1, inplace=True)
confirmed_df.drop('Province/State', axis=1, inplace=True)
recovered_df.drop('Province/State', axis=1, inplace=True)
country_df.drop(['People_Tested', 'People_Hospitalized'], axis=1, inplace=True)

death_df.rename(columns={'Country/Region': 'Country'}, inplace=True)
confirmed_df.rename(columns={'Country/Region': 'Country'}, inplace=True)
recovered_df.rename(columns={'Country/Region': 'Country'}, inplace=True)
country_df.rename(columns={'Country_Region': 'Country', 'Long_': 'Long'}, inplace=True)
country_df.sort_values('Confirmed', ascending=False, inplace=True)


### functions to plot figures

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
# from plots import global_animation, us_bar
def global_animation():
    fig = px.scatter_mapbox(full_grouped,
                            lat="Lat", 
                            lon="Long",                       
                            color="Confirmed", 
                            size=full_grouped['Confirmed']**0.5*50,
                            template='seaborn',
                            color_continuous_scale="rainbow", 
                            size_max=50, 
                            animation_frame='Date',
                            center=dict({'lat': 32, 'lon': 4}), 
                            zoom=0.7, 
                            hover_data= ['Country/Region'])
    
    fig.update_layout(
        mapbox_style="carto-positron", width=900, height=700,
        margin={"r":1,"t":1,"l":1,"b":1})
    #update frame speed
    fig.layout.updatemenus[0].buttons[0].args[1]["frame"]["duration"] = 200
    #update different layouts
    fig.layout.sliders[0].currentvalue.xanchor="center"
    fig.layout.sliders[0].currentvalue.offset=-100
    fig.layout.sliders[0].currentvalue.prefix=""
    fig.layout.sliders[0].len=.9
    fig.layout.sliders[0].currentvalue.font.color="black"
    fig.layout.sliders[0].currentvalue.font.size=18
    fig.layout.sliders[0].y= 1.1
    fig.layout.sliders[0].x= 0.1
    fig.layout.updatemenus[0].y=1.27
    return fig


# def us_bar(us_covid = pd.read_csv('US-COVID-19-time-series-clean-complete.csv')):
#     fig = go.Figure(go.Bar(x=us_covid["Date"], 
#                           y=us_covid["Confirmed"],
#                           name="Confirmed", 
#                           marker_color='red', opacity=.8
#                        ))
#     fig.add_trace(go.Bar(x=us_covid["Date"], 
#                         y=us_covid["Deaths"],
#                         name="Deaths",
#                         marker_color='grey', opacity=1
#                        ))
#     fig.update_layout(
#                         barmode='overlay', 
#                         xaxis={'categoryorder':'total ascending'},
#                         xaxis_type='category',
#                         title={
#                             'text': 'Cumulative COVID-19 US trend',
#                             'y':0.79,
#                             'x':0.45,
#                             'xanchor': 'center',
#                             'yanchor': 'top'},)
#     fig.update_xaxes(title= 'Time' ,showline=True)
#     fig.update_yaxes(title= 'Number of cases', showline=True)
#     return fig

   

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