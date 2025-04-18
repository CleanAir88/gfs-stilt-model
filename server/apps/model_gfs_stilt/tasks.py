import sys
from celery import shared_task
sys.path.append('../../')
from tasks.gfs_stilt_task.main import run as gfs_stilt_run


@shared_task(name="gfs_stilt_task")
def run_gfs_stilt_task(run_date: str, receptor_ids: str):
    gfs_stilt_run(run_date, receptor_ids)
    return "GFS-STILT task completed"