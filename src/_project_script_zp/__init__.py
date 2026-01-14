from .gitupdate import gitupdate_cmd
from .updatebashrc import updatebashrc_cmd


def zp_cmd():
    """
    Command line interface for zp.
    
    Behavior:
    - Lists all available script commands with their descriptions
    - Simple, clean output format
    """
    
    # Define all available scripts and their descriptions
    scripts_info = [
        ('updatebashrc', 'Add custom settings to ~/.bashrc file (Linux systems only)'),
        ('gitupdate', 'Update git repository (pull/push main branch for all the remotes)')
    ]
    
    # Print header
    print("Available commands:")
    print("===================")
    
    # List all commands with descriptions
    for cmd_name, description in scripts_info:
        print(f"{cmd_name:<15} {description}")
    


