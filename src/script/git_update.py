from ._utils import *


gitupdate = Script(
    cmd = 'gitupdate',
    intro = 'update repo, pull from and push to remotes (branch main)\n\trecursively update submodules',
    readme = f'''
gitupdate REPO_PATH
ignore remote if remote name startswith `_`

examples:
    gitupdate .
    gitupdate ./abc

or do it in below py file
{path(__file__).parent/"git_update_sample.py"}

{__file__}
'''.strip()
)


def gitupdate_cmd(repo_path=None):
    if len(sys.argv) == 1:
        print(gitupdate.readme)
        return

    repo_path = sys.argv[1]
    git_update(repo_path)


def git_update(repo_path, push_to_github=True):
    repo_path = path(repo_path).resolve()
    os.chdir(repo_path)
    print(f'> `{repo_path.stem}` Git Update Starts ...')

    # update submodule first
    # submodules = subprocess.check_output('git config --file .gitmodules --get-regexp path', shell=True, text=True)
    submodules = subprocess.run('git config --file .gitmodules --list', shell=True, text=True, capture_output=True).stdout
    if submodules is not None:
        for line in submodules.strip().splitlines():
            k, v = line.split('=', 1)
            if k.split('.')[-1] == 'path':
                git_update(repo_path/v)

    os.chdir(repo_path)
    # Step 1: Get all remotes
    try:
        remotes_output = subprocess.check_output(['git', 'remote', '-v'], text=True)
        remotes:Dict[str,str] = {}
        print('> Remote found:')
        for line in remotes_output.strip().splitlines():
            name, url = line.split()[:2]  # Get remote name and URL
            if name.startswith('_'):
                continue
            remotes[name] = url
        for name, url in remotes.items():
            print(f'{name:7s}: {url}')
        print()
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
    for remote, url in remotes.items():
        try:
            if 'github.com' in url:
                # if 'zp' in url.lower():
                if push_to_github:
                    print(f"> git push {remote} main:main")
                    subprocess.run(['git', 'push', remote, 'main:main'], check=True)
            else:
                print(f'> git push {remote} main:zp')
                subprocess.run(['git', 'push', remote, 'main:zp'], check=True)
                host_name, host_repo_path = \
                    (url[6:] if url.startswith('ssh://') else url).split(':', 1)
                print(f'> ssh {host_name} \"cd {host_repo_path} && git merge zp\"')
                subprocess.run(f'ssh {host_name} \"cd {host_repo_path} && git merge zp\"', shell=True, check=True)
            print()
        except subprocess.CalledProcessError as e:
            print(f"> Error pushing to {remote}:\n{e}")
            return

    print(f'> ||| {repo_path.stem} ||| Git Update Done!\n')




