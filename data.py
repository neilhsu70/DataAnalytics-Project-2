#import dependencies
import dash
#pip install dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
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

#loading global COVID-19 datasets
death_df =  pd.read_csv('https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_deaths_global.csv')
confirmed_df = pd.read_csv('https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_global.csv')
recovered_df = pd.read_csv('https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_recovered_global.csv')
country_df = pd.read_csv('https://raw.githubusercontent.com/CSSEGISandData/COVID-19/web-data/data/cases_country.csv')

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

full_grouped.to_csv('COVID-19-time-series-clean-complete.csv')

figure_df=pd.read_csv('COVID-19-time-series-clean-complete.csv')

us_confirmed = pd.read_csv('https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_US.csv')
death_df =  pd.read_csv('https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_deaths_global.csv')
us_deaths = pd.read_csv('https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_deaths_US.csv')

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
us_covid=us_fig_data.to_csv('US-COVID-19-time-series-clean-complete.csv')
#US Covid 
us_covid=pd.read_csv('US-COVID-19-time-series-clean-complete.csv')
us_covid_day = us_fig_data.groupby(['Date']).sum().reset_index()
us_covid_day
