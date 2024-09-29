import sys
from pathlib import Path as path


def add_sys_path(cur_path, to_parent_num=0, insert_to_head=True):
    cur_path = path(cur_path)
    for _ in range(to_parent_num):
        cur_path = cur_path.parent
    cur_path = str(cur_path)
    if insert_to_head:
        sys.path.insert(0, cur_path)
    else:
        sys.path.append(cur_path)
        

