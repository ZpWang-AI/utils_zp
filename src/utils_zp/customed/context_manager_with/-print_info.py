# from utils_zp.core import *
from utils_zp import *


_input = []
_output = {}

with PrintInfoManager(
    manager_name='123',
    print_running_time=True,
    input_=_input,
    output_=_output,
    print_func=builtin_print,
    info_line_len=60,
):
    _input.extend([1,2,3])
    _output[1] = 123
    print('xxx')
    1/0
    