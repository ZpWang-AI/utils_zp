import os
import subprocess


def git_update():
    # Step 1: Get all remotes
    try:
        remotes_output = subprocess.check_output(['git', 'remote', '-v'], text=True)
        remotes = {}
        for line in remotes_output.strip().splitlines():
            name, url = line.split()[:2]  # Get remote name and URL
            remotes[name] = url
        print("> Remotes found:\n", remotes, '\n')
    except subprocess.CalledProcessError as e:
        print("> Error fetching remotes:\n", e)
        return

    # Step 2: Git pull from each remote
    for remote, url in remotes.items():
        try:
            print(f'> git fetch {remote}')
            subprocess.run(['git', 'fetch', remote], check=True)
            print(f'> git merge {remote}/main')
            subprocess.run(['git', 'merge', f'{remote}/main'], check=True)
            print()
        except subprocess.CalledProcessError as e:
            print(f"> Error pulling from {remote}:\n{e}")
            return

    # Step 3: Git push to each remote
    for remote in remotes.keys():
        try:
            if 'github.com' in url:
                print(f"> git push {remote} main:main")
                subprocess.run(['git', 'push', remote, 'main:main'], check=True)
            else:
                print(f'> git push {remote} main:zp')
                subprocess.run(['git', 'push', remote, 'main:zp'], check=True)
            print()
        except subprocess.CalledProcessError as e:
            print(f"> Error pushing to {remote}:\n{e}")
            return


if __name__ == '__main__':
    # Example usage
    repo_path = r'D:\ZpWang\Projects\01.04-utils\utils_zp'  # Replace with your repository path
    os.chdir(repo_path)
    git_update()