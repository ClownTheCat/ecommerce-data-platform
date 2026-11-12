import boto3
from pathlib import Path
import os


MINIO_ENDPOINT = "http://localhost:9000"
ACCESS_KEY = "minioadmin"
SECRET_KEY = "minioadmin"
BUCKET_NAME = 'bronze'

s3_client = boto3.client(
    's3',
    endpoint_url=MINIO_ENDPOINT,
    aws_access_key_id = ACCESS_KEY,
    aws_secret_access_key = SECRET_KEY
)


LOCAL_FILE= Path(__file__).resolve().parent.parent / 'data' / 'bronze' / 'customers.parquet'

def upload_file():
    if not LOCAL_FILE.exists():
        print(f'❌ Файл {LOCAL_FILE} не найден! (┬┬﹏┬┬)')
        return

    print(f'🐦‍⬛ Загружаю {LOCAL_FILE.name} в бакет {BUCKET_NAME}... ')

    try:
        s3_client.upload_file(
            Filename=str(LOCAL_FILE),
            Bucket=BUCKET_NAME,
            Key=LOCAL_FILE.name
        )
        print(f'✅ Файл успешно загружен в MinIO! ( •̀ ω •́ )✧')
    except Exception as err:
        print(f'❌ Ошибка загрузки {err} (┬┬﹏┬┬)')

if __name__ == '__main__':
    upload_file()