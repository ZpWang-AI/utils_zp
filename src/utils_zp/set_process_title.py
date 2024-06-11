from setproctitle import setproctitle
from datetime import datetime


def set_process_title(title, prefix='zp_'):
    setproctitle(f'{prefix}{title}')