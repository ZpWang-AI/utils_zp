git checkout --orphan main_tmp
# --orphan means create a brand new branch
git add .
git commit -m "Init"
git branch -d main
git branch -m main
git gc
# git rm -r --cached .
