"""utils_zp v2 package."""

from __future__ import annotations

from importlib import import_module
from typing import Any

__version__ = "2.0.0"

__all__ = [
    "__version__",
    "GPUInfo",
    "GPUMemoryMonitor",
    "GPUMemoryOccupier",
    "auto_set_cuda_visible",
    "count_model_parameters",
    "get_available_gpus",
    "get_gpu",
    "list_gpu_indices",
    "list_gpus",
    "load_monitor_log",
    "pick_gpu_indices",
    "plot_monitor_log",
    "set_cuda_visible_devices",
    "wait_for_available_gpus",
]

_CUDA_EXPORTS = {
    "GPUInfo",
    "GPUMemoryMonitor",
    "GPUMemoryOccupier",
    "auto_set_cuda_visible",
    "get_available_gpus",
    "get_gpu",
    "list_gpu_indices",
    "list_gpus",
    "load_monitor_log",
    "pick_gpu_indices",
    "plot_monitor_log",
    "set_cuda_visible_devices",
    "wait_for_available_gpus",
}

_PRETRAINED_MODEL_EXPORTS = {
    "count_model_parameters",
}


def __getattr__(name: str) -> Any:
    if name in _CUDA_EXPORTS:
        cuda_module = import_module(".cuda", __name__)
        value = getattr(cuda_module, name)
        globals()[name] = value
        return value
    if name in _PRETRAINED_MODEL_EXPORTS:
        pretrained_model_module = import_module(".pretrained_model_parameter_count", __name__)
        value = getattr(pretrained_model_module, name)
        globals()[name] = value
        return value
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
