from ..file_io import *


def run_shell(shell_filepath=None, cmd:str=None):
    if shell_filepath:
        shell_filepath = path(shell_filepath)
        check_file_exists(shell_filepath)
        shell_cmd = auto_load(shell_filepath)
        os.system(shell_cmd)
        
    if cmd:
        os.system(cmd)
        
        