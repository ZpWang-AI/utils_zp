from ._utils import *
from .pszp import pszp_func, ProcessInfo

killzp = Script(
    cmd = 'killzp',
    intro = 'ps -aux and grep zp and kill process',
    readme = f'''
`killzp .`

{__file__}
'''.strip()
)


def killzp_cmd():
    if len(sys.argv) == 1:
        print(killzp.readme)
    else:
        killzp_func()


def killzp_func():
    zp_process = pszp_func()
    kill_target = input(
        'kill target (like `a` or `0 1 2`):\n'
    )
    if kill_target.lower() == 'a':
        kill_target = list(range(len(zp_process)))
    else:
        kill_target = list(map(int, kill_target.split()))
    for p in kill_target:
        subprocess.run(f'kill -9 {zp_process[p].pid}', shell=True)
