from datetime import datetime
from airflow import DAG
from airflow.operators.bash import BashOperator

with DAG(
    dag_id='generate_data',
    start_date=datetime(2024,1,1),
    schedule_interval='@daily',
    catchup=False,
    tags=['etl','bronze']
)as dag:

    generate_data=BashOperator(
        task_id='generate_data',
        bash_command='cd /opt/airflow/project && python scripts/generate_data.py',
        env={
            'POSTGRES_HOST':'shop_postgres',
            'POSTGRES_PORT':'5432'
        }
    )