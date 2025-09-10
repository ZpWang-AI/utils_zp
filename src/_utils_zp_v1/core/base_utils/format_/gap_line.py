# from functools import wraps


def gap_line(info_str=None, fillchar='=', total_len=40, ljust:int=None):
    if not info_str:
        return fillchar*total_len
    info_str = str(info_str)
    if ljust is None:
        left_len = max(1, (total_len-len(info_str)-2)//2)
    else:
        left_len = ljust
    res = fillchar*left_len + f' {info_str} '
    right_len = max(1, total_len-len(res))
    res += fillchar*right_len
    return res
        


# @wraps(gap_line)
# def fill_with_delimiter(*args, **kwargs):
#     return gap_line(*args, **kwargs)


if __name__ == '__main__':
    print(gap_line('123'))
    print(gap_line())
    