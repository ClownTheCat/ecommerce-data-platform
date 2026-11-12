import json
import io
import time
import os
import pandas as pd
import boto3
import psycopg
from confluent_kafka import Consumer,KafkaError
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()


conf = {
    'bootstrap.servers' :'localhost:9092',
    'group.id':'clickstream-consumer-group-v5',
    'auto.offset.reset':'latest'
}

consumer = Consumer(conf)
topic_name = 'user_events_stream'

s3_client = boto3.client(
    's3',
    endpoint_url = 'http://localhost:9000',
    aws_access_key_id = 'minioadmin',
    aws_secret_access_key = 'minioadmin'
)
BUCKET_NAME = 'bronze'



pg_conn_info = {
    'host': os.getenv('POSTGRES_HOST'),
    'port':  os.getenv('POSTGRES_PORT',5433),
    'user': os.getenv('POSTGRES_USER'),
    'password': os.getenv('POSTGRES_PASSWORD'),
    'dbname':os.getenv('POSTGRES_DB')
}

BATCH_SIZE = 500
batch=[]

def save_batch_to_minio(data_batch):
    if not data_batch:
        return
    df=pd.DataFrame(data_batch)

    timestamp=datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    filename=f"stream/user_events_{timestamp}.parquet"

    parquet_buffer = io.BytesIO()
    df.to_parquet(parquet_buffer,index=False,coerce_timestamps='us')

    try:
        s3_client.put_object(
            Bucket=BUCKET_NAME,
            Key=filename,
            Body=parquet_buffer.getvalue()

        )
        print(f'✅ Батч сохранен в MinIO: s3://{BUCKET_NAME}/{filename} (событий: {len(df)})')
    except Exception as e:
        print(f'❌ ОШИБКА СОХРАНЕНИЯ В MinIO: {e}')


def save_batch_to_postgres(data_batch):
    if not data_batch:
        return
    try:
        with psycopg.connect(**pg_conn_info) as conn:
            with conn.cursor() as cur:
                data_to_insert = []
                for event in data_batch:
                    data_to_insert.append((
                        event['event_id'],
                        event['user_id'],
                        event.get('session_id', None),

                        event['event_type'],
                        event['product_id'],
                        event['event_timestamp'],
                        json.dumps(event.get('properties', {}))
                    ))
                cur.executemany("""
                    insert into user_events
                    (event_id,user_id,session_id, event_type,product_id,event_timestamp,properties)
                    values(%s,%s,%s,%s,%s,%s,%s)

                """, data_to_insert)

        print(f'✅ Батч сохранен в Postgres (user_events): {len(data_batch)} строк')
    except Exception as err:
        print(f'❌ ОШИБКА POSTGRES: {err}')

def main():
    consumer.subscribe([topic_name])
    print(f"🎧 Консъюмер запущен. Слушаю топик '{topic_name}'...")
    print(f"⌛ Жду накопления {BATCH_SIZE} событий для сохранения в MinIO.")

    try:
        while True:
            msg=consumer.poll(1.0)

            if msg is None:
                continue
            if msg.error():
                if msg.error().code() == KafkaError._PARTITION_EOF:
                    continue
                else:
                    print(f"❌ ОШИБКА KAFKA: {msg.error()}")
                    break

            event_data = json.loads(msg.value().decode('utf-8'))
            batch.append(event_data)

            if len(batch) >=BATCH_SIZE:
                print(f"📦 Накопилось {len(batch)} событий. Сохраняю...")
                save_batch_to_minio(batch)
                save_batch_to_postgres(batch)
                batch.clear()
                consumer.commit()
    except KeyboardInterrupt:
        print('\n 🛑 Остановка консьюмера...')
    finally:
        if batch:
            print(f"📦 Сохраняю последний неполный батч ({len(batch)} событий)...")
            save_batch_to_minio(batch)
            consumer.commit()

        consumer.close()
        print('👋 Консьюмер корректно закрыт! ( •̀ ω •́ )✧')

if __name__ == '__main__':
    main()