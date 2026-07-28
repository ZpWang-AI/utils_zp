from __future__ import annotations

import os
import sys
import types
import unittest
from unittest import mock

from utils_zp.cuda import occupy
from utils_zp.cuda.query import GPUInfo


def make_gpu(index: int, *, used_mb: int = 0, total_mb: int = 24000, uuid: str | None = None) -> GPUInfo:
    return GPUInfo(
        index=index,
        name=f"gpu-{index}",
        uuid=uuid or f"GPU-{index}",
        total_mb=total_mb,
        used_mb=used_mb,
        free_mb=total_mb - used_mb,
        utilization_gpu=None,
        temperature_c=None,
    )


class _FakeTorch:
    def __init__(self) -> None:
        self.arange_devices: list[str] = []
        self.eye_devices: list[str] = []
        self.cuda = types.SimpleNamespace(empty_cache=lambda: None)

    def arange(self, start: int, end: int, *, device: str):
        self.arange_devices.append(device)
        return {"start": start, "end": end, "device": device}

    def eye(self, size: int, *, device: str):
        self.eye_devices.append(device)
        return 1


class OccupyTests(unittest.TestCase):
    def test_resolve_torch_device_maps_visible_physical_index_to_logical_index(self) -> None:
        with mock.patch.dict(os.environ, {"CUDA_VISIBLE_DEVICES": "3,7,9"}, clear=False):
            device = occupy._resolve_torch_device_for_physical_gpu(7)

        self.assertEqual(device, "cuda:1")

    def test_resolve_torch_device_supports_uuid_visibility(self) -> None:
        with mock.patch.dict(
            os.environ,
            {"CUDA_VISIBLE_DEVICES": "GPU-7-uuid-prefix,GPU-3-uuid"},
            clear=False,
        ), mock.patch.object(occupy, "get_gpu", return_value=make_gpu(7, uuid="GPU-7-uuid-prefix-full")):
            device = occupy._resolve_torch_device_for_physical_gpu(7)

        self.assertEqual(device, "cuda:0")

    def test_resolve_torch_device_raises_when_gpu_is_not_visible(self) -> None:
        with mock.patch.dict(os.environ, {"CUDA_VISIBLE_DEVICES": "4,5"}, clear=False), mock.patch.object(
            occupy, "get_gpu", return_value=make_gpu(7, uuid="GPU-7-uuid")
        ):
            with self.assertRaisesRegex(RuntimeError, "Physical gpu_id=7 is not visible"):
                occupy._resolve_torch_device_for_physical_gpu(7)

    def test_occupy_one_gpu_uses_mapped_torch_device(self) -> None:
        fake_torch = _FakeTorch()
        occupier = occupy.GPUMemoryOccupier(target_used_mb=100, device_indices=[7], auto_start=False)

        with mock.patch.dict(sys.modules, {"torch": fake_torch}), mock.patch.dict(
            os.environ, {"CUDA_VISIBLE_DEVICES": "3,7"}, clear=False
        ), mock.patch.object(
            occupy,
            "get_gpu",
            side_effect=[make_gpu(7, used_mb=10), make_gpu(7, used_mb=100), make_gpu(7, used_mb=100)],
        ):
            occupier._occupy_one_gpu(device_index=7, tensor_stack=[[], []])

        self.assertEqual(fake_torch.arange_devices, ["cuda:1"])

    def test_spin_uses_mapped_torch_device(self) -> None:
        fake_torch = _FakeTorch()
        occupier = occupy.GPUMemoryOccupier(target_used_mb=100, device_indices=[7], auto_start=False)

        with mock.patch.dict(sys.modules, {"torch": fake_torch}), mock.patch.dict(
            os.environ, {"CUDA_VISIBLE_DEVICES": "3,7"}, clear=False
        ):
            occupier._spin(device_index=7)

        self.assertEqual(fake_torch.eye_devices, ["cuda:1"])


if __name__ == "__main__":
    unittest.main()
