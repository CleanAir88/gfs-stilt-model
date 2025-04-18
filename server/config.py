import os

BASE_PATH = os.environ.get('BASE_PATH', '/src')
STILT_WD = os.environ.get('STILT_WD', '/usr/local/stilt')
GFS_DATA_PATH = STILT_WD + "/arlout"
OUT_DATA_PATH = STILT_WD + "/stiltout_data"
