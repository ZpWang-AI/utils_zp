import re
import os, sys
import json
import collections, copy, itertools, functools
import time, datetime
import tqdm, traceback
import subprocess, threading
import random
import dataclasses
import shutil

from typing import *
from pathlib import Path as path
from copy import deepcopy as dcopy
from traceback import format_exc, print_exc
from builtins import print as builtin_print
from functools import wraps
from dataclasses import dataclass, field
from importlib import import_module


class LazyImport:
    def __init__(self, module_name:'str', package:'str'=None):
        self.module_name = module_name
        self.package = package
        self.module = None
    
    def __getattr__(self, name):
        if self.module is None:
            self.module = import_module(self.module_name, self.package)
        return getattr(self.module, name)


np = LazyImport('numpy')
pd = LazyImport('pandas')
torch = LazyImport('torch')
nn = LazyImport('torch.nn')
transformers = LazyImport('transformers')
plt = LazyImport('matplotlib.pyplot')


if 0:
    import numpy as np
    import pandas as pd
    import torch
    import torch.nn as nn
    import transformers
    import matplotlib.pyplot as plt


