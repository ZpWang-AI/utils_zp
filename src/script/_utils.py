import sys, os
import subprocess
import datetime
import dataclasses

from typing import *
from pathlib import Path as path


@dataclasses.dataclass
class Script:
    cmd: str
    intro: str
    readme: str
