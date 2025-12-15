from ._utils import *


update_bashrc = Script(
    cmd = 'update_bashrc',
    intro = 'add customized settings into ~/.bashrc (only for linux)',
    readme = f'''
`update_bashrc .`

write in below files:
{path(__file__).parent/'bashrc_zp.sh'}
{path(__file__).parent/'bashrc_zp.local.sh'}

{__file__}
'''.strip()
)



def update_bashrc_cmd():
    if len(sys.argv) == 1:
        print(update_bashrc.readme)
        return

    update_bashrc_()


def update_bashrc_():
    bashrc_zp_path = path(__file__).parent/'bashrc_zp.sh'
    bashrc_zp_local_path = path(__file__).parent/'bashrc_zp.local.sh'
    bashrc_zp_local_path.touch()

    home_dir = path(os.path.expanduser("~"))
    bashrc_path = home_dir / '.bashrc'
    with open(bashrc_path, 'r', encoding='utf8')as f:
        lines = f.readlines()
    
    if not lines or lines[-1]!='\n': lines.append('\n')
    linea = f'. {bashrc_zp_path}\n'
    lineb = f'. {bashrc_zp_local_path}\n'
    for p, line in enumerate(lines):
        if 'bashrc_zp.sh' in line:
            lines[p] = linea; break
    else: lines.append(linea)
    for p, line in enumerate(lines):
        if 'bashrc_zp.local.sh' in line:
            lines[p] = lineb; break
    else: lines.append(lineb)

    with open(bashrc_path, 'w', encoding='utf8')as f:
        f.writelines(lines)
        print('~/.bashrc is updated')
    
    print('=====')
    print('the following .sh files are added')
    print(bashrc_zp_path)
    print(bashrc_zp_local_path)
    print('=====')
    
    print(f'Please run the below cmd.')
    # print('=====')
    print('source ~/.bashrc')
