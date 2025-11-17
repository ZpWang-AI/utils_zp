# How to add new script

1. create a new py file
2. create a new _utils.Script 
3. add the corresponding func named `{cmd}_cmd`, like `zp_cmd`
4. update __init__.script_list
5. run _update_pyproject_toml.py
6. `pip install -e .` again
