from ._utils import *


show_bashrc = Script(
    cmd = 'show_bashrc',
    intro = 'print contents in bashrc_zp.sh and bashrc_zp.local.sh',
    readme = f'''
`show_bashrc .`

print contents in below files:
{path(__file__).parent/'bashrc_zp.sh'}
{path(__file__).parent/'bashrc_zp.local.sh'}

{__file__}
'''.strip()
)



def show_bashrc_cmd():
    if len(sys.argv) == 1:
        print(show_bashrc.readme)
        return

    show_bashrc_()


def show_bashrc_():
    bashrc_zp_path = path(__file__).parent/'bashrc_zp.sh'
    bashrc_zp_local_path = path(__file__).parent/'bashrc_zp.local.sh'
    
    print('>>>', str(bashrc_zp_path))
    print()
    if bashrc_zp_path.exists():
        with open(bashrc_zp_path, 'r', encoding='utf8')as f:
            print(''.join(f.readlines()))
    else:
        print()
    
    print()
    print('>>>', str(bashrc_zp_local_path))
    print()
    if bashrc_zp_local_path.exists():
        with open(bashrc_zp_local_path, 'r', encoding='utf8')as f:
            print(''.join(f.readlines()))
    else:
        print()
