conda create --name _env_ python=3.10 --yes
conda create --name _env_ --clone _source_env_

conda remove -n _env_ _package_
conda env remove -n _env_

conda env list

