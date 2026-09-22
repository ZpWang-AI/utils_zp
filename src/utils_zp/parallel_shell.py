from __future__ import annotations

import re
import shlex
from dataclasses import dataclass
from pathlib import Path
from typing import Sequence


TASK_NAME_PATTERN = re.compile(r"^[A-Za-z0-9._-]+$")


@dataclass(frozen=True)
class TaskSpec:
    name: str
    gpu: int
    command: str


def parse_task_spec(raw_spec: str) -> TaskSpec:
    parts = raw_spec.split("|", 2)
    if len(parts) != 3:
        raise ValueError(f"Invalid task spec: {raw_spec!r}. Expected format 'name|gpu|command'.")

    name = parts[0].strip()
    gpu_text = parts[1].strip()
    command = parts[2].strip()

    if not name:
        raise ValueError(f"Invalid task spec: {raw_spec!r}. Task name cannot be empty.")
    if not TASK_NAME_PATTERN.fullmatch(name):
        raise ValueError(
            f"Invalid task name {name!r}. Only ASCII letters, digits, dot, underscore and hyphen are allowed."
        )
    if not gpu_text:
        raise ValueError(f"Invalid task spec: {raw_spec!r}. GPU id cannot be empty.")
    try:
        gpu = int(gpu_text)
    except ValueError as exc:
        raise ValueError(f"Invalid GPU id {gpu_text!r} in task spec {raw_spec!r}.") from exc
    if gpu < 0:
        raise ValueError(f"Invalid GPU id {gpu}. GPU id must be >= 0.")
    if not command:
        raise ValueError(f"Invalid task spec: {raw_spec!r}. Command cannot be empty.")

    return TaskSpec(name=name, gpu=gpu, command=command)


def resolve_output_path(output_arg: str) -> Path:
    return Path(output_arg).expanduser().resolve()


def resolve_workdir_path(workdir_arg: str) -> Path:
    workdir = Path(workdir_arg).expanduser().resolve()
    if not workdir.exists():
        raise ValueError(f"workdir does not exist: {workdir}")
    if not workdir.is_dir():
        raise ValueError(f"workdir must be a directory: {workdir}")
    return workdir


def resolve_log_root_path(log_root_arg: str | None, workdir: Path) -> Path:
    if log_root_arg is None:
        return workdir / "tmp" / "logs"
    return Path(log_root_arg).expanduser().resolve()


def sanitize_job_name(job_name: str) -> str:
    sanitized = re.sub(r"[^A-Za-z0-9._-]+", "_", job_name.strip())
    sanitized = sanitized.strip("._-")
    if not sanitized:
        raise ValueError(f"Invalid job name: {job_name!r}")
    return sanitized


def validate_tasks(tasks: Sequence[TaskSpec], *, allow_gpu_reuse: bool) -> None:
    if not tasks:
        raise ValueError("At least one task is required.")

    seen_names: set[str] = set()
    seen_gpus: set[int] = set()
    for task in tasks:
        if task.name in seen_names:
            raise ValueError(f"Duplicated task name is not allowed: {task.name}")
        seen_names.add(task.name)
        if not allow_gpu_reuse and task.gpu in seen_gpus:
            raise ValueError(
                f"Duplicated GPU id is not allowed by default: {task.gpu}. "
                "Use --allow-gpu-reuse if you really want to share a GPU."
            )
        seen_gpus.add(task.gpu)


def build_script_content(*, workdir: Path, log_root: Path, job_name: str, tasks: Sequence[TaskSpec]) -> str:
    lines = [
        "#!/usr/bin/env bash",
        "",
        "set -euo pipefail",
        "",
        f"ROOT_DIR={shlex.quote(str(workdir))}",
        f"JOB_NAME={shlex.quote(job_name)}",
        f"LOG_ROOT={shlex.quote(str(log_root))}",
        'RUN_TS="$(date +%Y%m%d_%H%M%S)"',
        'LOG_DIR="${LOG_ROOT}/${JOB_NAME}_${RUN_TS}"',
        'mkdir -p "${LOG_DIR}"',
        "",
        "PIDS=()",
        "TASK_NAMES=()",
        "TASK_GPUS=()",
        "TASK_LOGS=()",
        "",
        "cleanup() {",
        "  local pid",
        '  for pid in "${PIDS[@]:-}"; do',
        '    if kill -0 "${pid}" 2>/dev/null; then',
        '      kill "${pid}" 2>/dev/null || true',
        "    fi",
        "  done",
        "}",
        "",
        "trap cleanup INT TERM",
        "",
        'echo "log_dir=${LOG_DIR}"',
        f'echo "launching {len(tasks)} task(s)"',
        "",
    ]

    for index, task in enumerate(tasks):
        log_file_expr = f'${{LOG_DIR}}/{index:02d}_{task.name}.log'
        inner_command = f"cd {shlex.quote(str(workdir))} && {task.command}"
        lines.extend(
            [
                f"task_name={shlex.quote(task.name)}",
                f"gpu_id={task.gpu}",
                f'log_file="{log_file_expr}"',
                'echo "[launch] task=${task_name} gpu=${gpu_id} log=${log_file}"',
                f'CUDA_VISIBLE_DEVICES="${{gpu_id}}" bash -lc {shlex.quote(inner_command)} >"${{log_file}}" 2>&1 &',
                'PIDS+=("$!")',
                'TASK_NAMES+=("${task_name}")',
                'TASK_GPUS+=("${gpu_id}")',
                'TASK_LOGS+=("${log_file}")',
                "",
            ]
        )

    lines.extend(
        [
            'echo "all tasks launched"',
            'echo "example: tail -f ${TASK_LOGS[0]}"',
            "",
            "failed=0",
            'for idx in "${!PIDS[@]}"; do',
            '  pid="${PIDS[$idx]}"',
            '  task_name="${TASK_NAMES[$idx]}"',
            '  gpu_id="${TASK_GPUS[$idx]}"',
            '  log_file="${TASK_LOGS[$idx]}"',
            '  if wait "${pid}"; then',
            '    echo "[done] task=${task_name} gpu=${gpu_id} log=${log_file}"',
            "  else",
            "    exit_code=$?",
            '    echo "[fail] task=${task_name} gpu=${gpu_id} exit_code=${exit_code} log=${log_file}"',
            "    failed=1",
            "  fi",
            "done",
            "",
            'if [[ "${failed}" -ne 0 ]]; then',
            '  echo "at least one task failed; inspect ${LOG_DIR}"',
            "  exit 1",
            "fi",
            "",
            'echo "all tasks finished; logs: ${LOG_DIR}"',
            "",
        ]
    )
    return "\n".join(lines)


def write_shell(path: Path, content: str, *, overwrite: bool) -> None:
    if path.exists() and not overwrite:
        raise FileExistsError(f"Output shell already exists: {path}. Use --overwrite to replace it.")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    path.chmod(0o755)


def generate_parallel_shell(
    *,
    output: str | Path,
    tasks: Sequence[TaskSpec],
    workdir: str | Path = ".",
    job_name: str | None = None,
    log_root: str | Path | None = None,
    overwrite: bool = False,
    allow_gpu_reuse: bool = False,
) -> dict[str, object]:
    output_path = resolve_output_path(str(output))
    workdir_path = resolve_workdir_path(str(workdir))
    log_root_path = resolve_log_root_path(None if log_root is None else str(log_root), workdir_path)
    validate_tasks(tasks, allow_gpu_reuse=allow_gpu_reuse)

    job_name_source = job_name or output_path.stem
    normalized_job_name = sanitize_job_name(job_name_source)
    content = build_script_content(
        workdir=workdir_path,
        log_root=log_root_path,
        job_name=normalized_job_name,
        tasks=tasks,
    )
    write_shell(output_path, content, overwrite=overwrite)

    return {
        "output": str(output_path),
        "job_name": normalized_job_name,
        "workdir": str(workdir_path),
        "log_root": str(log_root_path),
        "task_count": len(tasks),
        "tasks": [{"name": task.name, "gpu": task.gpu, "command": task.command} for task in tasks],
    }


__all__ = [
    "TASK_NAME_PATTERN",
    "TaskSpec",
    "build_script_content",
    "generate_parallel_shell",
    "parse_task_spec",
    "resolve_log_root_path",
    "resolve_output_path",
    "resolve_workdir_path",
    "sanitize_job_name",
    "validate_tasks",
    "write_shell",
]
