from ._utils import *


pszp = Script(
    cmd = 'pszp',
    intro = 'ps -aux and grep zp',
    readme = f'''
`pszp .`

{__file__}
'''.strip()
)


def pszp_cmd():
    if len(sys.argv) == 1:
        print(pszp.readme)
    else:
        pszp_func()


@dataclasses.dataclass
class ProcessInfo:
    user:str
    pid:str
    cpu:str
    mem:str
    vsz:str
    rss:str
    tty:str
    stat:str
    start:str
    time:str
    command:str

    @property
    def formated_str(self):
        # _output = [self.user, self.pid, self.command]
        return f'{self.user:6s} {int(self.pid):7d} {self.command}'

    @staticmethod
    def show_processes(processes:List['ProcessInfo']):
        for p, line in enumerate(processes):
            line:ProcessInfo
            print(f'> {p:2d} {line.formated_str}')


def pszp_func() -> List[ProcessInfo]:
    process = subprocess.run('ps -aux', shell=True, text=True, capture_output=True)
    process = process.stdout.splitlines()

    res = []
    for line in process:
        if (
            'zp' in line and
            'grep' not in line and
            '.vscode-server' not in line and 
            '/code-server/' not in line and
            'gpustat' not in line and
            'ps -aux' not in line and
            '/tmp/tmp' not in line and
            '/bin/killzp' not in line and
            1
        ):
            res.append(ProcessInfo(*line.split(maxsplit=10)))
            # user, pid, cpu, mem, vsz, rss, tty, stat, start, time, command = line.split()
            # res.append(f'{}')
    
    # print(process[0])
    ProcessInfo.show_processes(res)
    return res
    # print(res)
    "ps -aux | grep -v grep | grep -v .vscode-server | grep -v /code-server/ | grep -v /gpustat | grep zp | grep -v 'ps -aux'"