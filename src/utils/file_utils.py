import os
import json

from typing import *

from pathlib import Path as path
from collections import defaultdict


def make_path(file_or_dir_path):
    file_or_dir_path = path(file_or_dir_path)
    if file_or_dir_path.is_file():
        file_or_dir_path.parent.mkdir(parents=True, exist_ok=True)
        file_or_dir_path.touch()
    else:
        file_or_dir_path.mkdir(parents=True, exist_ok=True)


def dump_json(target, file_path, mode='w', indent=None):
    with open(file_path, mode=mode, encoding='utf8')as f:
        json.dump(target, f, indent=indent, ensure_ascii=False)
        if mode == 'a':
            f.write('\n')


def load_json(file_path):
    file_path = path(file_path)
    with open(file_path, 'r', encoding='utf8')as f:
        if file_path.suffix == '.json':
            content = json.load(f)
        elif file_path.suffix == '.jsonl':
            content = []
            for line in f.readlines():
                line = line.strip()
                if line:
                    content.append(json.loads(line))
        else:
            raise Exception('wrong file_path')
    return content


def get_json_data_from_dir(root_dir, file_name) -> Dict[str, List[Union[int, float]]]:
    if path(file_name).suffix != '.json':
        return {}
    total_metrics = defaultdict(list)  # {metric_name: [values]}
    for dirpath, dirnames, filenames in os.walk(root_dir):
        if path(dirpath) == path(root_dir):
            continue
        for cur_file in filenames:
            if str(cur_file) == str(file_name):
                with open(path(dirpath, cur_file), 'r', encoding='utf8')as f:
                    cur_metrics = json.load(f)
                for k, v in cur_metrics.items():
                    total_metrics[k].append(v)
    return total_metrics
