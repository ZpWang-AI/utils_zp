import os, sys
from pathlib import Path as path


with open(path(__file__).parent / 'set_bashrc.sh', 'r', encoding='utf8')as f:
    custom_setting_str = f.read().strip()+'\n'

# os.system('cd ~')
os.chdir(os.path.expanduser("~"))
with open('.bashrc', 'r', encoding='utf8')as f:
    bashrc = f.read()

gap_line = f"# {'='*10}zp{'='*10}\n"
if gap_line in bashrc:
    pre_str, setting_str, post_str = bashrc.split(gap_line)
else:
    pre_str, post_str = bashrc.split('\n\n', 1)
    pre_str += '\n\n'
new_bashrc = gap_line.join([
    pre_str, custom_setting_str, post_str
])
with open('.bashrc', 'w', encoding='utf8')as f:
    f.write(new_bashrc)
    
print(new_bashrc)
print('\n> Please run below cmd.')
print('source ~/.bashrc')
