import sys, os
import subprocess
import datetime
from pathlib import Path as path


def update_bashrc():
    bashrc_zp_path = path(__file__).parent/'bashrc_zp.sh'
    bashrc_zp_local_path = path(__file__).parent/'bashrc_zp.local.sh'
    bashrc_zp_local_path.touch()

    home_dir = path(os.path.expanduser("~"))
    bashrc_path = home_dir / '.bashrc'
    with open(bashrc_path, 'r', encoding='utf8')as f:
        lines = f.readlines()
    for line in lines:
        if 'bashrc_zp.sh' in line:
            print('bashrc_zp.sh is already in the ~/.bashrc file')
            break
    else:
        with open(bashrc_path, 'a', encoding='utf8')as f:
            f.write(f'\n. {bashrc_zp_path}\n')
            f.write(f'. {bashrc_zp_local_path}\n')
        print('~/.bashrc is updated')
    
    print('=====')
    print('the following .sh files are added')
    print(bashrc_zp_path)
    print(bashrc_zp_local_path)
    print('=====')
    
    print(f'Please run the below cmd.')
    # print('=====')
    print('source ~/.bashrc')
