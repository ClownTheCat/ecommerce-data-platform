from datetime import datetime
from airflow import DAG
from airflow.operators.bash import BashOperator

with DAG(
    dag_id='project_etl',
    start_date=datetime(2024,1,1),
    schedule_interval='@daily',
    catchup=False,
    tags=['etl','bronze']
)as dag:

    extract_task=BashOperator(
        task_id='extract_to_parquet',
        bash_command='cd /opt/airflow/project && python scripts/extract_to_parquet.py',
        env={
            'POSTGRES_HOST':'shop_postgres',
            'POSTGRES_PORT':'5432',
            'MINIO_ENDPOINT':'http://minio:9000'
        }
    )

    dbt_run_task=BashOperator(
        task_id='dbt_run',
        bash_command="cd /opt/airflow/project/dbt && dbt run --profiles-dir ."
    )
    dbt_test_task=BashOperator(
            task_id='dbt_test',
            bash_command="cd /opt/airflow/project/dbt && dbt test --profiles-dir ."
    )

    extract_task >> dbt_run_task >> dbt_test_task


    # transform_task=BashOperator(
    #         task_id='transform_silver',
    #         bash_command='cd /opt/airflow/project && python scripts/transform_silver.py'
    #     )

    # dq_task=BashOperator(
    #         task_id='data_quality',
    #         bash_command='cd /opt/airflow/project && python scripts/data_quality.py'
    #     )
    
    # gold_task=BashOperator(
    #             task_id='build_gold',
    #             bash_command='cd /opt/airflow/project && python scripts/build_gold.py'
    #         )
    # extract_task >> transform_task >> dq_task >> gold_task