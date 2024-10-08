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
        _info = [f'=== {self.manager_name} starts ... '.ljust(self.info_line_len, '=')]
        if self.print_running_time:
            self.start_time = cur_time(return_formated_str=False)
            _info.append(f'> Start time: {cur_time()}')
        if self.input_ is not None:
            _info.append(f'> Input:\n  {str(self.input_)}')
        _info.append(gap_line(fillchar='-', total_len=self.info_line_len))
        self.print_func('\n'.join(_info))
        
    def __exit__(self, *exc_info):
        _info = [f'=== {self.manager_name} ends ... '.ljust(self.info_line_len, '=')]
        if self.print_running_time:
            running_time = cur_time(return_formated_str=False)-self.start_time
            running_time = format_seconds_to_str(running_time)
            start_time_str = format_datetime(datetime.datetime.fromtimestamp(self.start_time))
            _info.append(
                f'> Running time: {start_time_str} - {cur_time()}\n'
                f'> Time cost: {running_time}'
            )
        if self.output_:
            _info.append(f'> Output:\n  {str(self.output_)}')
        _info.append(gap_line(fillchar='-', total_len=self.info_line_len))
        self.print_func('\n'.join(_info[::-1])+'\n')
        return False


if __name__ == '__main__':
    pass