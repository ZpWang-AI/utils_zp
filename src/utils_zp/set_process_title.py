from setproctitle import setproctitle
from .time_utils import get_cur_time


def set_process_title(title, prefix='zp_', add_time=False):
    process_title = f'{prefix}{title}'
    if add_time:
        process_title += '_'+get_cur_time('%Y.%m.%d-%H:%M:%S')
    setproctitle(process_title)
    