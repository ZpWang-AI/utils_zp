from .import_ import *
from .format_ import format_seconds_to_str


def cur_time(format='%Y-%m-%d %H:%M:%S', return_formated_str=True) -> Union[str, float]:
    """
    %Y-%m-%d %H:%M:%S
    
    %Y-%m-%d-%H-%M-%S
    
    %Y_%m_%d_%H_%M_%S
    
    %Y.%m.%d-%H:%M:%S
    """
    if return_formated_str:
        return datetime.datetime.now().strftime(format)
    else:
        return time.time()


class StopWatch:
    def __init__(self) -> None:
        self.time_list = []
    
    def record(self):
        self.time_list.append(cur_time(return_formated_str=False))
    
    def __repr__(self) -> str:
        if not self.time_list:
            return ''
        elif len(self.time_list) == 1:
            return datetime.datetime.fromtimestamp(self.time_list[0])
        else:
            res = [
                format_seconds_to_str(
                    self.time_list[p+1]-self.time_list[p] 
                ) for p in range(len(self.time_list)-1)
            ]
            return ', '.join(res)