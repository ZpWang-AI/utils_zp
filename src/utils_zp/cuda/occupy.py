"""Helpers for occupying GPU memory until a target usage is reached."""

from __future__ import annotations

import threading
import time

from .query import get_gpu


class GPUMemoryOccupier:
    def __init__(
        self,
        *,
        device_indices: list[int] | None = None,
        target_used_mb: int | float | None = None,
        leave_free_mb: int | float | None = None,
        keep_busy: bool = False,
        interval_s: float = 0.1,
        warmup_s: int | float = 10,
        auto_start: bool = True,
    ) -> None:
        self.device_indices = device_indices or [0]

        if leave_free_mb is not None:
            total_mem = get_gpu(self.device_indices[0]).total_mb
            self.target_used_mb = float(total_mem - leave_free_mb)
        elif target_used_mb is not None:
            self.target_used_mb = float(target_used_mb)
        else:
            raise ValueError("either target_used_mb or leave_free_mb must be provided")

        self.keep_busy = keep_busy
        self.interval_s = float(interval_s)
        self.warmup_s = float(warmup_s) + 0.001
        self._keep_occupying = False
        self._run_threads: list[threading.Thread] = []
        self._occupy_thread: threading.Thread | None = None

        if auto_start:
            self.start()

    def start(self) -> None:
        if self._keep_occupying:
            return

        self._keep_occupying = True
        self._run_threads = [
            threading.Thread(target=self._spin, daemon=True, kwargs={"device_index": device_index})
            for device_index in self.device_indices
        ]
        for thread in self._run_threads:
            thread.start()

        self._occupy_thread = threading.Thread(target=self._occupy_loop, daemon=True)
        self._occupy_thread.start()

    def stop(self) -> None:
        if not self._keep_occupying:
            return
        self._keep_occupying = False
        if self._occupy_thread is not None:
            self._occupy_thread.join()
            self._occupy_thread = None
        for thread in self._run_threads:
            thread.join()
        self._run_threads = []

    def close(self) -> None:
        self.stop()

    def _occupy_loop(self) -> None:
        import torch

        time.sleep(self.warmup_s)
        print("occupier starts")
        tensor_stacks = [[[], []] for _ in self.device_indices]

        while self._keep_occupying:
            for device_index, tensor_stack in zip(self.device_indices, tensor_stacks):
                self._occupy_one_gpu(device_index=device_index, tensor_stack=tensor_stack)
            time.sleep(self.interval_s)

        for tensor_stack in tensor_stacks:
            tensor_stack[0].clear()
            tensor_stack[1].clear()
        torch.cuda.empty_cache()
        print("occupier ends")

    def _occupy_one_gpu(self, *, device_index: int, tensor_stack: list[list]) -> None:
        import torch

        def make_tensor(exp: int):
            return torch.arange(1, 10**exp, device=f"cuda:{device_index}")

        used_mb = get_gpu(device_index).used_mb
        for pid, (exp, buffer_mb) in enumerate(zip([7, 5], [80, 1])):
            try:
                while used_mb < self.target_used_mb - buffer_mb:
                    tensor_stack[pid].append(make_tensor(exp))
                    used_mb = get_gpu(device_index).used_mb
            except torch.cuda.OutOfMemoryError:
                pass

        for pid in range(len(tensor_stack)):
            while tensor_stack[pid] and get_gpu(device_index).used_mb >= self.target_used_mb:
                tensor_stack[pid].pop()
                torch.cuda.empty_cache()

    def _spin(self, *, device_index: int) -> None:
        import torch

        x = torch.eye(100, device=f"cuda:{device_index}")
        while self._keep_occupying and self.keep_busy:
            for _ in range(100):
                x *= x
            time.sleep(0.001)
