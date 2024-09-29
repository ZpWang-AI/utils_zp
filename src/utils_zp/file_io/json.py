from .__utils_file_io import *


def json_loads(s, *args, **kwargs):
    return json.loads(s, *args, **kwargs)


def json_dumps(obj, indent, *args, **kwargs):
    return json.dumps(obj=obj, indent=indent, ensure_ascii=False, *args, **kwargs)


def json_load(filepath, encoding='utf-8'):
    filepath = load_dump_prepocess(
        filepath=filepath,
        is_load=True,
        valid_suffixes=['.json', '.jsonl'],
    )
    
    if filepath.suffix == '.json':
        with open(filepath, 'r', encoding=encoding)as f:
            obj = json.load(f)
        return obj
    elif filepath.suffix == '.jsonl':
        with open(filepath, 'r', encoding=encoding)as f:
            objs = [json_loads(line)for line in f.readlines()]
        return objs
    
    
def json_dump(obj, filepath, indent=None, auto_indent=True, encoding='utf-8'):
    filepath = load_dump_prepocess(
        filepath=filepath,
        is_load=False,
        valid_suffixes=['.json', '.jsonl'],
    )
    
    if filepath.suffix == '.json':
        mode = 'w'
    elif filepath.suffix == '.jsonl':
        mode = 'a'
    
    if auto_indent:
        if mode == 'w':
            if indent is None:
                indent = 4
        elif mode == 'a':
            indent = None
            
    obj_str = json_dumps(obj, indent)
    with open(filepath, mode=mode, encoding=encoding)as f:
        f.write(obj_str+'\n')

        
if __name__ == '__main__':
    dic = {123: '123', '321': 321}
    loaded_dic = json_loads(json_dumps(dic, 100))
    json_filepath = './tmp.json'
    json_dump(loaded_dic, json_filepath)
    loaded_dic2 = json_load(json_filepath)
    print(loaded_dic)
    print(loaded_dic2)
    
    import os
    os.remove(json_filepath)
    