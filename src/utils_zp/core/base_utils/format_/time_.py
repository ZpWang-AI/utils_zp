from datetime import datetime as dtime, timedelta as timed


def format_datetime(_datetime, _format='%Y-%m-%d %H:%M:%S'):
    """
    %Y-%m-%d %H:%M:%S
    
    %Y-%m-%d-%H-%M-%S
    
    %Y_%m_%d_%H_%M_%S
    
    %Y.%m.%d-%H:%M:%S
    """
    import re
    if isinstance(_datetime, str):
        y_m_d_h_m_s = re.findall(r'\d+', _datetime)
        assert len(y_m_d_h_m_s) == 6
        _datetime = dtime(*y_m_d_h_m_s)
    return _datetime.strftime(_format)
    

def format_to_seconds(day=0, hour=0, minute=0, second=0):
    return timed(days=day, hours=hour, minutes=minute, seconds=second).total_seconds()

    
def format_seconds_to_str(seconds):
    if isinstance(seconds, str):
        seconds = float(seconds)
    if seconds < 1:
        return f'{seconds:.3f}s'
    elif seconds < 30:
        return f'{seconds:.2f}s'
    else:
        return str(timed(seconds=int(seconds)))


if __name__ == '__main__':
    print(format_seconds_to_str(format_to_seconds(1000000, 1)))