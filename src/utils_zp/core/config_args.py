from .base_utils import *


@dataclasses.dataclass
class ConfigArgs:
    # part1:str = None
    # desc:str = None
    # _version_info_list:Union[list, tuple] = None

    # def __init__(self, *args, **kwargs):
    #     super().__init__(self, *args, **kwargs)

    def __post_init__(self):
        self.format_part()
        # self.create_time:Datetime_ = Datetime_()

    def set_create_time(self, create_time=None):
        if not create_time:
            self.create_time = Datetime_()
        else:
            self.create_time = create_time

    # def __new__(cls):
    #     instance = super().__new__(cls)
    #     return dataclasses.dataclass(instance)

    # @property
    # def version(self): ...
        # raise Exception('TODO')
        # '''
        # join version_info_list with `.`
        # '''
        # return '.'.join(map(str, self._version_info_list))
        
    @property
    def dic(self):
        '''
        dataclasses.asdict(self) \\
        show all attrs
        '''
        return dataclasses.asdict(self)

    @property
    def arg_dic(self):
        '''
        start from self.dic
        - ignore key starts with _ 
        - json.dumps values or get ConfigArgs.arg_dic recursively
        '''
        arg_dic = {}
        for k,v in self.dic.items():
            if k.startswith('_'):
                continue
            elif isinstance(v, ConfigArgs):
                arg_dic[k] = v.arg_dic
            else:
                arg_dic[k] = json.loads(json_dumps_force(v))
        return arg_dic

    def __repr__(self):
        return json.dumps(self.arg_dic, ensure_ascii=False, indent=4)

    def format_part(self):
        dic = self.dic
        for p in range(1000):
            part_name = f'part{p}'
            if part_name not in dic:
                continue
            part_val:str = str(dic[part_name])
            if part_val is not None and part_val[0] != '=':
                self.__setattr__(part_name, gap_line(part_val, ljust=10))
    
    def format_part_in_file(self, filepath):
        '''
        ConfigArgs().format_part_in_file(__file__)

        - search `    partX:str`
        - add annotation auto
        - reorder part num
        '''
        with open(filepath, 'r', encoding='utf8')as f:
            lines = f.readlines()
        part_cnt = 1
        prefix_space = ' '*4
        target_lines:List[str] = []
        for line in lines:
            match = re.search(r'^    (part\d*):\s*str', line)
            if match:
                part_val = self.__getattribute__(match.group(1))
                comment = f'{prefix_space}# {part_val}\n'
                if target_lines and re.match(r'^\s*#', target_lines[-1]):
                    target_lines[-1] = comment
                else:
                    target_lines.append(comment)
                part_cnt += 1
                
            target_lines.append(line)
        
        with open(filepath, 'w', encoding='utf8')as f:
            f.writelines(target_lines)

        print(f'format {filepath} successfully')


_type_var = TypeVar('_args_cls')

def config_args(cls:_type_var) -> Union[_type_var, Type[ConfigArgs]]:
# def config_args(cls:_typevar):
    # new_cls = cls
    cls = dataclasses.dataclass(cls)
    # cls = type(cls.__name__, (cls, ConfigArgs), {})

    # cls.__repr__ = ConfigArgs.__repr__
    # return cls

    @dataclasses.dataclass
    class _cls(cls, ConfigArgs):
        create_time:Datetime_ = Datetime_()

        def __repr__(self):
            return ConfigArgs.__repr__(self)

    return _cls
    # setattr(cls, 'abbbb', 1)
    # cls = dataclasses.dataclass(cls)
    # return cls
    # cls = dataclasses.dataclass(
    #     cls, 
    #     init=True, repr=False, 
    #     eq=True, order=True,
    #     unsafe_hash=False,
    #     frozen=False,
    #     # match_args=True
    # )

    # new_cls: Type[ConfigArgs]
    # # new_cls: 
    # return new_cls
    # cls = dataclasses.dataclass(cls)
    # @functools.wraps(cls)
    # class _cls(ConfigArgs, cls):
    # class _cls(cls, ConfigArgs):
    #     pass
    # _cls: Type[new_type|ConfigArgs]
    # _cls: Type[ConfigArgs]
    # return _cls