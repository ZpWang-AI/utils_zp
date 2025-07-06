from ..base_utils import *


class PrintInfoManager:
    def __init__(
        self,
        manager_name='__',
        print_running_time=False,
        input_=None,
        output_=None,
        print_func=builtin_print,
        info_line_len=40,
    ) -> None:
        self.manager_name = str(manager_name)
        self.print_running_time = print_running_time
        self.input_ = input_
        self.output_ = output_
        self.print_func = print_func
        
        self.start_time = None
        self.info_line_len = info_line_len
        
    def __enter__(self):
        _info = [gap_line(
            f'{self.manager_name} starts ...', 
            total_len=self.info_line_len, 
            ljust=3,
        )]
        if self.print_running_time:
            self.start_time = Datetime_()
            _info.append(f'> Start time: {Datetime_().format_str(1)}')
        if self.input_ is not None:
            _info.append(f'> Input:\n{str(self.input_)}')
        _info.append(gap_line(fillchar='-', total_len=self.info_line_len))
        self.print_func('\n'.join(_info))
        
    def __exit__(self, *exc_info):
        _info = [gap_line(fillchar='-', total_len=self.info_line_len)]
        if self.print_running_time:
            end_time = Datetime_()
            _info.append(
                f'> Running time: {self.start_time.format_str(1)} - {end_time.format_str(1)}\n'
                f'> Time cost: {end_time - self.start_time}'
            )
        if self.output_ is not None:
            _info.append(f'> Output:\n{str(self.output_)}')
        _info.append(gap_line(
            f'{self.manager_name} ends ...',
            total_len=self.info_line_len,
            ljust=3,
        ))
        self.print_func('\n'.join(_info)+'\n')
        return False


if __name__ == '__main__':
    pass