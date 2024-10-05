from .csv import *
# from .file_utils_old import *
from .json import *
from .txt import *


def auto_load(filepath):
    filepath = path(filepath)
    func_map = {
        '.csv': csv_load,
        '.json': json_load,
        '.jsonl': json_load,
        '.txt': txt_load,
    }
    if filepath.suffix in func_map:
        return func_map[filepath.suffix](filepath=filepath)
    else:
        raise Exception(f'wrong suffix of {filepath}')


def auto_dump(obj, filepath):
    filepath = path(filepath)
    func_map = {
        '.csv': csv_dump,
        '.json': json_dump,
        '.jsonl': json_dump,
        '.txt': txt_dump,
    }
    if filepath.suffix in func_map:
        return func_map[filepath.suffix](obj=obj, filepath=filepath)
    else:
        raise Exception(f'wrong suffix of {filepath}')