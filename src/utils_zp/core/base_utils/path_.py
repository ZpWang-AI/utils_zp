from .import_ import *


def make_path(dir_path=None, file_path=None):
    if file_path is not None:
        file_path = path(file_path)
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.touch()
    if dir_path is not None:
        dir_path = path(dir_path)
        dir_path.mkdir(parents=True, exist_ok=True)


def add_sys_path(cur_path, to_parent_num=0, insert_to_head=True):
    cur_path = path(cur_path)
    for _ in range(to_parent_num):
        cur_path = cur_path.parent
    cur_path = str(cur_path)
    if insert_to_head:
        sys.path.insert(0, cur_path)
    else:
        sys.path.append(cur_path)