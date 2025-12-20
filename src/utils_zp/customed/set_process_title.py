from .base_utils import Datetime_


def set_process_title(title='zp', add_time=False):
    from setproctitle import setproctitle
    process_title = f'{title}'
    if add_time:
        process_title += ' | '+Datetime_().format_str(1)
    setproctitle(process_title)
    