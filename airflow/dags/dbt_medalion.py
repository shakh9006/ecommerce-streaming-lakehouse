import logging
import sys
from datetime import timedelta

sys.path.append('/opt/airflow/plugins')

from airflow.sdk import dag, task
from dbt_operator import DbtCoreOperator
from airflow import settings

logger = logging.getLogger(__name__)

DBT_PROJECT_PATH = f"{settings.AIRFLOW_HOME}/dbt_ecommerce"

logger.info(f"DBT Project Path: {DBT_PROJECT_PATH}")

@dag(
    dag_id="dbt_medalion",
    schedule="*/5 * * * *",
    catchup=False,
    description="DBT Medalion DAG - Staging -> Core -> Metrics",
    tags=["dbt", "medallion"],
    default_args={
        "owner": "airflow",
        "depends_on_past": False,
        "email_on_failure": False,
        "email_on_retry": False,
        "retries": 1,
        "retry_delay": timedelta(minutes=5),
    },
)
def transformation():
    dbt_staging = DbtCoreOperator(
        task_id='dbt_run_staging',
        dbt_project_dir=DBT_PROJECT_PATH,
        dbt_profiles_dir=DBT_PROJECT_PATH,
        dbt_command='run',
        select='staging',
        full_refresh=True,
    )
    
    dbt_core = DbtCoreOperator(
        task_id='dbt_run_core',
        dbt_project_dir=DBT_PROJECT_PATH,
        dbt_profiles_dir=DBT_PROJECT_PATH,
        dbt_command='run',
        select='marts.core',
        full_refresh=True,
    )
    
    dbt_metrics = DbtCoreOperator(
        task_id='dbt_run_metrics',
        dbt_project_dir=DBT_PROJECT_PATH,
        dbt_profiles_dir=DBT_PROJECT_PATH,
        dbt_command='run',
        select='marts.metrics',
    )
    
    dbt_staging >> dbt_core >> dbt_metrics

transformation()