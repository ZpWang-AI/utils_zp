# from functools import wraps


def gap_line(mid_str=None, fillchar='=', total_len=40):
    if not mid_str:
        return fillchar*total_len
    mid_str = str(mid_str)
    left_len = max(1, (total_len-len(mid_str)-2)//2)
    res = fillchar*left_len + f' {mid_str} '
    right_len = max(1, total_len-len(res))
    return res + fillchar*right_len


# @wraps(gap_line)
# def fill_with_delimiter(*args, **kwargs):
#     return gap_line(*args, **kwargs)


if __name__ == '__main__':
    print(gap_line('123'))
    print(gap_line())