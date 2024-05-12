import logging
from pika import BlockingConnection, URLParameters
from time import sleep
import psycopg2
import sys
from time import sleep
from db import db_params

from conf import (DELAY_BETWEEN_RETRIES, RABBITMQ_LOGIN,
                  RABBITMQ_CONNECT_RETRIES, 
                  RABBITMQ_PASSWORD, RABBITMQ_HOST_NAME, RABBITMQ_QUEUE_NAME)

def create_queues(db_params: dict):
    for attempt_number in range(1, RABBITMQ_CONNECT_RETRIES + 1):
        try:
            connection = BlockingConnection(URLParameters(f"amqp://{RABBITMQ_LOGIN}:{RABBITMQ_PASSWORD}@{RABBITMQ_HOST_NAME}/"))
            if connection:
                print("Successfully connected to RabbitMQ")
                break
        except Exception as ex:
            sleep(DELAY_BETWEEN_RETRIES)
            print(ex)
            print(f"Failed to connect to RabbitMQ. Retrying...(attempt number {attempt_number})")
    else:
        print("Failed to connect... Exiting")
        return 1
    channel = connection.channel()
    # queue_name = RABBITMQ_QUEUE_NAME + request.GET.get('id')
    users = get_users(db_params)
    logging.info("users got: ", users)
    for user_id in users:
        queue_name = f"newsletter_queue_{user_id}"
        queue = channel.queue_declare(queue_name)
        channel.queue_bind(exchange="amq.direct", queue=queue_name, routing_key=queue_name)
    connection.close()
    return 0

def get_users(db_params: dict):
    conn = psycopg2.connect(**db_params)
    cursor = conn.cursor()
    cursor.execute(f"SELECT id FROM auth_user")
    res = cursor.fetchall()
    conn.close()
    return [item[0] for item in res]

if __name__ == "__main__":
    create_queues(db_params)