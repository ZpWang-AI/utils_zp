from __future__ import annotations


def count_model_parameters(model: torch.nn.Module, *, trainable_only: bool = False) -> int:
    import torch
    parameters = model.parameters()
    if trainable_only:
        parameters = (parameter for parameter in parameters if parameter.requires_grad)
    return sum(int(parameter.numel()) for parameter in parameters)
