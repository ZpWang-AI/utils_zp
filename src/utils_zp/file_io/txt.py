from ._utils_file_io import *


def txt_load(filepath, encoding='utf-8'):
    filepath = load_dump_prepocess(
        filepath=filepath,
        is_load=True,
        valid_suffixes=['.txt'],
    )
    
    with open(filepath, 'r', encoding=encoding)as f:
        obj = f.read()
    return obj


def txt_dump(obj:Union[str, list, tuple], filepath, mode='w', encoding='utf-8'):
    """
    Add '\n' in each line
    """
    filepath = load_dump_prepocess(
        filepath=filepath,
        is_load=False,
        valid_suffixes=['.txt'],
    )
    
    with open(filepath, mode=mode, encoding=encoding)as f:
        if isinstance(obj, (tuple, list)):
            f.writelines([line+'\n' for line in obj])
        elif isinstance(obj, str):
            f.write(obj+'\n')
    

if __name__ == '__main__':
    sample = ['a', 'bcd', 'efg']
    txt_filepath = './tmp.txt'
    txt_dump(sample, txt_filepath)
    loaded_dic = txt_load(txt_filepath)
    print(loaded_dic)
    
    import os
    os.remove(txt_filepath)