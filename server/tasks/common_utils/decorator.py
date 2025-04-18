import time
from functools import wraps

from loguru import logger


def timer(func_name: str = None, is_debug=True):
    def decorate(func):
        @wraps(func)
        def wrap(*args, **kwargs):
            s = time.time()
            res = func(*args, **kwargs)
            e = time.time()
            txt = f"{func_name or func.__name__}: {round((e - s), 4)}s"
            if is_debug:
                logger.opt(depth=1).debug(txt)
            else:
                logger.opt(depth=1).info(txt)
            return res

        return wrap

    return decorate
