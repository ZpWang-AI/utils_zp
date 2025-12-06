from ..base import *


class FileDict:
    def __init__(self, data_dir, digest_size:int=2):
        # max database size = 256**digest_size
        self.data_dir = path(data_dir)
        make_path(self.data_dir)

        assert digest_size >= 1
        self.digest_size = digest_size

        from hashlib import blake2b
        self.hash_func = blake2b

    # def _hash(self, s) -> str:
    #     _blake2b = blake2b(str(s).encode(), digest_size=self.digest_size)
    #     return _blake2b.hexdigest()
    
    def _hash_key2filepath(self, key) -> path:
        _blake2b = self.hash_func(str(key).encode(), digest_size=self.digest_size)
        _hash = _blake2b.hexdigest()
        _filepath = self.data_dir
        for i in range(0, (self.digest_size<<1)-2, 2):
            _filepath /= _hash[i:i+2]
        _filepath /= f'{_hash[-2:]}.json'
        return _filepath

    def __iter__(self):
        def _func():
            for _file in oswalk_full_path(self.data_dir, only_file=True):
                _dic:dict = self.__load(_file)
                for k,v in _dic.items():
                    yield k,v
        return _func()
    
    @classmethod
    def __check_key(cls, key:str) -> bool:
        return isinstance(key, (str,int,float,tuple))
    
    @classmethod
    def __dump(cls, filepath:path, _dic):
        if not filepath.parent.exists(): filepath.parent.mkdir(exist_ok=True, parents=True)
        with open(filepath, 'w', encoding=utf8)as f:
            json.dump(_dic, f, ensure_ascii=False)
    
    @classmethod
    def __load(cls, filepath:path):
        if filepath.exists():
            with open(filepath, 'r', encoding=utf8)as f:
                return json.load(f)
        else: 
            return {}

    def __contains__(self, key) -> bool:
        filepath = self._hash_key2filepath(key)
        _dic = self.__load(filepath)
        return key in _dic
        
    def __getitem__(self, key) -> Optional[str]:
        filepath = self._hash_key2filepath(key)
        _dic = self.__load(filepath)
        return _dic.get(key, None)
    
    def __delitem__(self, key):
        filepath = self._hash_key2filepath(key)
        _dic = self.__load(filepath)
        if key in _dic: 
            del _dic[key]
            self.__dump(filepath, _dic)
        
    def __setitem__(self, key, val):
        filepath = self._hash_key2filepath(key)
        _dic = self.__load(filepath)
        _dic[key] = val
        self.__dump(filepath, _dic)
        # auto_dump(_dic, filepath)

    def clear(self):
        shutil.rmtree(self.data_dir)
        make_path(self.data_dir)
