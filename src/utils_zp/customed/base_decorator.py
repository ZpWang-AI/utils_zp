from .base_utils import *


class _Return:
    def __init__(self):
        self.val = None
    
    def __str__(self):
        if isinstance(self.val, (list, tuple, dict)):
            return json_dumps_force(self.val, indent=4)
        return str(self.val)


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

        from .context_manager_with import PrintInfoManager
        
        @functools.wraps(func)
        def _func(*args, **kwargs):
            func_name = func.__name__
            ret = _Return()
            with PrintInfoManager(
                manager_name=func_name,
                print_running_time=self.print_running_time,
                input_=f'{json_dumps_force(args, indent=4)}\n{json_dumps_force(kwargs, indent=4)}',
                output_=ret,
                print_func=self.print_func,
                info_line_len=40,
            ):
                ret.val = func(*args, **kwargs)
            return ret.val
        return _func

    def exception_decorator(self, func):
        if not any([
            self.exception_log_file,
            self.exception_log_func,
            self.ignore_error,
        ]):
            return func

        from .context_manager_with import ExceptionManager
        
        @functools.wraps(func)
        def _func(*args, **kwargs):
            func_name = func.__name__
            with ExceptionManager(
                manager_name=func_name,
                exception_log_file=self.exception_log_file,
                exception_log_func=self.exception_log_func,
                exception_info={'args': args, 'kwargs': kwargs},
                ignore_error=self.ignore_error,
                info_line_len=40,
            ):
                return func(*args, **kwargs)
            return dcopy(self.default_return)
        return _func
    
    def __call__(self, func):
        func = self.exception_decorator(func)
        func = self.print_info_decorator(func)
        return func
        