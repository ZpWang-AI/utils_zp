"""GPU memory monitoring helpers."""

from __future__ import annotations

import json
import threading
import time
from dataclasses import asdict
from pathlib import Path
from typing import Any

from .query import list_gpu_indices, list_gpus


class GPUMemoryMonitor:
    def __init__(
        self,
        *,
        device_indices: list[int] | None = None,
        output_path: str | Path,
        interval_s: int | float = 3,
        overwrite: bool = True,
        auto_start: bool = True,
    ) -> None:
        self.device_indices = device_indices or list_gpu_indices()
        self.output_path = Path(output_path)
        if self.output_path.suffix != ".jsonl":
            raise ValueError("output_path must end with .jsonl")
        self.interval_s = float(interval_s)
        self._thread: threading.Thread | None = None
        self._running = False
        self._started_at: float | None = None

        self.output_path.parent.mkdir(parents=True, exist_ok=True)
        if overwrite and self.output_path.exists():
            self.output_path.unlink()

        if auto_start:
            self.start()

    def start(self) -> None:
        if self._running:
            return
        self._running = True
        self._started_at = time.time()
        self._write_meta()
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def stop(self) -> None:
        if not self._running:
            return
        self._running = False
        if self._thread is not None:
            self._thread.join()
            self._thread = None

    def close(self) -> None:
        self.stop()

    def _run(self) -> None:
        while self._running:
            self._write_sample()
            time.sleep(self.interval_s)

    def _write_meta(self) -> None:
        gpus = list_gpus(self.device_indices)
        payload = {
            "type": "meta",
            "device_indices": self.device_indices,
            "started_at": self._started_at,
            "gpus": [asdict(gpu) for gpu in gpus],
        }
        self._append_jsonl(payload)

    def _write_sample(self) -> None:
        assert self._started_at is not None
        gpus = list_gpus(self.device_indices)
        payload = {
            "type": "sample",
            "elapsed_s": round(time.time() - self._started_at, 3),
            "memory_used_mb": {str(gpu.index): gpu.used_mb for gpu in gpus},
        }
        self._append_jsonl(payload)

    def _append_jsonl(self, payload: dict[str, Any]) -> None:
        with self.output_path.open("a", encoding="utf-8") as file_obj:
            file_obj.write(json.dumps(payload, ensure_ascii=False) + "\n")


def load_monitor_log(log_path: str | Path) -> list[dict[str, Any]]:
    path = Path(log_path)
    with path.open("r", encoding="utf-8") as file_obj:
        return [json.loads(line) for line in file_obj if line.strip()]


def plot_monitor_log(log_path: str | Path, output_path: str | Path) -> None:
    try:
        import matplotlib.pyplot as plt
    except ModuleNotFoundError as exc:
        if exc.name not in {"matplotlib", "matplotlib.pyplot"}:
            raise
        raise RuntimeError(
            "plot_monitor_log requires matplotlib. Please install matplotlib in the "
            "current environment first."
        ) from exc

    records = load_monitor_log(log_path)
    if not records:
        raise ValueError("monitor log is empty")

    meta = records[0]
    samples = [record for record in records[1:] if record.get("type") == "sample"]
    if not samples:
        raise ValueError("monitor log has no samples")

    gpu_ids = [str(index) for index in meta["device_indices"]]
    xs = [sample["elapsed_s"] for sample in samples]
    total_mem = {
        str(gpu["index"]): gpu["total_mb"]
        for gpu in meta["gpus"]
    }

    for gpu_id in gpu_ids:
        ys = [sample["memory_used_mb"][gpu_id] for sample in samples]
        plt.plot(xs, ys, label=f"cuda:{gpu_id}")
        plt.plot(xs, [total_mem[gpu_id]] * len(xs), linestyle="--", alpha=0.2)

    plt.xlabel("elapsed_s")
    plt.ylabel("used_mb")
    plt.legend()
    plt.tight_layout()
    plt.savefig(output_path)
    plt.close()
