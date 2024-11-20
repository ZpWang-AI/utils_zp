def run_python_background():
    import sys
    import subprocess
    import datetime
    from pathlib import Path as path

    if len(sys.argv) == 1:
        print('''
bgpy [EXE_PATH] PYTHON_PATH

examples:
    bgpy ~test.py ( = bgpy python ~test.py)
    bgpy ~/miniconda3/bin/python ~test.py
        '''.strip())
        return
    elif len(sys.argv) == 2:
        exe_path = 'python'
        py_path = sys.argv[1]
    elif len(sys.argv) == 3:
        exe_path, py_path = sys.argv[1:]
    
    log_path = f'{datetime.datetime.now()}.log'
    cmd = f'{exe_path} "{py_path}"'
    print(cmd)
    
    cmd1 = f'nohup {exe_path} "{py_path}" 1>> "{log_path}" 2>&1 &'
    cmd2 = f'ps -aux | grep -v grep | grep -v /bin/bgpy | grep "{exe_path} {py_path}"'
    gap_line = '*'*60
    with open(log_path, 'w', encoding='utf8')as f:
        f.write(cmd1+'\n')
        f.write(cmd2+'\n')
        f.write(gap_line+'\n\n')
    subprocess.run(cmd1, shell=True)
    subprocess.run(cmd2, shell=True)

    