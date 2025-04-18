import os
import subprocess
from pathlib import Path
from loguru import logger


def run(cmd, bg=False, raise_error=False, stdout=False):
    logger.info(f'cmd: {cmd}')
    if bg:
        return subprocess.Popen(cmd.split())
    elif raise_error or stdout:
        res = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if raise_error:
            try:
                res.check_returncode()
            except:
                print(res.stdout.decode('utf-8'))
                raise
        if stdout: return res.stdout.decode('utf-8').strip()
    else:
        os.system(cmd)
    

def create_link_and_backup(source_file: Path, target_file: Path):
    if not target_file.is_symlink() and target_file.is_file():
        target_file.rename(str(target_file.absolute()) + '.old')
    run(f"ln -sf {source_file.absolute()} {target_file.absolute()}")