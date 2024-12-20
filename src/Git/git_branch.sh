git branch -v

git checkout _branch_or_commit_
git checkout --orphan _branch_  # create a brand new branch without commit history

# set upstream and remote
git fetch origin
git branch -u origin/main main
git remote set-head origin -a
