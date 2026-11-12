import json
import time
import uuid
import os
import random
import psycopg
from datetime import datetime
from confluent_kafka import Producer
from faker import Faker
from dotenv import load_dotenv

load_dotenv()

pg_conn_info = {
    'host': os.getenv('POSTGRES_HOST'),
    'port':  os.getenv('POSTGRES_PORT',5433),
    'user': os.getenv('POSTGRES_USER'),
    'password': os.getenv('POSTGRES_PASSWORD'),
    'dbname':os.getenv('POSTGRES_DB')
}


conf = {
    'bootstrap.servers' : 'localhost:9092',
    'client.id' : 'clickstream-producer'
}


with psycopg.connect(**pg_conn_info) as conn:
    with conn.cursor() as cur:
        cur.execute("select customer_id from customers;")
        valid_customer_ids = [row[0] for row in cur.fetchall()]

        cur.execute("select product_id from products;")
        valid_product_ids = [row[0] for row in cur.fetchall()]



producer = Producer(conf)
fake = Faker('ru_RU')

EVENT_TYPES = ['product_view','add_to_cart','search','purchase']
msg_count =0
def delivery_report(err,msg):
    global msg_count
    if err is not None:
        print(f'❌ ОШИБКА ДОСТАВКИ: {err}')
    else:
        msg_count+=1


def main():
    topic_name = 'user_events_stream'
    print(f'🚀 Продюсер запущен. Отправляю события в топик {topic_name}...')
    
    try:
        
        while True:
            event ={
                'event_id':str(uuid.uuid4()),
                'user_id': random.choice(valid_customer_ids),
                'session_id': str(uuid.uuid4()),
                'event_type': random.choice(EVENT_TYPES),
                'product_id': random.choice(valid_product_ids),
                'event_timestamp' : datetime.now().isoformat(),
                'properties' : {'source': random.choice(['google','vk','yandex'])}
            }

            producer.produce(
                topic_name,
                value=json.dumps(event).encode('utf-8'),
                callback=delivery_report
            )

            producer.poll(0)

            if random.randint(1,100) == 1:
                print(f'Отправляю событие: {event["event_type"]}')
            time.sleep(0.1)



    except KeyboardInterrupt:
        print('\n Остановка продюсера...')
    finally:
        producer.flush()
        print('✅ Все сообщения успешно доставлены!')
        print(f'Кол-во сообщений: {msg_count}')


if __name__=='__main__':
    main()