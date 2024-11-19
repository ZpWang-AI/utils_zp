from ..base_utils import *


class FileUtilsException(Exception):
    pass


class FileIO:
    @classmethod
    def fileio_prepocess(cls, filepath, is_load, valid_suffixes) -> path:
        filepath = path(filepath)
        
        if filepath.suffix not in valid_suffixes:
            raise FileUtilsException(f'wrong suffix: {filepath}')

        if is_load:
            if not filepath.exists():
                raise FileUtilsException(f'{filepath} does not exist')
        else:
            make_path(file_path=filepath)
        
        return filepath

    @classmethod
    def csv_load(cls, filepath):
        filepath = cls.fileio_prepocess(
            filepath=filepath,
            is_load=True,
            valid_suffixes=['.csv'],
        )
        import pandas as pd
        df = pd.read_csv(filepath)
        return df
    
    @classmethod
    def csv_dump(cls, obj:'pd.DataFrame', filepath):
        filepath = cls.fileio_prepocess(
            filepath=filepath,
            is_load=False,
            valid_suffixes=['.csv'],
        )
        obj.to_csv(filepath, index=False)

    @classmethod
    def json_load(cls, filepath, encoding='utf8'):
        filepath = cls.fileio_prepocess(
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
                objs = [json.loads(line)for line in f.readlines() if line.strip()]
            return objs
    
    @classmethod
    def json_dump(cls, obj, filepath, indent=None, auto_indent=True, encoding='utf-8'):
        filepath = cls.fileio_prepocess(
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
                
        obj_str = json_dumps_force(obj, indent)
        with open(filepath, mode=mode, encoding=encoding)as f:
            f.write(obj_str)
    
    @classmethod
    def txt_load(cls, filepath, encoding='utf8'):
        filepath = cls.fileio_prepocess(
            filepath=filepath,
            is_load=True,
            valid_suffixes=['.txt'],
        )
        
        with open(filepath, 'r', encoding=encoding)as f:
            obj = f.read()
        return obj

    @classmethod
    def txt_dump(cls, obj:Union[str, list, tuple, Any], filepath, mode='w', encoding='utf-8'):
        """
        str: directly write in
        
        tuple or list: str and join by "\\n"
        
        others: str and write in
        """
        filepath = cls.fileio_prepocess(
            filepath=filepath,
            is_load=False,
            valid_suffixes=['.txt'],
        )
        
        with open(filepath, mode=mode, encoding=encoding)as f:
            if isinstance(obj, (tuple, list)):
                f.write('\n'.join(map(str, obj)))
            else:
                f.write(str(obj))

    @classmethod
    def yaml_load(cls, filepath, encoding='utf-8'):
        filepath = cls.fileio_prepocess(
            filepath=filepath,
            is_load=True,
            valid_suffixes=['.yaml'],
        )
        
        import yaml
        with open(filepath, 'r', encoding=encoding)as f:
            obj = yaml.load(f, Loader=yaml.FullLoader)
        return obj
        
    @classmethod
    def yaml_dump(cls, obj, filepath, sort_keys=False, encoding='utf-8'):
        filepath = cls.fileio_prepocess(
            filepath=filepath,
            is_load=False,
            valid_suffixes=['.yaml'],
        )
                
        import yaml
        with open(filepath, mode='w', encoding=encoding)as f:
            yaml.dump(obj, f, sort_keys=sort_keys)


def auto_load(filepath, force=True):
    filepath = path(filepath)
    func_map = {
        '.csv': FileIO.csv_load,
        '.json': FileIO.json_load,
        '.jsonl': FileIO.json_load,
        '.txt': FileIO.txt_load,
        '.yaml': FileIO.yaml_load
    }
    if filepath.suffix in func_map:
        return func_map[filepath.suffix](filepath=filepath)
    else:
        if not force:
            raise FileUtilsException(f'wrong suffix: {filepath}')
        if not filepath.exists():
            raise FileUtilsException(f'{filepath} does not exist')
        
        with open(filepath, 'r', encoding='utf8')as f:
            res = f.read()
        return res


def auto_dump(obj, filepath, force=True):
    filepath = path(filepath)
    func_map = {
        '.csv': FileIO.csv_dump,
        '.json': FileIO.json_dump,
        '.jsonl': FileIO.json_dump,
        '.txt': FileIO.txt_dump,
        '.yaml': FileIO.yaml_dump,
    }
    if filepath.suffix in func_map:
        return func_map[filepath.suffix](obj=obj, filepath=filepath)
    else:
        if not force:
            raise FileUtilsException(f'wrong suffix: {filepath}')
        
        with open(filepath, 'w', encoding='utf8')as f:
            f.write(str(obj))

