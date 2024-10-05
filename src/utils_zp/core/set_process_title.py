from .base_utils import cur_time


def set_process_title(title='zp', add_time=False):
    from setproctitle import setproctitle
    process_title = f'{title}'
    if add_time:
        process_title += '_'+cur_time()
    setproctitle(process_title)
    