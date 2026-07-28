"""CUDA selection helpers."""

from __future__ import annotations

import os
import time
from typing import Sequence

from .query import GPUInfo, list_gpus


def get_available_gpus(
    *,
    min_free_mb: int = 8000,
    device_indices: Sequence[int] | None = None,
) -> list[GPUInfo]:
    gpus = list_gpus(device_indices=device_indices)
    available = [gpu for gpu in gpus if gpu.free_mb >= min_free_mb]
    return sorted(available, key=lambda gpu: (-gpu.free_mb, gpu.index))


def wait_for_available_gpus(
    *,
    required_count: int = 1,
    min_free_mb: int = 8000,
    device_indices: Sequence[int] | None = None,
    poll_interval_s: int | float = 5,
    verbose: bool = False,
) -> list[GPUInfo]:
    while True:
        available = get_available_gpus(
            min_free_mb=min_free_mb,
            device_indices=device_indices,
        )
        if len(available) >= required_count:
            return available[:required_count]
        if verbose:
            print("waiting for available gpus ...")
        time.sleep(poll_interval_s)


def pick_gpu_indices(
    *,
    required_count: int = 1,
    min_free_mb: int = 8000,
    device_indices: Sequence[int] | None = None,
    wait: bool = False,
    poll_interval_s: int | float = 5,
    verbose: bool = False,
) -> list[int]:
    if wait:
        selected = wait_for_available_gpus(
            required_count=required_count,
            min_free_mb=min_free_mb,
            device_indices=device_indices,
            poll_interval_s=poll_interval_s,
            verbose=verbose,
        )
        return [gpu.index for gpu in selected]

    available = get_available_gpus(
        min_free_mb=min_free_mb,
        device_indices=device_indices,
    )
    return [gpu.index for gpu in available[:required_count]]


def set_cuda_visible_devices(device_indices: Sequence[int] | str) -> str:
    if isinstance(device_indices, str):
        visible = device_indices
    else:
        visible = ",".join(map(str, device_indices))
    os.environ["CUDA_VISIBLE_DEVICES"] = visible
    return visible


def auto_set_cuda_visible(
    *,
    required_count: int = 1,
    min_free_mb: int = 8000,
    device_indices: Sequence[int] | None = None,
    wait: bool = False,
    poll_interval_s: int | float = 5,
    verbose: bool = False,
) -> str:
    selected = pick_gpu_indices(
        required_count=required_count,
        min_free_mb=min_free_mb,
        device_indices=device_indices,
        wait=wait,
        poll_interval_s=poll_interval_s,
        verbose=verbose,
    )
    visible = set_cuda_visible_devices(selected)
    print(f"=== CUDA {visible} ===")
    return visible
