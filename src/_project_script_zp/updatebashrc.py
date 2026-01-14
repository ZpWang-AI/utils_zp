import sys
from pathlib import Path

# Define relevant file paths
shell_dir = Path(__file__).parent.parent.parent / 'shell'
bashrc_zp_path = shell_dir / 'bashrc_zp.sh'
bashrc_zp_local_path = shell_dir / 'bashrc_zp.local.sh'
home_dir = Path.home()
bashrc_path = home_dir / '.bashrc'


def updatebashrc_cmd():
    """
    Interactively update ~/.bashrc file to add custom settings.
    
    Features:
    1. Always print usage instructions
    2. Always ask for user confirmation before updating
    3. Perform update only if user confirms
    """
    # Print usage instructions
    usage_info = f"""=== Bashrc Updater ===
Add custom settings to ~/.bashrc file (Linux systems only)

Function:
  Updates ~/.bashrc to add references to these files:
  - {bashrc_zp_path}
  - {bashrc_zp_local_path}
  
Current script: {__file__}
"""
    
    print(usage_info)

    # Check if running on Linux
    if sys.platform != "linux":
        print(f"Warning: Current system is {sys.platform}, this feature is designed for Linux")
        print("Continue anyway? (may affect configuration files on other systems)")
        confirm = input("Type 'yes' to continue: ").strip().lower()
        if confirm != 'yes':
            print("Operation cancelled")
            return
    
    # Ask for user confirmation
    while True:
        user_input = input("Do you want to update ~/.bashrc now? (y/n): ").strip().lower()
        
        if user_input in ['y', 'yes']:
            print("\nUpdating ~/.bashrc...")
            _perform_update()
            break
        elif user_input in ['n', 'no']:
            print("\nOperation cancelled")
            break
        else:
            print("Please enter 'y' or 'n'")


def _perform_update():
    """
    Perform the actual ~/.bashrc update operation
    """
    # Ensure local file exists (create empty file if not)
    assert bashrc_zp_path.exists()
    bashrc_zp_local_path.touch(exist_ok=True)
    
    # Read existing ~/.bashrc content
    try:
        with open(bashrc_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
    except FileNotFoundError:
        print(f"Warning: {bashrc_path} does not exist, will create new file")
        lines = []
    except Exception as e:
        print(f"Error reading {bashrc_path}: {e}")
        return
    
    # Ensure the last line has a newline character
    if not lines or lines[-1] != '\n':
        lines.append('\n')
    
    # Prepare the two lines to add
    source_line_a = f'. {bashrc_zp_path}\n'
    source_line_b = f'. {bashrc_zp_local_path}\n'
    
    # Track if we made changes
    made_changes = False
    
    # Update or add first line (bashrc_zp.sh)
    for i, line in enumerate(lines):
        if 'bashrc_zp.sh' in line:
            if lines[i] != source_line_a:
                lines[i] = source_line_a
                made_changes = True
            break
    else:
        lines.append(source_line_a)
        made_changes = True
    
    # Update or add second line (bashrc_zp.local.sh)
    for i, line in enumerate(lines):
        if 'bashrc_zp.local.sh' in line:
            if lines[i] != source_line_b:
                lines[i] = source_line_b
                made_changes = True
            break
    else:
        lines.append(source_line_b)
        made_changes = True
    
    # Write updated content back to file
    try:
        with open(bashrc_path, 'w', encoding='utf-8') as f:
            f.writelines(lines)
        
        if made_changes:
            print("✓ successfully updated")
        else:
            print("✓ already updated (no changes needed)")
        
        print()
        print("Run this command to apply changes:")
        print("  source ~/.bashrc")
        
    except Exception as e:
        print(f"Error writing to {bashrc_path}: {e}")
        print("Update failed")


if __name__ == "__main__":
    updatebashrc_cmd()


