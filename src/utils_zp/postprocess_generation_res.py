from typing import *


def postprocess_generation_res_to_lid(
    pred:Iterable[str]=None,
    gt:Iterable[str]=None,
    label_list:Iterable[str]=None, 
    match_strategy:Literal['complete', 'first exists', 'last exists']='complete',
    out_of_range_lid:int=None,
    lower_results=False,
) -> dict:
    if pred is not None:
        pred = list(pred)
    else:
        pred = []
    if gt is not None:
        gt = list(gt)
    else:
        gt = []
        
    if not label_list:
        if gt:
            label_list = sorted(set(gt))
        elif pred:
            label_list = sorted(set(pred))
        else:
            raise Exception('pred, gt and label_list not exist')

    if out_of_range_lid is None:
        out_of_range_lid = len(label_list)
    
    out_of_range_score = -1000
    if match_strategy == 'complete':
        def score_func(x, label):
            if lower_results:
                x, label = x.lower(), label.lower()
            return 1 if x == label else out_of_range_score
    elif match_strategy == 'first exists':
        def score_func(x, label):
            if lower_results:
                x, label = x.lower(), label.lower()
            return x.index(label) if label in x else out_of_range_score
    elif match_strategy == 'last exists':
        def score_func(x, label):
            if lower_results:
                x, label = x.lower(), label.lower()
            x, label = x[::-1], label[::-1]
            return x.index(label) if label in x else out_of_range_score
    
    def process_to_lid(x, label_list):
        x = str(x)
        x_lid = max(
            range(len(label_list)), 
            key=lambda lid:(score_func(x, label_list[lid]), len(label_list[lid]))
        )
        return (
            x_lid if score_func(x, label_list[x_lid]) != out_of_range_score
            else out_of_range_lid
        )
    
    return {
        'pred': [process_to_lid(x, label_list)for x in pred],
        'gt': [process_to_lid(x, label_list)for x in gt],
        'label_list': label_list,
        'match_strategy': match_strategy,
        'out_of_range_lid': out_of_range_lid,
    }