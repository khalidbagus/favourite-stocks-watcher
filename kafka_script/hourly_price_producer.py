import random
import sys
import time
from datetime import datetime
from json import dumps

from cassandra.cluster import Cluster
from kafka import KafkaProducer
import mysql.connector

CASSANDRA_HOST = 'localhost'
CASSANDRA_KEYSPACE = 'trading'
CASSANDRA_TABLE = 'real_time_data'

KAFKA_BOOTSTRAP_SERVER = 'localhost:29092'

def get_last_id():
    cluster = Cluster([CASSANDRA_HOST])
    session = cluster.connect(CASSANDRA_KEYSPACE)
    query = f"SELECT MAX(id) AS last_id FROM {CASSANDRA_TABLE}"
    result = session.execute(query)
    last_id = result.one().last_id
    return last_id if last_id else 0

def produce_message(id):
    cluster = Cluster([CASSANDRA_HOST])
    session = cluster.connect(CASSANDRA_KEYSPACE)
    message = {}
    message["id"] = id
    message["created_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    message["open"] = session.execute(f"SELECT open FROM {CASSANDRA_TABLE} WHERE hour={message["created_at"]}")
    message["close"] = 
    message["high"] = 
    message["low"] = random.uniform(10,40)
    return message

def main():
    KAFKA_TOPIC = sys.argv[1]
    producer = KafkaProducer(bootstrap_servers=KAFKA_BOOTSTRAP_SERVER,
                            value_serializer=lambda x: dumps(x).encode('utf-8'))
    last_id = get_last_id()
    print("Starting Kafka Producer application...")

    try:
        while True:
            message = []
            id = last_id + 1
            message.append(produce_message(id))
            last_id = id  
            print(f"Produced message: {message}")
            producer.send(KAFKA_TOPIC, message)
            time.sleep(2)  
    except KeyboardInterrupt:
        producer.flush()
        producer.close()
        print("Kafka producer application completed.")
        
if __name__ == "__main__":
    main()