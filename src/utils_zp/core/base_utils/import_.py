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


if 0:
    import numpy as np
    import pandas as pd
    import torch
    import torch.nn as nn
    import transformers


def import_np():
    global np
    import numpy as np

def import_pd():
    global pd
    import pandas as pd

def import_torch():
    global torch
    import torch
    global nn
    import torch.nn as nn
    
def import_transformer():
    global transformers
    import transformers
    