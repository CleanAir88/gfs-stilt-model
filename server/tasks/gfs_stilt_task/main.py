import typer
from tasks.gfs_stilt_task.run_gfs_stilt import run_gfs_stilt


def run(run_date: str, receptor_ids: str = None):
    run_gfs_stilt(run_date=run_date, receptor_ids=receptor_ids)


if __name__ == '__main__':
    typer.run(run)