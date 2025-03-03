#region imports
import os
from sqlalchemy import (
    create_engine,
    MetaData,
    Table,
    Column,
    String,
    Integer,
    select,
    insert,
    text,
)
from llama_index.core import SQLDatabase
from llama_index.llms.azure_openai import AzureOpenAI
from llama_index.core.query_engine import NLSQLTableQueryEngine
from termcolor import colored
#endregion

#region Initialize the Azure OpenAI client
endpoint = os.getenv("ENDPOINT_URL")
deployment_name = os.getenv("DEPLOYMENT_NAME")
subscription_key = os.getenv("AZURE_OPENAI_API_KEY")
llm = AzureOpenAI(
    azure_endpoint = endpoint,
    api_key = subscription_key,
    api_version = "2024-08-01-preview",
    model=deployment_name,
    engine=deployment_name,
)
#endregion

#region create sqlite engine, tables, and insert dummy data
engine = create_engine("sqlite:///:memory:") #create an in-memory database
metadata_obj = MetaData()

# create city SQL table
table_name = "city_stats"
city_stats_table = Table(
    table_name,
    metadata_obj,
    Column("city_name", String(16), primary_key=True),
    Column("population", Integer),
    Column("country", String(16), nullable=False),
)
metadata_obj.create_all(engine)

sql_database = SQLDatabase(engine, include_tables=["city_stats"])

rows = [
    {"city_name": "Toronto", "population":  2930000, "country": "Canada"},
    {"city_name": "LalaLand", "population":   22089000, "country": "CocoCountry"},
    {"city_name": "Tokyo", "population":    13960000, "country": "Japan"},
    {"city_name": "Chicago", "population":  2679000,  "country": "United States",},
    {"city_name": "Seoul", "population":    9776000, "country": "South Korea"},
]
for row in rows:
    stmt = insert(city_stats_table).values(**row)
    with engine.begin() as connection:
        cursor = connection.execute(stmt)
#endregion

#region view current table
stmt = select(
    city_stats_table.c.city_name,
    city_stats_table.c.population,
    city_stats_table.c.country,
).select_from(city_stats_table)

with engine.connect() as connection:
    results = connection.execute(stmt).fetchall()
    print(colored("all rows: ", 'red'))
    print(results)

with engine.connect() as con:
    rows = con.execute(text("SELECT city_name from city_stats"))
    print(colored("city names: ", 'red'))
    for row in rows:        
        print(row)
#endregion

query_engine = NLSQLTableQueryEngine(
    sql_database=sql_database, tables=["city_stats"], llm=llm
)

queries = [
    "What is the total population?", 
    "What is the total population of all cities?", 
    "What is the total population of all countries?", 
    "Which city has the highest population?",
    "Which country has the lowest population?", 
    "What is the city in the country CocoCountry?", 
    "Which country the LalaLand city is in?", 
    "The city LalaLand is in which country?"]

print()
for q in queries:
    response = query_engine.query(q)
    print(colored(q, 'red'))
    print(f"{response}")
    print()
