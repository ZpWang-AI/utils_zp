from ..__utils import *
from .attr_dic import AttrDict


def fill_with_delimiter(s:str):
    return f'{"="*10} {s} {"="*(30-len(s))}'


class ExpArgs(AttrDict):
    def __init__(self) -> None:
        # ========== 'base_setting' ================
        self.part1 = 'base_setting'
        self.desc = 'test'
        
        self._version_info_list = []
        
    @property
    def version(self):
        return '.'.join(self._version_info_list)
        raise "TODO version"
    
    def format_part(self):    
        for p in range(1000):
            part_name = f'part{p}'
            if part_name in self:
                part_val:str = self[part_name]
                if not part_val.startswith('='*10):
                    self[part_name] = fill_with_delimiter(part_val)
    
    @staticmethod
    def format_part_in_file(file_path):
        with open(file_path, 'r', encoding='utf8')as f:
            lines = f.readlines()
        part_cnt = 1
        prefix_space = ' '*8
        target_lines:List[str] = []
        for line in lines:
            if re.match(r'^\s+self\.part\d*\s*=', line):
                part_val = line.split('=')[-1].strip()
                comment = f'{prefix_space}# {fill_with_delimiter(part_val)}\n'
                if re.match(r'^\s*#', target_lines[-1]):
                    target_lines[-1] = comment
                else:
                    target_lines.append(comment)
                target_lines.append(f'{prefix_space}self.part{part_cnt} = {part_val}\n')
                part_cnt += 1
            else:
                target_lines.append(line)
        
        with open(file_path, 'w', encoding='utf8')as f:
            f.writelines(target_lines)
    

if __name__ == '__main__':
    # sample_args = CustomArgs(test_setting=False)
    # print(sample_args)
    
    ExpArgs.format_part_in_file(__file__)
    pass