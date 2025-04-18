from loguru import logger
from functools import wraps
from pathlib import Path
import json
import numpy as np
from netCDF4 import Dataset


def nc_data_to_json(
    filename: Path,
    target_path: Path
) -> Path:
    """获取NetCDF(Network Common Data Form) 文件的数据"""
    fh = Dataset(filename, mode='r')
    lons = fh.variables['lon'][:]
    lats = fh.variables['lat'][:]
    foot = fh.variables['foot'][:]

    lons = np.round(lons, 6)
    lats = np.round(lats, 6)

    foot_masked = foot > 0
    time_indices, lat_indices, lng_indices = np.where(foot_masked)

    data = [
        (lons[j], lats[i], float(foot[t, i, j]))  # 将numpy类型转换为Python原生类型
        for t, i, j in zip(time_indices, lat_indices, lng_indices)
    ]

    fh.close()
    res = {"columns": ["lng", "lat", "val"], "data": data}  # 修改为字典格式，更符合JSON标准
    json_name = Path(target_path, filename.stem + '.json')
    with open(json_name, 'w') as f:  # 修改为文本模式写入
        json.dump(res, f)  # 使用json.dump替代orjson.dumps
    return json_name