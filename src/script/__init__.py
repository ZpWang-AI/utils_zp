from ._utils import *
from .bg_python import *
from .git_update import *
from .test_cmd import *
from .update_bashrc import *


zp = Script(
    cmd = 'zp',
    intro = 'new command help',
    readme = '',
)


script_list = [
    zp,
    bgpy,
    gitupdate,
    update_bashrc,
    zp_test,
]


def zp_cmd():
    print('Here\'re the new commands in utils_zp:\n')
    for script in script_list:
        print(f'> {script.cmd}\n\t{script.intro}')
    print('\nSee details by input corresponding cmd.')

