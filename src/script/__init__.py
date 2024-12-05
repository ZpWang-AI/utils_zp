from .bg_python import run_python_background
from .git_update import git_update
from .update_bashrc import update_bashrc


def zp_help():
    print('''
Here're the new commands in utils_zp:

> bgpy
    run python in background
> gitupdate
    update current git repo, pull from remotes and push to remotes (branch zp)
> update_bashrc (only for linux)
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