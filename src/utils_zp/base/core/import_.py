import re
import os, sys
import json
import math
import collections, copy, itertools, functools
import time, datetime
import tqdm, traceback
import subprocess, threading
import random
import dataclasses
import shutil

from typing import *
from pathlib import Path
path = Path
from copy import deepcopy as dcopy
from collections import defaultdict
from traceback import format_exc, print_exc
from builtins import print as builtin_print
from functools import wraps
from dataclasses import dataclass, field
from importlib import import_module


class LazyImport:
    def __init__(self, module_name:'str', package:'str'=None, function_name:'str'=None):
        self.module_name = module_name
        self.package = package
        self.function_name = function_name
        self._module = None
        self._function = None
    
    @property
    def module(self):
        if self._module is None:
            self._module = import_module(self.module_name, self.package)
        return self._module
    
    @property
    def function(self):
        assert self.function_name
        if self._function is None:
            self._function = getattr(self.module, self.function_name)
        return self._function

    def __getattr__(self, name):
        if self.function_name is None:
            return getattr(self.module, name)        
        else:
            return getattr(self.function, name) 

    def __call__(self, *args, **kwargs):
        return self.function(*args, **kwargs)
    
    def __repr__(self):
        module_name = self.package+self.module_name if self.package else self.module_name
        if self.function_name:
            if self._function is None:
                return f"<LazyImport '{module_name}.{self.function_name}' (not loaded)>"
            else:
                return f"<LazyImport '{module_name}.{self.function_name}' (loaded)>"
        else:
            if self._module is None:
                return f"<LazyImport module '{module_name}' (not loaded)>"
            else:
                return f"<LazyImport module '{module_name}' (loaded)>"
            

np = LazyImport('numpy')
pd = LazyImport('pandas')
torch = LazyImport('torch')
nn = LazyImport('torch.nn')
transformers = LazyImport('transformers')
plt = LazyImport('matplotlib.pyplot')
cv2 = LazyImport('cv2')


if 0:
    # import numpy as np
    # import pandas as pd
    # import torch
    # import torch.nn as nn
    # import transformers
    # import matplotlib.pyplot as plt
    pass

