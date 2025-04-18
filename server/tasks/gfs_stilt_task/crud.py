import pendulum
import requests
from pathlib import Path
from loguru import logger
import config


def clean_old_gfs_files(directory_path: Path, days_threshold: int = 3):
    """
    删除指定目录下超过指定天数的文件
    
    Args:
        directory_path: 要清理的目录路径
        days_threshold: 文件保留天数阈值，默认3天
    """
    if not directory_path.exists() or not directory_path.is_dir():
        logger.warning(f"目录不存在或不是有效目录: {directory_path}")
        return
    
    now = pendulum.now()
    deleted_count = 0
    skipped_count = 0
    
    logger.info(f"开始清理 {directory_path} 中超过 {days_threshold} 天的文件")
    
    for item in directory_path.glob('**/*'):  # 递归搜索所有文件和目录
        if item.is_file():
            # 获取文件的最后修改时间
            mtime = pendulum.from_timestamp(item.stat().st_mtime)
            days_old = (now - mtime).days
            
            if days_old > days_threshold:
                try:
                    item.unlink()  # 删除文件
                    deleted_count += 1
                    logger.debug(f"已删除: {item} (最后修改: {mtime.to_date_string()}, {days_old}天前)")
                except Exception as e:
                    logger.error(f"删除文件 {item} 时出错: {e}")
            else:
                skipped_count += 1
    
    logger.info(f"清理完成: 已删除 {deleted_count} 个文件, 保留 {skipped_count} 个文件")


def get_gfs(date: pendulum.Date):
    """下载 GFS 文件"""
    GFS_URL = "https://www.ready.noaa.gov/data/archives/gfs0p25/"
    DATA_DIR = Path(config.GFS_DATA_PATH)
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    date_str = date.format("YYYYMMDD")
    file_path = DATA_DIR / f"{date_str}_gfs0p25"

    if file_path.exists():
        logger.info(f"{file_path} exist, skip.")
        return file_path

    file_url = f"{GFS_URL}{date_str}_gfs0p25"
    logger.info(f"download {file_url} ...")
    response = requests.get(file_url, stream=True)
    with file_path.open("wb") as f:
        for chunk in response.iter_content(chunk_size=1024*1024):
            f.write(chunk)

    logger.info(f"download finished: {file_path}")
    return file_path



def get_model_gfs_stilt():
    """获取GFS-STILT模型列表"""
    url = "http://127.0.0.1:8000/api/model_gfs_stilt/model_gfs_stilt/"
    response = requests.get(url).json()
    if len(response) > 0:
        return response[0]
    return None


def get_receptors():
    url = "http://127.0.0.1:8000/api/model_gfs_stilt/receptor/"
    return requests.get(url).json()



if __name__ == "__main__":
    today = pendulum.today("UTC")
    get_gfs(today)