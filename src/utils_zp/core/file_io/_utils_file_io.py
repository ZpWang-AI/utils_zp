from ..base_utils import *


class FileUtilsException(Exception):
    pass


def check_file_exists(filepath:path):
    if not filepath.exists():
        raise FileUtilsException(f'{filepath} does not exist')


def raise_file_suffix(filepath:path):
    raise FileUtilsException(f'wrong suffix of filepath, which is {filepath}')


def load_dump_prepocess(filepath, is_load, valid_suffixes) -> path:
    filepath = path(filepath)
    
    if is_load:
        check_file_exists(filepath)
    else:
        make_path(file_path=filepath)
        
    if filepath.suffix not in valid_suffixes:
        raise_file_suffix(filepath)
    
    return filepath
