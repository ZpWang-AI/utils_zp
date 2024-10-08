from ._utils_file_io import *


def yaml_load(filepath, encoding='utf-8'):
    filepath = load_dump_prepocess(
        filepath=filepath,
        is_load=True,
        valid_suffixes=['.yaml'],
    )
    
    import yaml
    with open(filepath, 'r', encoding=encoding)as f:
        obj = yaml.load(f, Loader=yaml.FullLoader)
    return obj
    
    
def yaml_dump(obj, filepath, encoding='utf-8'):
    filepath = load_dump_prepocess(
        filepath=filepath,
        is_load=False,
        valid_suffixes=['.yaml'],
    )
            
    import yaml
    with open(filepath, mode='w', encoding=encoding)as f:
        yaml.dump(obj, f, sort_keys=False)


if __name__ == '__main__':
    dic = {123: '123', '321': 321}
    yaml_filepath = './tmp.json'
    yaml_dump(dic, yaml_filepath)
    loaded_dic2 = yaml_load(yaml_filepath)
    print(loaded_dic2)
    
    import os
    # os.remove(yaml_filepath)