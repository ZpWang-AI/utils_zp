from ..base_utils import *


class AttrDict(dict):
    def __init__(self, *args, **kwargs):
        pass
    
    def __new__(cls, *args, **kwargs):
        instance = super().__new__(cls)
        for k,v in dict(*args, **kwargs).items():
            instance[k] = v
        return instance

    def __setattr__(self, __name: str, __value) -> None:
        self.__dict__[__name] = __value
        super().__setitem__(__name, __value)
        
    def __setitem__(self, key: str, value):
        self.__setattr__(key, value)
    
    @property
    def json(self):
        json_dic = {}
        for k,v in self.items():
            if k.startswith('_'):
                continue
            elif isinstance(v, AttrDict):
                json_dic[k] = v.json
            else:
                json_dic[k] = json_dumps_force(v)
        return json_dic

    def __repr__(self):
        return json.dumps(self.json, ensure_ascii=False, indent=4)

    # @property
    # def yaml(self):
    #     return self.json
    
