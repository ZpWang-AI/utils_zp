from typing import *


def postprocess_generation_res_to_lid(
    pred:Iterable[str]=None,
    gt:Iterable[str]=None,
    label_list:Iterable[str]=None, 
    match_strategy:Literal['complete', 'first exists', 'last exists']='first exists',
    out_of_range_lid:int=None,
    lower_results:bool=True,
) -> dict:
    # process pred gt 
    pred_key, gt_key = None, None
    if pred is None:
        pred = []
    elif isinstance(pred, (list, tuple)):
        pred = list(pred)
    elif isinstance(pred, dict):
        pred_key, pred = zip(*pred.items())
        pred = list(pred)
    else:
        raise f'wrong type of pred: {type(pred)}'
    if gt is None:
        gt = []
    elif isinstance(gt, (list, tuple)):
        gt = list(gt)
    elif isinstance(gt, dict):
        gt_key, gt = zip(*gt.items())
        gt = list(gt)
    else:
        raise f'wrong type of gt: {type(gt)}'

    # get label_list out_of_range_lid
    if not label_list:
        if gt:
            label_list = sorted(set(gt))
        elif pred:
            label_list = sorted(set(pred))
        else:
            raise Exception('pred, gt and label_list not exist')
    label_list = list(map(str, label_list))
    if out_of_range_lid is None:
        out_of_range_lid = len(label_list)
    
    # get score_func, choose the one with max score
    out_of_range_score = -1000
    if match_strategy == 'complete':
        def score_func(x, label):
            return 1 if x == label else out_of_range_score
    elif match_strategy == 'first exists':
        def score_func(x, label):
            return -x.index(label) if label in x else out_of_range_score
    elif match_strategy == 'last exists':
        def score_func(x, label):
            x, label = x[::-1], label[::-1]
            return -x.index(label) if label in x else out_of_range_score
    else:
        raise 'wrong match_strategy'
    
    _label_list = [p.lower()for p in label_list] if lower_results else label_list
    def process_x_to_lid(x):
        x = str(x)
        if lower_results:
            x = x.lower()
        x_lid = max(
            range(len(_label_list)), 
            key=lambda lid:(
                score_func(x, _label_list[lid]), 
                len(_label_list[lid]),
            )
        )
        return (
            x_lid if score_func(x, _label_list[x_lid]) != out_of_range_score
            else out_of_range_lid
        )
    
    processed_pred = list(map(process_x_to_lid, pred))
    processed_gt = list(map(process_x_to_lid, gt))
    if pred_key is not None:
        processed_pred = dict(zip(pred_key, processed_pred))
    if gt_key is not None:
        processed_gt = dict(zip(gt_key, processed_gt))
    
    return {
        'pred': processed_pred,
        'gt': processed_gt,
        'label_list': label_list,
        'match_strategy': match_strategy,
        'out_of_range_lid': out_of_range_lid,
    }
    