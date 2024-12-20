import re
import os, sys
import json
import collections, copy, itertools, functools
import time, datetime
import tqdm
import traceback
import threading
import random

from typing import *
from pathlib import Path as path
from copy import deepcopy as dcopy
from traceback import format_exc, print_exc
from builtins import print as builtin_print
from functools import wraps

from .format import *


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
        

def cur_time(format='%Y-%m-%d %H:%M:%S', return_formated_str=True) -> Union[str, float]:
    """
    %Y-%m-%d %H:%M:%S
    
    %Y-%m-%d-%H-%M-%S
    
    %Y_%m_%d_%H_%M_%S
    
    %Y.%m.%d-%H:%M:%S
    """
    if return_formated_str:
        return datetime.datetime.now().strftime(format)
    else:
        return time.time()
