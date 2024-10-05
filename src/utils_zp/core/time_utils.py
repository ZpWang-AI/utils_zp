from .base_utils import *
from .base_decorator import format_seconds_to_str


class Stopwatch:
    def __init__(self) -> None:
        self.time_list = []
    
    def record(self):
        self.time_list.append(cur_time(return_formated_str=False))
    
    def __repr__(self) -> str:
        if not self.time_list:
            return ''
        elif len(self.time_list) == 1:
            return datetime.fromtimestamp(self.time_list[0])
        else:
            res = [format_seconds_to_str(
                self.time_list[p+1]-self.time_list[p] 
                for p in range(len(self.time_list)-1)
            )]
            return ', '.join(res)
            
    