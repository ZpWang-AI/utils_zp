from .__utils import *


def format_seconds_to_str(seconds:Union[int, float, str]):
    if isinstance(seconds, str):
        seconds = float(seconds)
    if seconds < 1:
        return f'{seconds:.3f}s'
    elif seconds < 30:
        return f'{seconds:.2f}s'
    else:
        return datetime.timedelta(seconds=int(seconds))


def base_decorator_creator(
    print_info=False,
    print_func=builtin_print,
    print_running_time=False,
    print_input=False,
    print_output=False,
    
    exception_log_file='',
    exception_info='',
    exception_log_func=None,
    raise_error=True, 
    default_return=None,
):
    def base_decorator(func):
        @functools.wraps(func)
        def new_func(*args, **kwargs):
            func_name = func.__name__
            if print_info:
                _info = [f'=== {func_name} starts ... '.ljust(30, '=')]
                if print_running_time:
                    start_time_str = cur_time()
                    start_time = cur_time(return_formated_str=False)
                    _info.append(f'> Start time: {start_time_str}')
                if print_input:
                    _info.append(f'> Input:\n  {str(args)}\n  {str(kwargs)}')
                _info.append('-'*30)
                print_func('\n'.join(_info))
            
            try:
                ret = func(*args, **kwargs)
            except Exception as e:
                if exception_log_file:
                    _exception_log_file = path(exception_log_file)
                    make_path(file_path=_exception_log_file)
                    _log_info = '\n'.join([
                        '!' * 80,
                        f'time     : {cur_time()}',
                        f'func name: {func_name}',
                        f'Input    :\n  {str(args)}\n  {str(kwargs)}',
                        f'Info     :\n  {exception_info}' if exception_info else '',
                        f'-' * 80, '',
                        traceback.format_exc(),
                        '\n',
                    ])
                    with open(_exception_log_file, 'a', encoding='utf8')as f:
                        f.write(_log_info)
                    
                    if raise_error:
                        raise e
                    else:
                        ret = dcopy(default_return)
                        
            if print_info:
                _info = [f'=== {func_name} ends ... '.ljust(30, '=')]
                if print_running_time:
                    running_time = cur_time(return_formated_str=False)-start_time
                    running_time = format_seconds_to_str(running_time)
                    _info.append(
                        f'> Running time: {start_time_str} - {cur_time()}\n'
                        f'> Time cost: {running_time}'
                    )
                if print_output:
                    _info.append(f'> Output:\n  {str(ret)}')
                _info.append('-'*30)
                print_func('\n'.join(_info[::-1]))
                
            return ret
        return new_func
    return base_decorator


