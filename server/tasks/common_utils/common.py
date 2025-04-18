import os
import pendulum
from pathlib import Path
from jinja2 import Template
from loguru import logger
from .model_types import Namelist


def check_files(expected_files, path=''):
    result = True
    if type(expected_files) == str:
        expected_files = [expected_files]
    for file in expected_files:
        if not Path(path, file).is_file():
            logger.info(f'File {file} has not been generated!')
            result = False
            break
    return result


def check_files_exist_one(files: list, all_exist: bool = True):
    """Check if files exist."""
    error_files = []
    exist_files = []
    for file in files:
        if not os.path.exists(file):
            error_files.append(file)
        else:
            exist_files.append(file)
    if all_exist:
        if error_files:
            return False, error_files 
    else:
        if not exist_files:
            return False, error_files
    return True, None


def render_template(template_file: str, data: dict) -> str:
    print('rendering template ', template_file)

    with open(template_file, 'r') as tf:
        template = Template(tf.read())
        return template.render(data)
    

def get_stilt_job_id(time: pendulum.DateTime, longitude, latitude, zagl):
    """Generate STILT job ID."""
    # /home/wrf_model/data/stilt_data/20240418/202404182100_117.1914_36.9719_2_foot.nc"""
    job_id = (
        time.format("YYYYMMDDHH00") + f"_{longitude}"
        f"_{latitude}"
        f"_{zagl}"
    )
    return job_id



def get_stilt_out_filename(namelist: Namelist, stilt_wd: str):
    """Get STILT output filenames."""
    file_list = []
    for hour_delta in range(int((namelist.t_end - namelist.t_start).total_hours())):
        time = namelist.t_start.add(hours=hour_delta)
        job_id = get_stilt_job_id(
            time=time, longitude=namelist.long, latitude=namelist.lati, zagl=namelist.zagl
        )
        filename = os.path.join(
            stilt_wd, "out", "by-id", job_id, f"{job_id}_foot.nc"
        )
        file_list.append(filename)
    return file_list