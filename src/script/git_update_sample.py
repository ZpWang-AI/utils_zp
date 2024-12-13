from utils_zp import *

add_sys_path(__file__, 2)

from script import git_update


if __name__ == '__main__':
    repos = [
        r'D:\ZpWang\Projects\01.04-utils\utils_zp',
        r'D:\ZpWang\Projects\02.01-IDRR_data\IDRR_data',
        r'D:\ZpWang\Projects\02.08-LLaMA\LLaMA-Factory_zp',
        # r'D:\ZpWang\Projects\02.08-LLaMA\LLaMA-Factory_zp\LLaMA-Factory',
        # r'D:\ZpWang\Projects\02.08-LLaMA\LLaMA-Factory_zp'
    ]
    for repo in repos:
        git_update(repo)