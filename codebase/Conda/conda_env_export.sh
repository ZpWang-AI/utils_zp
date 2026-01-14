#####
# IMPORTANT
# You can not transfer conda env to a different system (windows, linux)
#####


### conda pack

pip install conda-pack
conda pack -n _env_name_ -o conda_env.tar.gz --ignore-editable-packages

scp _serverA_:conda_env.tar.gz _serverB_:~/tmp

which python # get conda_path
mkdir -p _conda_path_/_new_env_name_
tar -xzf ~/tmp/conda_env.tar.gz -C _conda_path_/_new_env_name_
# source /data/zpwang/anaconda3/envs/zpwang_main/bin/activate
# conda activate zpwang_main
# conda-unpack


### pip list

pip list --format=freeze > env.txt

# install while skipping the failed packages
while read -r package; do pip install "$package" || echo "Failed to install $package"; done < env.txt

# delete distribute, pip, setuptools, wheel, pywin
grep -vE '^(distribute|pip|setuptools|wheel|pywin)' env.txt > env2.txt
pip install -r env2.txt

