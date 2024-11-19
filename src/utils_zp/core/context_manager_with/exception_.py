from ..base_utils import *


class ExceptionManager:
    def __init__(
        self,
        manager_name='__',
        exception_log_file='',
        exception_log_func=None,
        exception_info='',
        ignore_error=False, 
        info_line_len=80,
    )-> None:
        self.manager_name = str(manager_name)
        if exception_log_file:
            self.exception_log_file = path(exception_log_file)
            make_path(file_path=self.exception_log_file)
        else:
            self.exception_log_file = None
        self.exception_log_func = exception_log_func
        self.exception_info = exception_info
        self.ignore_error = ignore_error
        self.info_line_len = info_line_len
        
    def __enter__(self):
        pass
    
    def __exit__(self, exc_type, exc_value, traceback_):
        _info = {
            'Time': Datetime_().format_str(1),
            'Name': self.manager_name,
            'Info': self.exception_info,
        }
        _log_info = CustomExceptionHandler(info=_info).str
        if self.exception_log_file:
            with open(self.exception_log_file, 'a', encoding='utf8')as f:
                f.write(_log_info)
        if self.exception_log_func:
            self.exception_log_func(_log_info)
        
        return self.ignore_error
    
    
class IgnoreException:
    def __init__(self, print_exc=False) -> None:
        self.print_exc = print_exc
    
    def __enter__(self):
        pass
    
    def __exit__(self, exc_type, exc_value, traceback_):
        if self.print_exc:
            traceback.print_exc()
            print()
        return True


ignore_exception = IgnoreException()
