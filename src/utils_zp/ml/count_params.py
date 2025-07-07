from ..base import format_int


def count_parameters(model):
    return {
        'total': format_int(sum(
            p.numel() for p in model.parameters()
        )),
        'trainable': format_int(sum(
            p.numel() for p in model.parameters() if p.requires_grad
        )),
    }

