from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.bash import BashOperator


with DAG(
    dag_id='my_dag',
    description='my first basic dag',
    start_date=datetime(2024, 9, 14, 2),
    schedule_interval='@daily'
) as dag:
    task1 = BashOperator(
        task_id='first_task',
        bash_command="echo hello from first task"
    )

    task2 = BashOperator(
        task_id='second_task',
        bash_command="echo hello from second task"
    )

    task3 = BashOperator(
        task_id='thrid_task',
        bash_command="echo hello from third task"
    )

    task1 >> [task2, task3]