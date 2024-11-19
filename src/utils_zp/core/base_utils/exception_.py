from .import_ import *
from .format_ import *


class CustomExceptionHandler:
    gap_line_a = '!'*80
    gap_line_b = '-'*80

    def __init__(self, info:dict, exc_str=None, **kwargs) -> None:
        assert isinstance(info, dict)
        self.info = info
        self.info.update(kwargs)
        if exc_str is None:
            self.exc_str:str = traceback.format_exc()
        else:
            self.exc_str:str = str(exc_str)
    
    def __repr__(self) -> str:
        _log_info = [
            self.gap_line_a,
            json_dumps_force(self.info, indent=4),
            self.gap_line_b,
            '',
            self.exc_str,
            '',
        ]
        return '\n'.join(_log_info)
    
    @property
    def str(self):
        return str(self)
    
    @classmethod
    def load_from_file(cls, filepath) -> List["CustomExceptionHandler"]:
        filepath = path(filepath)
        assert filepath.exists()
        
        with open(filepath, 'r', encoding='utf8')as f:
            content = f.read()
            
        records = []
        for record_str in content.split(cls.gap_line_a):
            info_str, exc_str = record_str.split(cls.gap_line_b, 1)
            records.append(cls(
                info=json.loads(info_str), 
                exc_str=exc_str,
            ))
        return records
        