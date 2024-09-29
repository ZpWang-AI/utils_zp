from ..__utils import *


class FileUtilsException(Exception):
    pass


def load_dump_prepocess(filepath, is_load, valid_suffixes) -> path:
    filepath = path(filepath)
    
    if is_load:
        if not filepath.exists():
            raise FileUtilsException(f'{filepath} does not exist')
    else:
        filepath.parent.mkdir(parents=True, exist_ok=True)
        filepath.touch()
        
    if filepath.suffix not in valid_suffixes:
        raise FileUtilsException(f'wrong suffix of filepath, which is {filepath}')
    
    return filepath
