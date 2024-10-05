from .base_utils import *
# import datetime, time
# import json
# import os, sys
# import pandas as pd
# import traceback

# from typing import *
# from pathlib import Path as path
# from collections import defaultdict
# from functools import wraps
# from copy import deepcopy as dcopy


def print_sep(sep='-', num=20):
    print(sep*num)


# def iterations_are_equal(iterations:Iterable[Iterable[Union[str, int, float]]]):
#     iterations = list(iterations)
#     if not len(iterations):
#         return True
#     first = sorted(iterations[0])
#     return (
#         all(
#             len(iterations[p])==len(iterations[0]) for p in range(1,len(iterations))
#         ) and 
#         all(
#             sorted(iterations[p])==first for p in range(1,len(iterations))
#         )
#     )


def build_dict_from_df_or_dicts(
    df_or_dicts:Union[pd.DataFrame, Iterable[dict]],
    key_col_name:str, val_col_name:str,
    make_key_str=False,
):
    if isinstance(df_or_dicts, pd.DataFrame):
        key_col = df_or_dicts[key_col_name]
        val_col = df_or_dicts[val_col_name]
    else:
        key_col, val_col = [], []
        for dic in df_or_dicts:
            key_col.append(dic[key_col_name])
            val_col.append(dic[val_col_name])
    if make_key_str:
        key_col = list(map(str, key_col))    
    return dict(zip(key_col, val_col))
    

def clock_decorator(func):
    @wraps(func)
    def new_func(*args, **kwargs):
        print(f'{func.__name__} starts')
        start_time = time.time()
        res = func(*args, **kwargs)
        running_time = time.time()-start_time
        running_time = running_time if running_time < 3 else int(running_time)
        running_time = datetime.timedelta(seconds=running_time)
        print(f'{func.__name__} ends, runtime: {running_time}')
        return res
    return new_func


def input_output_decorator(func):
    @wraps(func)
    def new_func(*args, **kwargs):
        print('='*20)
        print(f'{func.__name__} Input:\n  {args} {kwargs}')
        print('-'*20)
        res = func(*args, **kwargs)
        print('-'*20)
        print(f'{func.__name__} Output:\n  {res}')
        print('='*20)
        return res
    return new_func


def catch_exception_decorator_creator(
    exception_log_file='./exception_log.txt',
    raise_error=True,
    default_return=None,
):
    def catch_exception_decorator(func):
        @wraps(func)
        def new_func(*args, **kwargs):
            try:
                res = func(*args, **kwargs)
                return res
            except Exception as e:
                if exception_log_file:
                    _exception_log_file = path(exception_log_file)
                    _exception_log_file.parent.mkdir(parents=True, exist_ok=True)
                    _exception_log_file.touch()
                    with open(_exception_log_file, 'a', encoding='utf8')as f:
                        exception_log = '\n'.join([
                            '!'*40,
                            f'time     : {str(datetime.datetime.today())}',
                            f'func name: {func.__name__}',
                            f'Input    :\n  {str(args)}\n  {str(kwargs)}',
                            '-'*40+'\n',
                            traceback.format_exc()+'\n',
                        ])
                        f.write(exception_log)
                if raise_error:
                    raise e
                else:
                    return default_return
        return new_func
    return catch_exception_decorator


def round_dict_values(dic, k):
    return {
        key: f'{value:.{k}f}' if isinstance(value, float) else value
        for key, value in dic.items()
    }
    

def dict_to_defaultdict(dic, default_type=dict):
    new_dic = collections.defaultdict(default_type)
    new_dic.update(dic)
    return new_dic


def format_element_to_shape(target, json_indent=True):
    target = dcopy(target)
    if hasattr(target, 'shape'):
        res = str(target.shape)
    elif isinstance(target, dict):
        res = {k:format_element_to_shape(v, False)for k,v in target.items()}
    else:
        try:
            target = list(target)
            res = [format_element_to_shape(p, False)for p in target]
            if res and all(res[0]==p for p in res):
                res = f'(*{len(res)}, {res[0]})'
        except:
            # from traceback import format_exc
            # print(format_exc())
            print(target)
            raise Exception(f'wrong type {type(target)}')
    return json.dumps(res, indent=4) if json_indent else res
    
    
if __name__ == '__main__':
    @clock_decorator
    @input_output_decorator
    def f(a=1,b=2):
        time.sleep(3)
        return a+b
    
    f(123,23)
    