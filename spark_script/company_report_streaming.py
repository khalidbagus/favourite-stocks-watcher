from pyspark.sql import SparkSession
from pyspark.sql.types import StructType, StringType
from pyspark.sql import functions as F
import requests
import json
import os
from dotenv import load_dotenv

# Load the environment variables
load_dotenv('/spark_script/.env')

# Access the API key from .env
SECTORS_API_KEY = os.getenv('SECTORS_API_KEY')
# de357f3f0363e960c0f7b426a829d530e4fbe6bbf29ba806c0ad698a87c070b1
# Define the Spark session with Cassandra configuration
spark = SparkSession \
    .builder \
    .appName("Kafka-Spark-Streaming") \
    .master("local[*]") \
    .config("spark.cassandra.connection.host", "cassandra") \
    .config("spark.cassandra.connection.port", "9042") \
    .getOrCreate()

# Kafka parameters
KAFKA_BROKER_URL = 'kafka:9092'
TOPIC_NAME = 'company-tickers'
SECTORS_APP_API_URL = "https://api.sectors.app/v1/company/report/"

# Fetch the company report from the external API (sectors.app)
def fetch_report_from_sectors_app(ticker):
    print(f"Fetching report for ticker: {ticker}")
    api_url = SECTORS_APP_API_URL.format(ticker)
    headers = {
        "Authorization": SECTORS_API_KEY
    }
    print(api_url)
    print(headers)
    #response = requests.get(api_url, headers=headers)
    response = requests.get(f"{SECTORS_APP_API_URL}{ticker}/", headers=headers)
    if response.status_code == 200:
        print(f"Received report data for ticker: {ticker}")
        return response.json()  # Return the JSON response
    else:
        print(f"Failed to fetch data for ticker: {ticker}, Status code: {response.status_code}")
        print(f"Response: {response.content}")
    return None

# Function to write batch to Cassandra
def write_to_cassandra(df, epoch_id):
    print(f"Writing batch to Cassandra for epoch: {epoch_id}")
    df.write \
        .format("org.apache.spark.sql.cassandra") \
        .options(keyspace="financial_data", table="company_reports") \
        .mode("append") \
        .save()

# Kafka Dataframe Schema
schema = StructType().add("ticker", StringType())

# Reading from Kafka
df = spark \
    .readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", KAFKA_BROKER_URL) \
    .option("subscribe", TOPIC_NAME) \
    .load() \
    .selectExpr("CAST(value AS STRING) as message")

# Parse the JSON messages from Kafka
df = df.withColumn("ticker", F.from_json(F.col("message"), schema).getItem("ticker"))

# Process the data and fetch reports from API, and write to Cassandra
def process_ticker_batch(df, batch_id):
    print(f"Processing batch {batch_id}")
    tickers = df.select("ticker").rdd.map(lambda row: row.ticker).collect()
    
    if not tickers:
        print(f"No tickers found in batch {batch_id}")
    else:
        print(f"Tickers found: {tickers}")
        print("Loaded .env:", os.path.exists('/spark_script/.env'))
        print(f"API Key Loaded: {SECTORS_API_KEY}")

    
    data_to_write = []
    for ticker in tickers:
        report_data = fetch_report_from_sectors_app(ticker)
        if report_data:
            print(f"Appending data for ticker: {ticker}")
            # Prepare row for Cassandra
            data_to_write.append((ticker, json.dumps(report_data)))
        else:
            print(f"No data to write for ticker: {ticker}")

    if data_to_write:
        print(f"Writing {len(data_to_write)} records to Cassandra for batch {batch_id}")
        # Create a DataFrame and write to Cassandra
        cassandra_df = spark.createDataFrame(data_to_write, schema=["ticker", "report_data"])
        write_to_cassandra(cassandra_df, batch_id)
    else:
        print(f"No data to write to Cassandra for batch {batch_id}")

# Apply the processing function to the streaming data
df.writeStream \
    .foreachBatch(process_ticker_batch) \
    .start() \
    .awaitTermination()


"""
# spark_streaming_consumer.py
from pyspark.sql import SparkSession
from pyspark.sql.types import StructType, StringType
from pyspark.sql import functions as F
import requests
from cassandra.cluster import Cluster
import json
import os
from dotenv import load_dotenv

# Load the environment variables
load_dotenv('/spark_script/.env')

# Access the API key from .env
SECTORS_API_KEY = os.getenv('SECTORS_API_KEY')

# Define the Spark session
spark = SparkSession \
    .builder \
    .appName("Kafka-Spark-Streaming") \
    .master("local[*]") \
    .config("spark.cassandra.connection.host", "localhost") \
    .getOrCreate()

# Kafka parameters
KAFKA_BROKER_URL = 'kafka:9092'
TOPIC_NAME = 'company-tickers'
SECTORS_APP_API_URL = 'https://api.sectors.app/v1/company/report/{}'

# Cassandra connection
def connect_to_cassandra():
    cluster = Cluster(['cassandra'])
    session = cluster.connect('financial_data')  # Keyspace
    return session

def store_in_cassandra(session, ticker, report_data):
    query = "INSERT INTO company_reports (ticker, report_data) VALUES (%s, %s)"
    session.execute(query, (ticker, json.dumps(report_data)))

# Fetch the company report from the external API (sectors.app)
def fetch_report_from_sectors_app(ticker):
    api_url = SECTORS_APP_API_URL.format(ticker)
    headers = {
        'Authorization': SECTORS_API_KEY
    }
    response = requests.get(api_url, headers=headers)
    if response.status_code == 200:
        return response.json()  # Return the JSON response
    return None

# Kafka Dataframe Schema
schema = StructType().add("ticker", StringType())

# Reading from Kafka
df = spark \
    .readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", KAFKA_BROKER_URL) \
    .option("subscribe", TOPIC_NAME) \
    .load() \
    .selectExpr("CAST(value AS STRING) as message")

# Parse the JSON messages from Kafka
df = df.withColumn("ticker", F.from_json(F.col("message"), schema).getItem("ticker"))

# Define the Cassandra session
cassandra_session = connect_to_cassandra()

# Process each ticker in the stream
def process_ticker_batch(df, batch_id):
    tickers = df.select("ticker").rdd.map(lambda row: row.ticker).collect()
    
    for ticker in tickers:
        report_data = fetch_report_from_sectors_app(ticker)
        if report_data:
            store_in_cassandra(cassandra_session, ticker, report_data)
            print(f"Stored report for {ticker} in Cassandra.")

# Apply the processing function to the streaming data
df.writeStream \
    .foreachBatch(process_ticker_batch) \
    .start() \
    .awaitTermination()
"""