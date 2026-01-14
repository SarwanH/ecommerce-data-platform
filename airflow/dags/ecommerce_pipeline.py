"""E-Commerce Data Pipeline DAG."""

from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
from airflow.utils.task_group import TaskGroup

default_args = {
    'owner': 'data-engineering',
    'depends_on_past': False,
    'retries': 2,
    'retry_delay': timedelta(minutes=5),
}

with DAG(
    dag_id='ecommerce_data_pipeline',
    default_args=default_args,
    description='Daily e-commerce data pipeline',
    schedule_interval='0 6 * * *',
    start_date=datetime(2024, 1, 1),
    catchup=False,
    tags=['ecommerce', 'production'],
) as dag:

    # Ingestion Tasks
    with TaskGroup('ingestion') as ingestion:
        def extract_data(**ctx):
            print(f"Extracting data for {ctx['ds']}")
        
        extract = PythonOperator(
            task_id='extract',
            python_callable=extract_data,
        )

    # Data Quality
    with TaskGroup('quality') as quality:
        def run_checks(**ctx):
            print("Running data quality checks")
        
        checks = PythonOperator(
            task_id='checks',
            python_callable=run_checks,
        )

    # dbt Transformations
    with TaskGroup('dbt') as dbt:
        dbt_run = BashOperator(
            task_id='run',
            bash_command='cd /opt/airflow/dbt && dbt run',
        )
        dbt_test = BashOperator(
            task_id='test',
            bash_command='cd /opt/airflow/dbt && dbt test',
        )
        dbt_run >> dbt_test

    # Completion
    def notify(**ctx):
        print(f"Pipeline complete for {ctx['ds']}")
    
    complete = PythonOperator(
        task_id='complete',
        python_callable=notify,
    )

    ingestion >> quality >> dbt >> complete