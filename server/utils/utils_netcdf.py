import typing
from functools import lru_cache
from pathlib import Path
from netCDF4 import Dataset
import json
import numpy as np

import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from matplotlib.colors import Normalize
from matplotlib.collections import PatchCollection
from io import BytesIO

import config as cfg



@lru_cache(maxsize=10)
def get_nc_data(
    filename: Path,
) -> typing.Tuple[typing.Tuple[str], typing.List[typing.Tuple[float]]]:
    """获取NetCDF(Network Common Data Form) 文件的数据"""
    with open(filename, 'r') as f:
        res = json.loads(f.read())
    return res


def parse_file_name(time: str, lng: float, lat: float, hight: int) -> Path:
    """获取文件路径 stilt_data/20240418/202404182100_117.1914_36.9719_2_foot.nc"""
    file = f"{time}_{lng}_{lat}_{hight}_foot.json"
    path = Path(cfg.OUT_DATA_PATH).joinpath(time[:8]).joinpath(file)
    if not path.exists():
        raise FileNotFoundError(f"文件 {path}不存在")
    return path


async def netcdf_to_data(file,):
    # file_stream = file.file
    netcdf_bytes = await file.read()
    fh = Dataset(file.filename, mode='r', memory=netcdf_bytes)
    # 获取每个变量的值
    lons = fh.variables['lon'][:]
    lats = fh.variables['lat'][:]
    foot = fh.variables['foot'][:]

    # lons 保留6位小数
    lons = np.round(lons, 6)
    lats = np.round(lats, 6)

    # 有效值过滤
    foot_masked = foot > 0
    time_indices, lat_indices, lng_indices = np.where(foot_masked)

    # 获取有效值
    data = [
        (lons[j], lats[i], foot[t, i, j])
        for t, i, j in zip(time_indices, lat_indices, lng_indices)
    ]

    fh.close()
    res = ("lng", "lat", "val"), data
    return res

    
def stilt_to_png(data, rect_unit=0.005):
    # 解析数据
    data_array = np.array(data["data"])
    lng, lat, val = data_array[:, 0], data_array[:, 1], np.log10(data_array[:, 2])

    # 过滤值
    mask = val >= -4
    lng, lat, val = lng[mask], lat[mask], val[mask]

    fig, ax = plt.subplots(figsize=(10, 6), dpi=300, frameon=False)
    ax.set_position([0, 0, 1, 1])  # 去除所有外边距

    # 颜色映射
    cmap = plt.get_cmap("BuPu")
    norm = Normalize(vmin=-4, vmax=max(val))

    # 批量创建矩形
    rects = [Rectangle((x - rect_unit / 2, y - rect_unit / 2), rect_unit, rect_unit) for x, y in zip(lng, lat)]
    patch_collection = PatchCollection(rects, cmap=cmap, norm=norm, alpha=0.75, edgecolor=None)
    patch_collection.set_array(val)
    ax.add_collection(patch_collection)

    # 设置范围
    ax.set_xlim(min(lng), max(lng))
    ax.set_ylim(min(lat), max(lat))
    ax.set_axis_off()

    # 保存到内存
    buffer = BytesIO()
    plt.savefig(buffer, format='png', bbox_inches='tight', pad_inches=0, transparent=True)
    buffer.seek(0)
    plt.close()

    return buffer