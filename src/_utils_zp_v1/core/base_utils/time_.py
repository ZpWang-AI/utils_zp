import datetime, re
from typing import *


class Datetime_:
    def __init__(self, time_:Union[datetime.datetime, Union[float, int], str, List[int], Tuple[int]]=None):
        if not time_:
            time_ = datetime.datetime.now()
        
        if isinstance(time_, datetime.datetime):
            self.time_ = time_
        elif isinstance(time_, (float, int)):
            self.time_ = datetime.datetime.fromtimestamp(time_)
        else:
            if isinstance(time_, str):
                time_ = re.findall(r'\d+', time_)
            assert len(time_) in [6,7]
            self.time_ = datetime.datetime(*map(int, time_))
    
    @property
    def timestamp(self):
        return self.time_.timestamp()
    
    def format_str(self, format:Union[str, int]='%Y-%m-%d %H:%M:%S.%f') -> str:
        """
        %Y-%m-%d %H:%M:%S.%f
        
        %Y-%m-%d %H:%M:%S
        
        %Y-%m-%d\\_%H-%M-%S
        
        %Y-%m-%d-%H-%M-%S
        
        %Y.%m.%d-%H:%M:%S
        """
        if isinstance(format, int):
            format_list = """
            %Y-%m-%d %H:%M:%S.%f
            
            %Y-%m-%d %H:%M:%S
            
            %Y-%m-%d_%H-%M-%S
            
            %Y-%m-%d-%H-%M-%S
            
            %Y.%m.%d-%H:%M:%S
            """
            format = [line.strip()for line in format_list.split('\n') if line.strip()][format]
        return self.time_.strftime(format=format)

    def __repr__(self):
        return self.format_str()

    def __sub__(self, time_:'Datetime_'):
        return TimeDelta_(self.time_ - time_.time_)
    
    def __lt__(self, other):
        return self.time_ < Datetime_(other).time_
    
    def __le__(self, other):
        return self.time_ <= Datetime_(other).time_
    
    def __gt__(self, other):
        return not self <= other
    
    def __ge__(self, other):
        return not self < other
    
    def __eq__(self, other):
        return self.time_ == Datetime_(other).time_
    
    def __ne__(self, other):
        return not self == other


class TimeDelta_:
    def __init__(self, seconds:Union[datetime.timedelta, int, float, str]=None):
        if seconds is None:
            seconds = .0
        
        if isinstance(seconds, datetime.timedelta):
            self.seconds = seconds.total_seconds()
        else:
            self.seconds = float(seconds)
    
    @property
    def str(self):
        """
        x = seconds
        x < 10: {x.3f}
        x < 100: {x.2f}
        else: str(timedelta(int(x))), like "1 days, 2:34:56"
        """
        return str(self)
    
    def __repr__(self):
        """
        x = seconds
        x < 10: {x.3f}
        x < 100: {x.2f}
        else: str(timedelta(int(x))), like "1 days, 2:34:56"
        """
        seconds = self.seconds
        if seconds < 10:
            return f'{seconds:.3f}s'
        elif seconds < 100:
            return f'{seconds:.2f}s'
        else:
            return str(datetime.timedelta(seconds=int(seconds)))


class StopWatch:
    def __init__(self) -> None:
        self.time_list = []
    
    def record(self):
        self.time_list.append(Datetime_())
    
    def __repr__(self) -> str:
        if not self.time_list:
            return ''
        elif len(self.time_list) == 1:
            return str(self.time_list[0])
        else:
            res = [
                str(self.time_list[p+1]-self.time_list[p])
                for p in range(len(self.time_list)-1)
            ]
            return ', '.join(res)


if __name__ == '__main__':
    print(Datetime_())
    print(datetime.datetime.now())
    print(Datetime_().format_str(0))
    print(Datetime_().format_str(1))
    print(Datetime_().format_str(2))
    import time
    print(Datetime_().timestamp)
    print(time.time())
    
    print(TimeDelta_(datetime.timedelta(1,hours=23,minutes=34,seconds=56,milliseconds=789)))

    sw = StopWatch()
    sw.record()
    time.sleep(1)
    sw.record()
    time.sleep(0.5)
    sw.record()
    print(sw)