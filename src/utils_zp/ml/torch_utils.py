from ..core import *


def tensor_to_list(tensor:'torch.Tensor'):
    return tensor.detach().cpu().tolist()