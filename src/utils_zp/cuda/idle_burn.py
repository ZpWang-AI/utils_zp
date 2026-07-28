"""Helpers for opportunistic GPU stress testing.

This module is mainly used to:
- generate a lightweight torch workload on GPU
- add load only when a target GPU is relatively idle
- do quick stress tests or contention experiments

It is more experimental than the core query/select/monitor/occupy modules,
but the file name is kept explicit because the purpose is straightforward.
"""

from __future__ import annotations

import os
import subprocess
import time
from dataclasses import dataclass
from typing import Callable


@dataclass(frozen=True, slots=True)
class GpuUsageSnapshot:
    gpu_id: int
    gpu_utilization: int
    memory_used_mb: int
    memory_total_mb: int

    @property
    def memory_free_mb(self) -> int:
        return self.memory_total_mb - self.memory_used_mb


@dataclass(frozen=True, slots=True)
class GpuProcessSnapshot:
    gpu_id: int
    pid: int
    process_name: str
    used_memory_mb: int


@dataclass(frozen=True, slots=True)
class QpsCalibrationSample:
    requested_qps: float
    achieved_qps: float
    baseline_gpu_utilization: float
    average_gpu_utilization: float
    added_gpu_utilization: float


def query_nvidia_smi_usage(gpu_id: int) -> GpuUsageSnapshot:
    """Query a single GPU from `nvidia-smi`."""
    cmd = [
        "nvidia-smi",
        "--query-gpu=index,utilization.gpu,memory.used,memory.total",
        "--format=csv,noheader,nounits",
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, check=False)
    output = ((result.stdout or "") + (result.stderr or "")).strip()

    if result.returncode != 0:
        raise RuntimeError(f"nvidia-smi failed: {output}")

    for line in output.splitlines():
        parts = [item.strip() for item in line.split(",")]
        if len(parts) != 4:
            continue

        index, util, mem_used, mem_total = parts
        if int(index) != int(gpu_id):
            continue

        return GpuUsageSnapshot(
            gpu_id=int(index),
            gpu_utilization=int(util),
            memory_used_mb=int(mem_used),
            memory_total_mb=int(mem_total),
        )

    raise RuntimeError(
        "Failed to parse nvidia-smi output. "
        f"gpu_id={gpu_id} may not exist. Raw output: {output!r}"
    )


def list_gpu_processes(gpu_id: int, *, include_self: bool = False) -> list[GpuProcessSnapshot]:
    """List compute processes on the target GPU using `nvidia-smi`.

    By default, the current Python process is filtered out so callers can ask
    whether there are "other" programs already using the GPU.
    """
    target_uuid = _query_gpu_uuid(gpu_id)
    cmd = [
        "nvidia-smi",
        "--query-compute-apps=gpu_uuid,pid,process_name,used_gpu_memory",
        "--format=csv,noheader,nounits",
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, check=False)
    output = ((result.stdout or "") + (result.stderr or "")).strip()

    if result.returncode != 0:
        # Some nodes return non-zero when there is no compute app at all.
        lowered = output.lower()
        if "no running" in lowered or "no devices were found" in lowered:
            return []
        raise RuntimeError(f"nvidia-smi process query failed: {output}")

    current_pid = os.getpid()
    processes: list[GpuProcessSnapshot] = []
    for line in output.splitlines():
        parts = [item.strip() for item in line.split(",")]
        if len(parts) != 4:
            continue

        process_gpu_uuid, pid_str, process_name, used_memory_str = parts
        if process_gpu_uuid != target_uuid:
            continue

        pid = int(pid_str)
        if not include_self and pid == current_pid:
            continue

        processes.append(
            GpuProcessSnapshot(
                gpu_id=gpu_id,
                pid=pid,
                process_name=process_name,
                used_memory_mb=int(used_memory_str),
            )
        )
    return processes


def list_significant_gpu_processes(
    gpu_id: int,
    *,
    include_self: bool = False,
    min_used_memory_mb: int = 100,
) -> list[GpuProcessSnapshot]:
    """List GPU processes whose memory usage is large enough to matter."""
    _validate_non_negative(min_used_memory_mb, "min_used_memory_mb")
    return [
        process
        for process in list_gpu_processes(gpu_id, include_self=include_self)
        if process.used_memory_mb > min_used_memory_mb
    ]


def create_fp16_linear_workload(
    *,
    input_dim: int = 2000,
    output_dim: int = 2000,
    batch_size: int = 1000,
    device: str = "cuda",
):
    """Create a small fp16 linear forward workload for GPU stress testing."""
    import torch

    if not torch.cuda.is_available():
        raise RuntimeError("CUDA is not available")

    model = torch.nn.Linear(input_dim, output_dim).to(device).half().eval()
    inputs = torch.randn(batch_size, input_dim, dtype=torch.float16, device=device)
    return model, inputs


def run_workload_step(model, inputs) -> None:
    """Run one workload step and release the output immediately."""
    import torch

    # Use inference mode so the stress loop measures forward workload rather than autograd overhead.
    with torch.inference_mode():
        output = model(inputs)
        del output


def stress_gpu_to_target_usage(
    *,
    gpu_id: int = 0,
    target_usage_when_idle: int = 90,
    target_usage_when_shared: int = 30,
    significant_process_memory_mb: int = 1000,
    calibration_step_duration_s: int | float = 1.0,
    calibration_stop_usage: int | float = 50.0,
    control_update_interval_s: int | float = 1.0,
    calibration_start_qps: int | float = 10.0,
    calibration_max_qps: int | float = 10000000.0,
    progress_callback: Callable[[int], object] | None = None,
) -> None:
    """Stress a GPU toward different target usage levels.

    `gpu_id` is always treated as the physical GPU index reported by `nvidia-smi`.
    - If the GPU has no other compute processes, aim for `target_usage_when_idle`.
    - If the GPU already has other compute processes, aim for `target_usage_when_shared`.
    - First calibrate a rough `QPS -> utilization` mapping by doubling QPS until
      utilization reaches `calibration_stop_usage`.
    - Then, every `control_update_interval_s`, recompute the next target QPS
      from the current utilization gap and the calibrated slope.
    """
    _validate_positive(calibration_step_duration_s, "calibration_step_duration_s")
    _validate_positive(calibration_stop_usage, "calibration_stop_usage")
    _validate_positive(control_update_interval_s, "control_update_interval_s")
    _validate_positive(calibration_start_qps, "calibration_start_qps")
    _validate_positive(calibration_max_qps, "calibration_max_qps")
    _validate_non_negative(significant_process_memory_mb, "significant_process_memory_mb")
    device = _resolve_torch_device_for_physical_gpu(gpu_id)
    model, inputs = create_fp16_linear_workload(device=device, batch_size=5000)
    calibration_samples = calibrate_qps_to_usage(
        gpu_id=gpu_id,
        model=model,
        inputs=inputs,
        start_qps=float(calibration_start_qps),
        step_duration_s=float(calibration_step_duration_s),
        stop_usage=float(calibration_stop_usage),
        max_qps=float(calibration_max_qps),
        progress_callback=None,
    )
    usage_per_qps = estimate_usage_per_qps(calibration_samples)
    print(
        "[calibration] estimated usage_per_qps="
        f"{usage_per_qps:.6f} util/qps from {len(calibration_samples)} samples"
    )
    current_target_qps = estimate_qps_for_usage(
        target_usage=float(target_usage_when_idle),
        usage_per_qps=usage_per_qps,
    )

    while True:
        gpu_usage = query_nvidia_smi_usage(gpu_id)
        other_processes = list_significant_gpu_processes(
            gpu_id,
            include_self=False,
            min_used_memory_mb=significant_process_memory_mb,
        )
        target_usage = (
            target_usage_when_shared
            if other_processes
            else target_usage_when_idle
        )
        delta_qps = estimate_qps_for_usage_gap(
            usage_gap=float(target_usage) - float(gpu_usage.gpu_utilization),
            usage_per_qps=usage_per_qps,
        )
        next_target_qps = max(0.0, current_target_qps + delta_qps)
        current_target_qps = run_workload_at_target_qps(
            model=model,
            inputs=inputs,
            device=device,
            target_qps=next_target_qps,
            duration_s=float(control_update_interval_s),
            progress_callback=progress_callback,
        )


def _query_gpu_uuid(gpu_id: int) -> str:
    cmd = [
        "nvidia-smi",
        "--query-gpu=index,uuid",
        "--format=csv,noheader,nounits",
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, check=False)
    output = ((result.stdout or "") + (result.stderr or "")).strip()
    if result.returncode != 0:
        raise RuntimeError(f"nvidia-smi uuid query failed: {output}")

    for line in output.splitlines():
        parts = [item.strip() for item in line.split(",")]
        if len(parts) != 2:
            continue
        index, uuid = parts
        if int(index) == int(gpu_id):
            return uuid

    raise RuntimeError(f"Failed to find uuid for gpu_id={gpu_id}. Raw output: {output!r}")


def _resolve_torch_device_for_physical_gpu(gpu_id: int) -> str:
    """Map a physical GPU index to the torch-visible logical device name."""
    visible_devices = os.environ.get("CUDA_VISIBLE_DEVICES", "").strip()
    if not visible_devices:
        return f"cuda:{gpu_id}"

    visible_tokens = [token.strip() for token in visible_devices.split(",") if token.strip()]
    if not visible_tokens:
        return f"cuda:{gpu_id}"

    physical_gpu_str = str(gpu_id)

    for logical_index, token in enumerate(visible_tokens):
        if token.isdigit() and token == physical_gpu_str:
            return f"cuda:{logical_index}"

    physical_gpu_uuid = _query_gpu_uuid(gpu_id)
    for logical_index, token in enumerate(visible_tokens):
        # CUDA_VISIBLE_DEVICES may contain full UUIDs or unique UUID prefixes.
        if physical_gpu_uuid == token or physical_gpu_uuid.startswith(token):
            return f"cuda:{logical_index}"

    raise RuntimeError(
        f"Physical gpu_id={gpu_id} is not visible to torch under "
        f"CUDA_VISIBLE_DEVICES={visible_devices!r}."
    )


def _synchronize_device(device: str) -> None:
    import torch

    torch.cuda.synchronize(device=device)


def run_workload_at_target_qps(
    *,
    model,
    inputs,
    device: str,
    target_qps: float,
    duration_s: float,
    progress_callback: Callable[[int], object] | None = None,
) -> float:
    """Run workload for a fixed duration while pacing submission rate by QPS."""
    _validate_non_negative(target_qps, "target_qps")
    _validate_positive(duration_s, "duration_s")

    if target_qps == 0:
        time.sleep(duration_s)
        return 0.0

    started_at = time.perf_counter()
    next_deadline = started_at
    step = 0
    while True:
        now = time.perf_counter()
        if now - started_at >= duration_s:
            break

        run_workload_step(model, inputs)
        step += 1
        if progress_callback is not None:
            progress_callback(1)

        next_deadline += 1.0 / target_qps
        remaining_s = duration_s - (time.perf_counter() - started_at)
        if remaining_s <= 0:
            break

        sleep_s = min(next_deadline - time.perf_counter(), remaining_s)
        if sleep_s > 0:
            time.sleep(sleep_s)

    _synchronize_device(device)
    elapsed_s = max(time.perf_counter() - started_at, 1e-9)
    return step / elapsed_s


def calibrate_qps_to_usage(
    *,
    gpu_id: int,
    model,
    inputs,
    start_qps: float,
    step_duration_s: float,
    stop_usage: float,
    max_qps: float,
    progress_callback: Callable[[int], object] | None = None,
) -> list[QpsCalibrationSample]:
    """Build a rough `QPS -> added GPU utilization` mapping by doubling QPS."""
    _validate_positive(start_qps, "start_qps")
    _validate_positive(step_duration_s, "step_duration_s")
    _validate_positive(stop_usage, "stop_usage")
    _validate_positive(max_qps, "max_qps")

    samples: list[QpsCalibrationSample] = []
    current_qps = float(start_qps)
    device = _infer_device_from_inputs(inputs)
    print(
        "[calibration] start "
        f"gpu_id={gpu_id} step_duration_s={step_duration_s:.1f} stop_usage={stop_usage:.1f}"
    )

    while True:
        sample = measure_utilization_at_qps(
            gpu_id=gpu_id,
            model=model,
            inputs=inputs,
            device=device,
            target_qps=current_qps,
            duration_s=step_duration_s,
            progress_callback=progress_callback,
        )
        samples.append(sample)
        print(
            "[calibration] "
            f"requested_qps={sample.requested_qps:.2f} "
            f"achieved_qps={sample.achieved_qps:.2f} "
            f"baseline_util={sample.baseline_gpu_utilization:.2f}% "
            f"avg_util={sample.average_gpu_utilization:.2f}% "
            f"added_util={sample.added_gpu_utilization:.2f}%"
        )

        if sample.average_gpu_utilization >= stop_usage or current_qps >= max_qps:
            break
        current_qps *= 2.0

    if all(sample.added_gpu_utilization <= 0 for sample in samples):
        raise RuntimeError(
            "Calibration failed: added GPU utilization stayed at 0. "
            "The current workload may be too light for this GPU."
        )
    return samples


def measure_utilization_at_qps(
    *,
    gpu_id: int,
    model,
    inputs,
    device: str,
    target_qps: float,
    duration_s: float,
    progress_callback: Callable[[int], object] | None = None,
) -> QpsCalibrationSample:
    """Run the workload at a fixed QPS and estimate average added GPU utilization."""
    _validate_positive(duration_s, "duration_s")

    baseline_gpu_utilization = _measure_average_gpu_utilization(
        gpu_id=gpu_id,
        duration_s=min(1.0, float(duration_s)),
    )
    remaining_s = float(duration_s)
    window_s = 1.0
    achieved_qps_values: list[float] = []
    utilization_values: list[float] = []

    while remaining_s > 0:
        current_window_s = min(window_s, remaining_s)
        achieved_qps = run_workload_at_target_qps(
            model=model,
            inputs=inputs,
            device=device,
            target_qps=target_qps,
            duration_s=current_window_s,
            progress_callback=progress_callback,
        )
        achieved_qps_values.append(achieved_qps)
        utilization_values.append(float(query_nvidia_smi_usage(gpu_id).gpu_utilization))
        remaining_s -= current_window_s

    return QpsCalibrationSample(
        requested_qps=float(target_qps),
        achieved_qps=sum(achieved_qps_values) / max(len(achieved_qps_values), 1),
        baseline_gpu_utilization=baseline_gpu_utilization,
        average_gpu_utilization=sum(utilization_values) / max(len(utilization_values), 1),
        added_gpu_utilization=max(
            0.0,
            (sum(utilization_values) / max(len(utilization_values), 1)) - baseline_gpu_utilization,
        ),
    )


def estimate_usage_per_qps(samples: list[QpsCalibrationSample]) -> float:
    """Estimate a linear `added_utilization ~= qps * slope` relationship."""
    weighted_usage_sum = 0.0
    weighted_qps_square_sum = 0.0
    for sample in samples:
        if sample.achieved_qps <= 0:
            continue
        weighted_usage_sum += sample.achieved_qps * sample.added_gpu_utilization
        weighted_qps_square_sum += sample.achieved_qps * sample.achieved_qps

    if weighted_qps_square_sum <= 0 or weighted_usage_sum <= 0:
        raise RuntimeError("Failed to estimate utilization per QPS from calibration samples.")
    return weighted_usage_sum / weighted_qps_square_sum


def estimate_qps_for_usage(target_usage: float, usage_per_qps: float) -> float:
    """Estimate the QPS needed for the target added utilization."""
    _validate_non_negative(target_usage, "target_usage")
    _validate_positive(usage_per_qps, "usage_per_qps")
    return target_usage / usage_per_qps


def estimate_qps_for_usage_gap(usage_gap: float, usage_per_qps: float) -> float:
    """Estimate QPS delta from the utilization gap."""
    _validate_positive(usage_per_qps, "usage_per_qps")
    return usage_gap / usage_per_qps


def _measure_average_gpu_utilization(gpu_id: int, duration_s: float) -> float:
    _validate_positive(duration_s, "duration_s")

    started_at = time.perf_counter()
    values: list[float] = []
    while True:
        values.append(float(query_nvidia_smi_usage(gpu_id).gpu_utilization))
        elapsed_s = time.perf_counter() - started_at
        if elapsed_s >= duration_s:
            break
        time.sleep(min(0.2, max(duration_s - elapsed_s, 0.01)))

    return sum(values) / max(len(values), 1)


def _validate_positive(value: int | float, name: str) -> None:
    if value <= 0:
        raise ValueError(f"{name} must be > 0, got {value!r}")


def _validate_non_negative(value: int | float, name: str) -> None:
    if value < 0:
        raise ValueError(f"{name} must be >= 0, got {value!r}")


def _infer_device_from_inputs(inputs) -> str:
    return str(inputs.device)


def _main() -> None:
    from tqdm import tqdm

    progress = tqdm()
    stress_gpu_to_target_usage(
        gpu_id=3,
        target_usage_when_idle=90,
        target_usage_when_shared=30,
        progress_callback=progress.update,
    )


if __name__ == "__main__":
    _main()
