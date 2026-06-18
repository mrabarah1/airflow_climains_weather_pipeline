from airflow import DAG
from airflow.providers.standard.operators.python import PythonOperator
from datetime import datetime, timedelta
from utils import extract, transform, load, view_database_data


default_args = {
    'owner': 'Emeka',
    'depends_on_past': False,
    'start_date': datetime(2024, 1, 1),
    'retries': 1,
    'retry_delay': timedelta(minutes=5),    
}

with DAG(
    dag_id= "weather_etl_pipeline",
    default_args=default_args,
    description='Weather ETL pipeline',
    schedule='@daily',
    catchup=True,
    tags=['weather', 'etl']
) as dag:
    
    extract_task = PythonOperator(
        task_id="extract",
        python_callable=extract,
        do_xcom_push=True,
    )
    
    transform_task = PythonOperator(
        task_id="transform",
        python_callable=transform,
        op_args=["{{ ti.xcom_pull(task_ids='extract') }}"],
        do_xcom_push=True,
    )
    
    load_task = PythonOperator(
        task_id="load",
        python_callable=load,
        op_args=["{{ ti.xcom_pull(task_ids='transform') }}"],
        do_xcom_push=True,
    )
    
    view_data_task = PythonOperator(
        task_id="view_database_data",
        python_callable=view_database_data,
    )
    
    extract_task >> transform_task >> load_task >> view_data_task

