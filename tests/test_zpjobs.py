from __future__ import annotations

import io
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import mock

from utils_zp.cli import zpjobs


class ZPJobsCLITests(unittest.TestCase):
    def test_main_prints_concise_job_summary_by_default(self) -> None:
        with TemporaryDirectory() as tmp_dir:
            jobs_path = Path(tmp_dir) / "jobs.agent.md"
            jobs_path.write_text("# demo jobs\n## 1. sample\n\n## 2. another job\n", encoding="utf-8")

            with mock.patch.object(zpjobs, "JOBS_PATH", jobs_path):
                stdout = io.StringIO()
                with redirect_stdout(stdout):
                    exit_code = zpjobs.main([])

        self.assertEqual(exit_code, 0)
        self.assertEqual(
            stdout.getvalue(),
            "Agent jobs:\n"
            "1. sample\n"
            "2. another job\n"
            f"\nFull doc: {jobs_path}\n"
            "Use `zpjobs --full` to print the full document.\n",
        )

    def test_main_prints_full_document_when_requested(self) -> None:
        with TemporaryDirectory() as tmp_dir:
            jobs_path = Path(tmp_dir) / "jobs.agent.md"
            jobs_path.write_text("# demo jobs\n## 1. sample\n", encoding="utf-8")

            with mock.patch.object(zpjobs, "JOBS_PATH", jobs_path):
                stdout = io.StringIO()
                with redirect_stdout(stdout):
                    exit_code = zpjobs.main(["--full"])

        self.assertEqual(exit_code, 0)
        self.assertEqual(
            stdout.getvalue(),
            f"Jobs Entry Path: {jobs_path}\n\n# demo jobs\n## 1. sample\n",
        )

    def test_main_reports_missing_jobs_file(self) -> None:
        missing_path = Path("/tmp/utils_zp_missing_jobs.md")

        with mock.patch.object(zpjobs, "JOBS_PATH", missing_path):
            stdout = io.StringIO()
            with redirect_stdout(stdout):
                exit_code = zpjobs.main([])

        self.assertEqual(exit_code, 1)
        self.assertEqual(stdout.getvalue(), f"missing jobs file: {missing_path}\n")


if __name__ == "__main__":
    unittest.main()
