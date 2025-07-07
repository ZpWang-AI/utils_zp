from .import_ import *


def make_path(dir_path=None, file_path=None):
    if file_path is not None:
        file_path = path(file_path)
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.touch()
    if dir_path is not None:
        dir_path = path(dir_path)
        dir_path.mkdir(parents=True, exist_ok=True)


def add_sys_path(cur_path, to_parent_num=0, insert_to_head=True) -> path:
    '''
    for _ in range(to_parent_num):
        cur_path = cur_path.parent
    sys.path.insert(0, cur_path) \\
    return cur_path
    '''
    cur_path = path(cur_path)
    for _ in range(to_parent_num):
        cur_path = cur_path.parent
    if str(cur_path) not in sys.path:
        if insert_to_head:
            sys.path.insert(0, str(cur_path))
        else:
            sys.path.append(str(cur_path))
    return cur_path


def listdir_full_path(dirpath, sort=True):
    dirpath = path(dirpath)
    son_paths = [dirpath/p for p in os.listdir(dirpath)]
    if sort:
        son_paths.sort()
    return son_paths


def oswalk_full_path(dirpath, only_file=True) -> Generator[path, None, None]:
    for dirpath, dirnames, filenames in os.walk(dirpath):
        if only_file:
            for p in filenames:
                yield path(dirpath, p)
        else:
            for p in dirnames+filenames:
                yield path(dirpath, p)
        
