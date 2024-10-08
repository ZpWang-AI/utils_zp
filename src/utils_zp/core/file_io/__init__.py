from ._utils_file_io import *
from .csv_ import *
# from .file_utils_old import *
from .json_ import *
from .txt_ import *
from .yaml_ import *


def auto_load(filepath, force=True):
    filepath = path(filepath)
    func_map = {
        '.csv': csv_load,
        '.json': json_load,
        '.jsonl': json_load,
        '.txt': txt_load,
        '.yaml': yaml_load
    }
    if filepath.suffix in func_map:
        return func_map[filepath.suffix](filepath=filepath)
    else:
        if not force:
            raise_file_suffix(filepath)
        
        check_file_exists(filepath)
        with open(filepath, 'r', encoding='utf8')as f:
            res = f.read()
        return res


def auto_dump(obj, filepath, force=True):
    filepath = path(filepath)
    func_map = {
        '.csv': csv_dump,
        '.json': json_dump,
        '.jsonl': json_dump,
        '.txt': txt_dump,
        '.yaml': yaml_dump,
    }
    if filepath.suffix in func_map:
        return func_map[filepath.suffix](obj=obj, filepath=filepath)
    else:
        if not force:
            raise_file_suffix(filepath)
        
        with open(filepath, 'w', encoding='utf8')as f:
            f.write(str(obj))
    