import time

from typing import *
from datetime import datetime


def get_cur_time(format='%Y-%m-%d-%H-%M-%S', return_formated_str=True) -> Union[str, float]:
    if return_formated_str:
        return datetime.now().strftime(format)
    else:
        return time.time()
    