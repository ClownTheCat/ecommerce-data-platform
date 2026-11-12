import psycopg
import os
import sys
import uuid
import json
import boto3
import io
import pandas as pd
from dotenv import load_dotenv
from pathlib import Path
from psycopg import sql

load_dotenv()
# DATA_BRONZE_DIRECTORY=Path(__file__).resolve().parent.parent / 'data' / 'bronze'
# DATA_BRONZE_DIRECTORY.mkdir(parents=True,exist_ok=True)


MINIO_ENDPOINT=os.getenv('MINIO_ENDPOINT', 'http://localhost:9000')
BUCKET_NAME = "bronze"

s3_client = boto3.client(
    's3',
    endpoint_url=MINIO_ENDPOINT,
    aws_access_key_id = 'minioadmin',
    aws_secret_access_key = 'minioadmin'
)



conn_info={
    'host':os.getenv('POSTGRES_HOST'),
    'port':int(os.getenv('POSTGRES_PORT',5433)),
    'user':os.getenv('POSTGRES_USER'),
    'password':os.getenv('POSTGRES_PASSWORD'),
    'dbname':os.getenv('POSTGRES_DB'),
}


def select_all_public_tables(cur):
    cur.execute("select tablename from pg_tables where schemaname='public';")
    tables=[row[0] for row in cur.fetchall()]
    for tablename in tables:
        cur.execute(sql.SQL("select * from {}").format(sql.Identifier(tablename)))
        rows=cur.fetchall()
        cols=[desc[0] for desc in cur.description]
        df=pd.DataFrame(rows,columns=cols)
        for col in df.columns:
            if df[col].dtype=='object':
                df[col] = df[col].apply(
                    lambda x: json.dumps(x) if isinstance(x,dict)
                    else str(x) if isinstance(x,uuid.UUID)
                    else x
                )
        # file_path=DATA_BRONZE_DIRECTORY/f'{tablename}.parquet'
        # df.to_parquet(file_path, index=False)
        # print(f'Таблица: {tablename} выгружена, строк: {len(df)}')

        parquet_buffer = io.BytesIO()
        df.to_parquet(parquet_buffer, index=False, coerce_timestamps='us')

        try:
            s3_client.put_object(
                Bucket=BUCKET_NAME,
                Key=f"{tablename}.parquet",
                Body=parquet_buffer.getvalue()
            )
            print(f'✅ Таблица {tablename} загружена в MinIO (бакет: {BUCKET_NAME}), строк: {len(df)}            ( •̀ ω •́ )✧')
        except Exception as err:
            print(f'❌ Ошибка при загрузке {tablename} в MinIO: {err}    (┬┬﹏┬┬)')


def main():
    try:
        with psycopg.connect(**conn_info) as conn:
            print(f'Подключение {__file__} к базе {conn_info["dbname"]} прошло успешно!')   
            with conn.cursor() as cur:
                select_all_public_tables(cur)


    except Exception as err:
        print(f'[ОШИБКА] Скрипт: {__file__} нихуя не подключился к базе: {conn_info["dbname"]}')
        print(err)
        sys.exit(1)


if __name__=='__main__':
    main()