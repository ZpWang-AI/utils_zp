from ..base import *



def git_update(repo_path, connect_to_github=True):
    import git
    repo = git.Repo(repo_path)
    print(f'> Start updating {path(repo_path).name}')

    for remote in repo.remotes:
        if remote.name.startswith('_'): continue
        if 'github.com' in remote.url and not connect_to_github: continue
        print(f'> pull from {remote.name}')
        remote.pull()
    for remote in repo.remotes:
        if remote.name.startswith('_'): continue
        if 'github.com' in remote.url and not connect_to_github: continue
        print(f'> push to {remote.name}')
        remote.push()
    
    print(f'> Complete updating')
    