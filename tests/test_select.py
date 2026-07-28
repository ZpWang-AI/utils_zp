from __future__ import annotations

import io
import os
import unittest
from contextlib import redirect_stdout
from unittest import mock

from utils_zp.cuda.query import GPUInfo
from utils_zp.cuda import select


def make_gpu(index: int, free_mb: int) -> GPUInfo:
    total_mb = 24000
    used_mb = total_mb - free_mb
    return GPUInfo(
        index=index,
        name=f"gpu-{index}",
        uuid=f"uuid-{index}",
        total_mb=total_mb,
        used_mb=used_mb,
        free_mb=free_mb,
        utilization_gpu=None,
        temperature_c=None,
    )


class SelectTests(unittest.TestCase):
    def test_get_available_gpus_filters_and_sorts_by_free_memory(self) -> None:
        fake_gpus = [
            make_gpu(index=0, free_mb=3000),
            make_gpu(index=1, free_mb=12000),
            make_gpu(index=2, free_mb=8000),
        ]

        with mock.patch.object(select, "list_gpus", return_value=fake_gpus):
            result = select.get_available_gpus(min_free_mb=5000)

        self.assertEqual([gpu.index for gpu in result], [1, 2])

    def test_pick_gpu_indices_returns_requested_count_when_available(self) -> None:
        fake_gpus = [
            make_gpu(index=2, free_mb=15000),
            make_gpu(index=7, free_mb=14000),
            make_gpu(index=1, free_mb=9000),
        ]

        with mock.patch.object(select, "list_gpus", return_value=fake_gpus):
            result = select.pick_gpu_indices(required_count=2, min_free_mb=8000)

        self.assertEqual(result, [2, 7])

    def test_pick_gpu_indices_should_fail_when_available_gpus_are_insufficient(self) -> None:
        fake_gpus = [make_gpu(index=2, free_mb=12000)]

        with mock.patch.object(select, "list_gpus", return_value=fake_gpus):
            with self.assertRaisesRegex(
                ValueError,
                "Not enough available GPUs: required_count=2, available_count=1",
            ):
                select.pick_gpu_indices(required_count=2, min_free_mb=8000, wait=False)

    def test_auto_set_cuda_visible_updates_environment_and_prints_selection(self) -> None:
        with mock.patch.object(select, "pick_gpu_indices", return_value=[7, 3]), mock.patch.dict(
            os.environ, {}, clear=False
        ):
            stdout = io.StringIO()
            with redirect_stdout(stdout):
                visible = select.auto_set_cuda_visible(required_count=2)
            current_visible = os.environ["CUDA_VISIBLE_DEVICES"]

        self.assertEqual(visible, "7,3")
        self.assertEqual(current_visible, "7,3")
        self.assertEqual(stdout.getvalue(), "=== CUDA 7,3 ===\n")


if __name__ == "__main__":
    unittest.main()
