from .base_utils import *


def format_seconds_to_str(seconds:Union[int, float, str]):
    if isinstance(seconds, str):
        seconds = float(seconds)
    if seconds < 1:
        return f'{seconds:.3f}s'
    elif seconds < 30:
        return f'{seconds:.2f}s'
    else:
        return datetime.timedelta(seconds=int(seconds))


class BaseDecoratorCreator:
    def __init__(
        self,
        print_info=False,
        print_func=builtin_print,
        print_running_time=False,
        print_input=False,
        print_output=False,
        
        exception_log_file='',
        exception_log_func=None,
        exception_info='',
        ignore_error=False, 
        default_return=None,
    ) -> None:
        self.print_info = print_info
        self.print_func = print_func
        self.print_running_time = print_running_time
        self.print_input = print_input
        self.print_output = print_output
        
        if exception_log_file:
            self.exception_log_file = path(exception_log_file)
            make_path(file_path=self.exception_log_file)
        else:
            self.exception_log_file = None
        self.exception_log_func = exception_log_func
        self.exception_info = exception_info
        self.ignore_error = ignore_error
        self.default_return = default_return
        
    def print_info_decorator(self, func):
        if not self.print_info:
            return func
        
        @functools.wraps(func)
        def _func(*args, **kwargs):
            func_name = func.__name__
            _info = [f'=== {func_name} starts ... '.ljust(30, '=')]
            if self.print_running_time:
                start_time_str = cur_time()
                start_time = cur_time(return_formated_str=False)
                _info.append(f'> Start time: {start_time_str}')
            if self.print_input:
                _info.append(f'> Input:\n  {str(args)}\n  {str(kwargs)}')
            _info.append('-'*30)
            self.print_func('\n'.join(_info))
            
            ret = func(*args, **kwargs)
                        
            _info = [f'=== {func_name} ends ... '.ljust(30, '=')]
            if self.print_running_time:
                running_time = cur_time(return_formated_str=False)-start_time # type: ignore
                running_time = format_seconds_to_str(running_time)
                _info.append(
                    f'> Running time: {start_time_str} - {cur_time()}\n'
                    f'> Time cost: {running_time}'
                )
            if self.print_output:
                _info.append(f'> Output:\n  {str(ret)}')
            _info.append('-'*30)
            self.print_func('\n'.join(_info[::-1]))
                
            return ret
        return _func

    def exception_decorator(self, func):
        if not any([
            self.exception_log_file,
            self.exception_log_func,
            self.ignore_error,
        ]):
            return func
        
        @functools.wraps(func)
        def _func(*args, **kwargs):
            func_name = func.__name__
            try:
                ret = func(*args, **kwargs)
            except Exception as e:
                _log_info = '\n'.join([
                    '!' * 80,
                    f'time     : {cur_time()}',
                    f'func name: {func_name}',
                    f'Input    :\n  {str(args)}\n  {str(kwargs)}',
                    f'Info     :\n  {self.exception_info}' if self.exception_info else '',
                    f'-' * 80, '',
                    traceback.format_exc(),
                    '\n',
                ])
                if self.exception_log_file:
                    with open(self.exception_log_file, 'a', encoding='utf8')as f:
                        f.write(_log_info)
                if self.exception_log_func:
                    self.exception_log_func(_log_info)
                
                if self.ignore_error:
                    ret = dcopy(self.default_return)
                else:
                    raise e
                
            return ret
        return _func
    
    def __call__(self, func):
        func = self.exception_decorator(func)
        func = self.print_info_decorator(func)
        return func
        