from kafka import KafkaProducer
import requests
import json
import sys

KAFKA_BROKER_URL = 'localhost:29092'
TOPIC_NAME = 'company-tickers'

def get_company_by_ticker(ticker):
    api_url = f"http://localhost:8000/api/get-companies?ticker={ticker}"
    response = requests.get(api_url)
    if response.status_code == 200:
        return response.json()  
    return None

def produce_ticker(ticker):
    producer = KafkaProducer(
        bootstrap_servers=KAFKA_BROKER_URL,
        value_serializer=lambda v: json.dumps(v).encode('utf-8')
    )
    
    company = get_company_by_ticker(ticker)
    if company:
        ticker_symbol = company[0]['symbol'] 
        producer.send(TOPIC_NAME, {"ticker": ticker_symbol})
        print(f"Produced {ticker_symbol} to {TOPIC_NAME}")

    producer.flush()

if __name__ == "__main__":
    tickers = sys.argv[1:]  # Accept multiple tickers as arguments
    for ticker in tickers:
        produce_ticker(ticker)


"""
# kafka_producer.py
from kafka import KafkaProducer
import requests
import json

KAFKA_BROKER_URL = 'localhost:29092'
TOPIC_NAME = 'company-tickers'

def get_company_by_ticker(ticker):
    api_url = f"http://localhost:8000/api/get-companies?ticker={ticker}"
    response = requests.get(api_url)
    if response.status_code == 200:
        return response.json()  # Assuming the response contains a company object
    return None

def produce_ticker(ticker):
    producer = KafkaProducer(
        bootstrap_servers=KAFKA_BROKER_URL,
        value_serializer=lambda v: json.dumps(v).encode('utf-8')
    )
    
    company = get_company_by_ticker(ticker)
    if company:
        ticker_symbol = company[0]['symbol']  # Assuming the first result contains the company info
        producer.send(TOPIC_NAME, {"ticker": ticker_symbol})
        print(f"Produced {ticker_symbol} to {TOPIC_NAME}")

    producer.flush()

if __name__ == "__main__":
    sample_ticker = "BBCA.JK"  # Example ticker
    produce_ticker(sample_ticker)
"""
