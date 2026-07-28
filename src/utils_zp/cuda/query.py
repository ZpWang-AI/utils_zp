"""CUDA device query helpers built on top of pynvml."""

from __future__ import annotations

from contextlib import contextmanager
from dataclasses import dataclass
from typing import Generator, Sequence


@dataclass(frozen=True, slots=True)
class GPUInfo:
    index: int
    name: str
    uuid: str
    total_mb: int
    used_mb: int
    free_mb: int
    utilization_gpu: int | None = None
    temperature_c: int | None = None

    @property
    def memory_utilization(self) -> float:
        if self.total_mb <= 0:
            return 0.0
        return self.used_mb / self.total_mb


def list_gpu_indices() -> list[int]:
    with _nvml_session() as pynvml:
        return list(range(pynvml.nvmlDeviceGetCount()))


def get_gpu(index: int) -> GPUInfo:
    gpus = list_gpus([index])
    if not gpus:
        raise ValueError(f"GPU {index} not found")
    return gpus[0]


def list_gpus(device_indices: Sequence[int] | None = None) -> list[GPUInfo]:
    with _nvml_session() as pynvml:
        if device_indices is None:
            device_indices = list(range(pynvml.nvmlDeviceGetCount()))

        gpu_infos: list[GPUInfo] = []
        for index in device_indices:
            handle = pynvml.nvmlDeviceGetHandleByIndex(index)
            mem_info = pynvml.nvmlDeviceGetMemoryInfo(handle)
            name = _decode_if_needed(pynvml.nvmlDeviceGetName(handle))
            uuid = _decode_if_needed(pynvml.nvmlDeviceGetUUID(handle))
            utilization = _safe_gpu_utilization(pynvml, handle)
            temperature = _safe_gpu_temperature(pynvml, handle)
            gpu_infos.append(
                GPUInfo(
                    index=index,
                    name=name,
                    uuid=uuid,
                    total_mb=_bytes_to_mb(mem_info.total),
                    used_mb=_bytes_to_mb(mem_info.used),
                    free_mb=_bytes_to_mb(mem_info.free),
                    utilization_gpu=utilization,
                    temperature_c=temperature,
                )
            )
        return gpu_infos


def _bytes_to_mb(value: int) -> int:
    return int(value) >> 20


def _decode_if_needed(value) -> str:
    if isinstance(value, bytes):
        return value.decode("utf-8")
    return str(value)


def _safe_gpu_utilization(pynvml, handle) -> int | None:
    try:
        return int(pynvml.nvmlDeviceGetUtilizationRates(handle).gpu)
    except Exception:
        return None


def _safe_gpu_temperature(pynvml, handle) -> int | None:
    try:
        return int(pynvml.nvmlDeviceGetTemperature(handle, pynvml.NVML_TEMPERATURE_GPU))
    except Exception:
        return None


@contextmanager
def _nvml_session() -> Generator:
    import pynvml

    try:
        pynvml.nvmlInit()
    except Exception as exc:
        raise RuntimeError(
            "Failed to initialize NVML. Please make sure the machine has a valid "
            "NVIDIA driver and a working libnvidia-ml runtime."
        ) from exc
    try:
        yield pynvml
    finally:
        try:
            pynvml.nvmlShutdown()
        except Exception:
            pass
