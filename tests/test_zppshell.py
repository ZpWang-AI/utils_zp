from __future__ import annotations

import io
import json
import shutil
import unittest
from contextlib import redirect_stdout
from pathlib import Path

from utils_zp import TaskSpec, build_script_content, generate_parallel_shell, parse_task_spec
from utils_zp.cli import zppshell


REPO_ROOT = Path(__file__).resolve().parents[1]


class ZPPShellTests(unittest.TestCase):
    def test_parse_task_spec(self) -> None:
        task = parse_task_spec("xlmr_full|3|PYTHONPATH=src python -m cli.train --config configs/train.yaml")
        expected = TaskSpec(
            name="xlmr_full",
            gpu=3,
            command="PYTHONPATH=src python -m cli.train --config configs/train.yaml",
        )
        self.assertEqual(task, expected)

    def test_parse_task_spec_should_reject_invalid_name(self) -> None:
        with self.assertRaisesRegex(ValueError, "Invalid task name"):
            parse_task_spec("bad task|0|echo ok")

    def test_build_script_content(self) -> None:
        content = build_script_content(
            workdir=REPO_ROOT,
            log_root=REPO_ROOT / "tmp" / "logs",
            job_name="cli_bundle",
            tasks=[
                TaskSpec(name="train", gpu=0, command="python train.py"),
                TaskSpec(name="eval", gpu=1, command="python eval.py"),
            ],
        )
        required_snippets = [
            "#!/usr/bin/env bash",
            "JOB_NAME=cli_bundle",
            'TASK_NAMES+=("${task_name}")',
            'CUDA_VISIBLE_DEVICES="${gpu_id}" bash -lc',
            "00_train.log",
            "01_eval.log",
        ]
        for snippet in required_snippets:
            self.assertIn(snippet, content)

    def test_generate_parallel_shell(self) -> None:
        work_dir = REPO_ROOT / "tmp" / "zppshell_test"
        shutil.rmtree(work_dir, ignore_errors=True)
        work_dir.mkdir(parents=True, exist_ok=True)
        output_path = work_dir / "run_parallel.sh"

        summary = generate_parallel_shell(
            output=output_path,
            workdir=REPO_ROOT,
            tasks=[
                TaskSpec(name="train", gpu=0, command="python train.py"),
                TaskSpec(name="eval", gpu=1, command="python eval.py"),
            ],
        )

        self.assertEqual(summary["task_count"], 2)
        self.assertTrue(output_path.exists())
        self.assertTrue(output_path.stat().st_mode & 0o111)

        content = output_path.read_text(encoding="utf-8")
        self.assertIn("python eval.py", content)
        self.assertIn(str(REPO_ROOT / "tmp" / "logs"), content)

    def test_cli_main_prints_summary(self) -> None:
        work_dir = REPO_ROOT / "tmp" / "zppshell_cli_test"
        shutil.rmtree(work_dir, ignore_errors=True)
        work_dir.mkdir(parents=True, exist_ok=True)
        output_path = work_dir / "run_parallel.sh"

        stdout = io.StringIO()
        with redirect_stdout(stdout):
            exit_code = zppshell.main(
                [
                    "--output",
                    str(output_path),
                    "--workdir",
                    str(REPO_ROOT),
                    "--task",
                    "train|0|python train.py",
                    "--task",
                    "eval|1|python eval.py",
                ]
            )

        self.assertEqual(exit_code, 0)
        payload = json.loads(stdout.getvalue())
        self.assertEqual(payload["task_count"], 2)
        self.assertEqual([item["name"] for item in payload["tasks"]], ["train", "eval"])


if __name__ == "__main__":
    unittest.main()
