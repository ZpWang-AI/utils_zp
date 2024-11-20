from .bg_python import run_python_background
from .update_bashrc import update_bashrc


def zp_help():
    print('''
Here're the new commands in utils_zp:

> bgpy
    run python in background
> update_bashrc
    add customized settings into ~/.bashrc
> zp_test
    test command
    '''.strip())


def zp_cmd_test():
    import subprocess
    subprocess.Popen('source ~/.bashrc')
    print(__file__)
    # import subprocess
    # print(1)
    # subprocess.run('ls', shell=True)