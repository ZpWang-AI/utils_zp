from ._utils import *


bgpy = Script(
    cmd = 'bgpy',
    intro = 'run python in background',
    readme = f'''
bgpy [EXE_PATH] PYTHON_PATH

examples:
    bgpy ~test.py ( = bgpy python ~test.py)
    bgpy ~/miniconda3/bin/python ~test.py

{__file__}
'''.strip()
)



def bgpy_cmd():
    if len(sys.argv) == 1:
        print(bgpy.readme)
        return
    elif len(sys.argv) == 2:
        exe_path = 'python'
        py_path = sys.argv[1]
    elif len(sys.argv) == 3:
        exe_path, py_path = sys.argv[1:]

    run_python_background(exe_path, py_path)


def run_python_background(exe_path, py_path):
    assert path(py_path).exists()
    
    log_path = path(py_path).parent / (
        datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S") + \
        path(py_path).name + \
        '.log'
    ) 
    # cmd = f'{exe_path} "{py_path}"'
    # print(cmd)
    
    cmd1 = f'nohup {exe_path} "{py_path}" 1>> "{log_path}" 2>&1 &'
    print(cmd1+'\n')
    cmd2 = f'ps -aux | grep -v grep | grep -v /bin/bgpy | grep "{exe_path} {py_path}"'
    gap_line = '*'*60
    with open(log_path, 'w', encoding='utf8')as f:
        f.write(cmd1+'\n\n')
        f.write(cmd2+'\n\n')

    subprocess.run(cmd1, shell=True)
    process_info = subprocess.run(cmd2, shell=True, text=True, capture_output=True)

    with open(log_path, 'a', encoding='utf8')as f:
        f.write(process_info.stdout+'\n')
        f.write(gap_line+'\n\n')
    
    print(f'> log:')
    print(log_path.absolute())