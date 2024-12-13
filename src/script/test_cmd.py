from ._utils import *


zp_test = Script(
    cmd = 'zp_test',
    intro = 'test command',
    readme = ''
)


def zp_test_cmd():
    import subprocess
    subprocess.Popen('source ~/.bashrc')
    print(__file__)
    # import subprocess
    # print(1)
    # subprocess.run('ls', shell=True)