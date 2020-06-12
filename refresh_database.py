#!pip install psycopg2-binary
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
import requests
from datetime import datetime
from sqlalchemy import create_engine
import plotly.express as px  # (version 4.7.0)
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, inspect
user = "postgres"
password = "zaFUa6XbhxjRQKp3nEKd"
host = "dataviz-project2.cx41ow9tqpnq.us-east-2.rds.amazonaws.com"
port = "5432"
db = "postgres"
uri = f"postgresql://{user}:{password}@{host}:{port}/{db}"


# uri= "sqlite:///db/covid19.sqlite"
engine = create_engine(uri)
conn = engine.connect()
### Pull data from sources and read into dataframes ###

#John Hopkins data
url1= "https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_US.csv"
url2= "https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_deaths_US.csv"


#European CDC data
url3= "https://opendata.ecdc.europa.eu/covid19/casedistribution/csv"

#John Hopkins data

us_confirmed = pd.read_csv(url1)
us_deaths= pd.read_csv(url2)
global_deaths =  pd.read_csv('https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_deaths_global.csv')
global_confirmed = pd.read_csv('https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_global.csv')
global_recovered = pd.read_csv('https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_recovered_global.csv')
country = pd.read_csv('https://raw.githubusercontent.com/CSSEGISandData/COVID-19/web-data/data/cases_country.csv')


#European CDC data
ecdc = pd.read_csv(url3)

#ARCGIS API data
#request data from web serve, returns COVID-19 data from web service in JSON format
raw= requests.get("https://services1.arcgis.com/0MSEUqKaxRlEPj5g/arcgis/rest/services/Coronavirus_2019_nCoV_Cases/FeatureServer/1/query?where=1%3D1&outFields=*&outSR=4326&f=json")
raw_json = raw.json()
df = pd.DataFrame(raw_json["features"])
#convert dictionary to a list
data_list = df["attributes"].tolist()
#build a new dataframe
arcgis = pd.DataFrame(data_list)
#set "OBJECTID" as index for every record
arcgis.set_index("OBJECTID")
#reorder columns 
arcgis = arcgis[["Country_Region", "Province_State", "Lat", "Long_", "Confirmed", "Recovered", "Deaths", "Last_Update"]]
#preview tranformed data
# arcgis.head()
# arcgis.to_sql("test-table", conn, index=False, if_exists="replace")
us_confirmed.to_sql("us_confirmed", conn, index=False, if_exists="replace")
engine.execute("ALTER TABLE us_confirmed ADD COLUMN ID SERIAL PRIMARY KEY;")
us_deaths.to_sql("us_deaths",conn, index=False, if_exists="replace")
engine.execute("ALTER TABLE us_deaths ADD COLUMN ID SERIAL PRIMARY KEY;")
ecdc.to_sql("ecdc",conn, index=False, if_exists="replace")
engine.execute("ALTER TABLE ecdc ADD COLUMN ID SERIAL PRIMARY KEY;")
arcgis.to_sql("arcgis",conn, index=False, if_exists="replace")
engine.execute("ALTER TABLE arcgis ADD COLUMN ID SERIAL PRIMARY KEY;")
global_confirmed.to_sql("global_confirmed", conn, index=False, if_exists="replace")
engine.execute("ALTER TABLE global_confirmed ADD COLUMN ID SERIAL PRIMARY KEY;")
global_deaths.to_sql("global_deaths", conn, index=False, if_exists="replace")
engine.execute("ALTER TABLE global_deaths ADD COLUMN ID SERIAL PRIMARY KEY;")
global_recovered.to_sql("global_recovered", conn, index=False, if_exists="replace")
engine.execute("ALTER TABLE global_recovered ADD COLUMN ID SERIAL PRIMARY KEY;")
country.to_sql("country", conn, index=False, if_exists="replace")
engine.execute("ALTER TABLE country ADD COLUMN ID SERIAL PRIMARY KEY;")



