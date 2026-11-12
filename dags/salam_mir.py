from datetime import datetime
from airflow import DAG
from airflow.operators.bash import BashOperator

with DAG(
    dag_id='salamalekym-mir',
    start_date=datetime(2024,1,1),
    schedule_interval='@daily',
    catchup=False,
    tags=['test']
) as dag:
    task_1 = BashOperator(
        task_id='print_salam',
        bash_command='echo "АЛАХАКБАР БЛЯТЬ ХОХЛЫ!!!!!!"',

    )
    task_2 = BashOperator(
        task_id='print_date',
        bash_command='date',
            
    )

    task_1 >> task_2