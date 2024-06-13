import json
import yaml
import datetime

from pathlib import Path as path


class AttrDict(dict):
    def __setattr__(self, __name: str, __value) -> None:
        self.__dict__[__name] = __value
        super().__setitem__(__name, __value)
        
    def __setitem__(self, key: str, value):
        self.__setattr__(key, value)
    
    def set_create_time(self, create_time=None):
        if not create_time:
            self.create_time = datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
        else:
            self.create_time = create_time
            
    @property
    def json(self):
        json_dic = {}
        for k,v in self.items():
            if k.startswith('_'):
                continue
            try:
                json.dumps(v)
                json_dic[k] = v
                continue
            except:
                pass
            try:
                json_dic[k] = str(v)
                continue
            except:
                pass
            raise TypeError(f'wrong type\n{k}: {v}\n{type(v)}')
        return json_dic

    @property
    def yaml(self):
        return self.json
    
    def __repr__(self):
        return json.dumps(self.json, ensure_ascii=False, indent=4)
        
    def merge_dict(self, dic:dict, overwrite_existing=False):
        if overwrite_existing:
            for k, v in dic.items():
                self[k] = v
        else:
            for k, v in dic.items():
                if k in self:
                    self[k] = v
    
    @classmethod
    def from_dict(cls, dic:dict, overwrite_existing=True, **kwargs):
        instance = cls()
        instance.merge_dict(dic, overwrite_existing=overwrite_existing)
        instance.merge_dict(kwargs, overwrite_existing=overwrite_existing)
        return instance

    def dump_json(self, json_path, overwrite=True):
        json_path = path(json_path)
        json_path.parent.mkdir(parents=True, exist_ok=True)
        if not json_path.exists() or overwrite:
            with open(json_path, 'w', encoding='utf8')as f:
                f.write(str(self)+'\n')
    
    @classmethod
    def load_json(cls, json_path, overwrite_existing=True):
        json_path = path(json_path)
        with open(json_path, 'r', encoding='utf8')as f:
            dic = json.load(f)
        return cls.from_dict(dic, overwrite_existing=overwrite_existing)

    def dump_yaml(self, yaml_path, overwrite=True):
        yaml_path = path(yaml_path)
        yaml_path.parent.mkdir(parents=True, exist_ok=True)
        if not yaml_path.exists() or overwrite:
            with open(yaml_path, 'w', encoding='utf8')as f:
                yaml.dump(self.yaml, f, sort_keys=False)
    
    @classmethod
    def load_yaml(cls, yaml_path, overwrite_existing=True):
        yaml_path = path(yaml_path)
        with open(yaml_path, 'r', encoding='utf8')as f:
            dic = yaml.load(f, Loader=yaml.FullLoader)
        return cls.from_dict(dic, overwrite_existing=overwrite_existing)
