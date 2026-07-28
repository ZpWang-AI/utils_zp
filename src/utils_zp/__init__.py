"""utils_zp v2 package."""

from .cuda import (
    GPUInfo,
    GPUMemoryMonitor,
    GPUMemoryOccupier,
    auto_set_cuda_visible,
    get_available_gpus,
    get_gpu,
    list_gpu_indices,
    list_gpus,
    load_monitor_log,
    pick_gpu_indices,
    plot_monitor_log,
    set_cuda_visible_devices,
    wait_for_available_gpus,
)

__version__ = "2.0.0"

__all__ = [
    "__version__",
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
]
