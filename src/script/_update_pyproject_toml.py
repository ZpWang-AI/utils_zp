from utils_zp import *

SRC_DIR = add_sys_path(__file__, 2)


def update_pyproject_toml():
    toml_file = path(__file__).parent.parent.parent / 'pyproject.toml'
    lines = auto_load(toml_file, force=True)
    split_line = '# -----\n'
    before, target, after = lines.split(split_line, 2)
    new_lines = [
        before,
        split_line,
        '[project.scripts]\n'
    ]
    from script import script_list
    for script in script_list:
        new_lines.append(f'{script.cmd} = "script:{script.cmd}_cmd"\n')
    new_lines.append(split_line)
    new_lines.append(after)
    auto_dump(''.join(new_lines), toml_file, force=True)

    print('Update Done!')


if __name__ == '__main__':
    update_pyproject_toml()