import pendulum
from pathlib import Path
from loguru import logger

import config
from tasks.gfs_stilt_task.crud import get_gfs, get_model_gfs_stilt, get_receptors, clean_old_gfs_files
from tasks.common_utils.model_types import Namelist
from tasks.common_utils.shell import run as run_cmd
from tasks.common_utils.process_stilt_data import nc_data_to_json
from tasks.common_utils.decorator import timer
from tasks.common_utils.exceptions import JobException
from tasks.common_utils.common import render_template, check_files_exist_one, get_stilt_out_filename


@timer()
def run_instance(namelist: Namelist):
    logger.info(f"namelist: {namelist.model_dump()}")
    # 1 生成 r 执行文件
    file_content = render_template(Path(Path(__file__).parent, 'model_template/run_stilt.r.T'), namelist.model_dump())
    r_config_file = Path(config.STILT_WD, "r", "run_stilt.r")
    with open(r_config_file, 'w') as f:
        f.write(file_content)
    
    # 2 执行 r 文件
    proc = run_cmd(cmd=r_config_file)

    # 3 检查输出结果 由于gfs文件可能有缺失 仅验证是否有文件生成 不验证数量
    output_files = get_stilt_out_filename(namelist, stilt_wd=config.STILT_WD)
    flag, error_files = check_files_exist_one(output_files, all_exist=False)
    if not flag:
        error_message = proc.stderr.decode("utf-8")
        logger.error(f"Files not generate: {error_files}")
        raise JobException(error_message)

    # 4 将结果转为json格式 保存到指定目录
    stilt_out_path = Path(config.STILT_WD, 'out/by-id')
    dirs = list(stilt_out_path.iterdir())
    for file_dir in dirs:
        date_path = file_dir.name[:8]
        target_path = Path(config.OUT_DATA_PATH, date_path)
        if not target_path.is_dir():
            target_path.mkdir(parents=True)
        for f in Path(stilt_out_path, file_dir).iterdir():
            if f.suffix == '.nc':
                nc_file = Path(stilt_out_path, file_dir, f)
                nc_data_to_json(filename=nc_file, target_path=target_path)


def run_gfs_stilt(run_date: str, receptor_ids: str = None):
    """
    运行 GFS-STILT 模型
    run_date: 运行日期 格式为 YYYY-MM-DD 默认执行当天 使用UTC时区
    """

    if not run_date:
        run_date = pendulum.now().format("YYYY-MM-DD")
    run_date = pendulum.parse(run_date)
    model_config = get_model_gfs_stilt()
    if model_config is None:
        raise JobException("No model config found.")
    clean_old_gfs_files(directory_path=Path(config.GFS_DATA_PATH), days_threshold=model_config["gfs_file_retention_days"])
    get_gfs(run_date)
    get_gfs(run_date.add(days=1))
    t_start = run_date
    t_end = run_date.add(days=1)
    receptor_list = get_receptors()
    if receptor_ids:
        receptor_ids = receptor_ids.split(',')
        receptor_list = [r for r in receptor_list if str(r["id"]) in receptor_ids]
    for receptor in receptor_list:
        namelist = Namelist(
            stilt_wd=config.STILT_WD,
            n_cores=model_config["n_cores"],
            t_start=t_start,
            t_end=t_end,
            lati=receptor["latitude"],
            long=receptor["longitude"],
            zagl=receptor["height"],
            xmn=receptor['region']["xmn"],
            xmx=receptor['region']["xmx"],
            ymn=receptor['region']["ymn"],
            ymx=receptor['region']["ymx"],
            xres=model_config["xres"],
            yres=model_config["yres"],
        )
        try:
            run_instance(namelist)
        except JobException as e:
            logger.error(f"Job failed: {e}")
            raise JobException(e)


if __name__ == '__main__':
    run_gfs_stilt(run_date='2025-01-03')