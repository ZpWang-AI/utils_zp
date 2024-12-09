from ..base_utils import *
from .attr_dic import AttrDict


class ExpArgs(AttrDict):
    def __init__(self, *args, **kwargs) -> None:
        # ============= base_setting =============
        self.part1 = 'base_setting'
        self.desc = 'test'
        self.create_time = Datetime_()
        
        self._version_info_list = []
        
    @property
    def version(self):
        return '.'.join(map(str, self._version_info_list))
            
    def format_part(self):    
        for p in range(1000):
            part_name = f'part{p}'
            if part_name in self:
                part_val:str = self[part_name]
                if part_val[0] != '=':
                    self[part_name] = gap_line(part_val, ljust=11)
    
    def set_create_time(self, create_time=None):
        if not create_time:
            self.create_time = Datetime_()
        else:
            self.create_time = create_time
    
    def format_part_in_file(self, filepath):
        with open(filepath, 'r', encoding='utf8')as f:
            lines = f.readlines()
        part_cnt = 1
        prefix_space = ' '*8
        target_lines:List[str] = []
        for line in lines:
            match = re.search(r'self\.part(\d+)', line)
            if match:
                part_val = self[f'part{match.group(1)}']
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
    

if __name__ == '__main__':
    # sample_args = CustomArgs(test_setting=False)
    # print(sample_args)
    pass