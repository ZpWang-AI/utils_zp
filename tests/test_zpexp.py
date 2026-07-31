from __future__ import annotations

import io
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import mock

from utils_zp import setting
from utils_zp.cli import zpexp


class ZPExpCLITests(unittest.TestCase):
    def test_main_prints_configured_exp_path_and_exp_versions_summary(self) -> None:
        with TemporaryDirectory() as tmp_dir:
            exp_root = Path(tmp_dir) / "exp"
            exp_root.mkdir()
            (exp_root / "exp_versions.md").write_text(
                "\n".join(
                    [
                        "# exp 版本索引",
                        "",
                        "| ID | 重要性 | 实验名 | 进度 | 文件夹 | 简要说明 | 标记 |",
                        "| ---: | --- | --- | --- | --- | --- | --- |",
                        "| 03 | `低` | `不会输出` | `1／4` | `20260729-hidden-exp` | `hidden` | `否` |",
                        "| 04 | `高` | `demo 实验任务` | `4／4` | `20260730-demo-exp` | `demo` | `是` |",
                        "",
                    ]
                ),
                encoding="utf-8",
            )

            with mock.patch.object(setting, "TARGET_EXP_PATH", exp_root):
                stdout = io.StringIO()
                with redirect_stdout(stdout):
                    exit_code = zpexp.main([])

        self.assertEqual(exit_code, 0)
        self.assertEqual(
            stdout.getvalue(),
            f"Target exp path: {exp_root}\n"
            "id | 重要性 | 进度 | 名称 | 简要说明\n"
            "04 | 高 | 4/4 | demo 实验任务 | demo\n",
        )

    def test_collect_experiments_reads_exp_versions_table(self) -> None:
        with TemporaryDirectory() as tmp_dir:
            exp_root = Path(tmp_dir) / "exp"
            exp_root.mkdir()
            (exp_root / "exp_versions.md").write_text(
                "\n".join(
                    [
                        "# exp 版本索引",
                        "",
                        "| ID | 重要性 | 实验名 | 进度 | 文件夹 | 简要说明 | 标记 |",
                        "| ---: | --- | --- | --- | --- | --- | --- |",
                        "| 01 | `中` | `baseline` | `2／4` | `20260724-demo-exp` | `demo` | `是` |",
                        "| 02 | `低` | `skip me` | `4／4` | `20260725-skip-exp` | `skip` | `否` |",
                        "",
                    ]
                ),
                encoding="utf-8",
            )

            experiments = zpexp.collect_experiments(exp_root)

        self.assertEqual(
            experiments,
            [
                zpexp.ExperimentInfo(
                    exp_id="01",
                    exp_path_id="01-20260724-demo-exp",
                    date_taskname="20260724-demo-exp",
                    importance="中",
                    name="baseline",
                    progress="2/4",
                    summary="demo",
                )
            ],
        )

    def test_collect_experiments_reports_missing_exp_versions_file(self) -> None:
        with TemporaryDirectory() as tmp_dir:
            exp_root = Path(tmp_dir) / "exp"
            exp_root.mkdir()

            with self.assertRaisesRegex(ValueError, "missing exp versions file"):
                zpexp.collect_experiments(exp_root)

    def test_main_reports_missing_exp_path(self) -> None:
        missing_path = Path("/tmp/utils_zp_missing_exp")

        with mock.patch.object(setting, "TARGET_EXP_PATH", missing_path):
            stdout = io.StringIO()
            with redirect_stdout(stdout):
                exit_code = zpexp.main([])

        self.assertEqual(exit_code, 1)
        self.assertEqual(stdout.getvalue(), f"missing exp path: {missing_path}\n")

    def test_main_prints_selected_experiment_detail(self) -> None:
        with TemporaryDirectory() as tmp_dir:
            exp_root = Path(tmp_dir) / "exp"
            exp_root.mkdir()
            (exp_root / "exp_versions.md").write_text(
                "\n".join(
                    [
                        "# exp 版本索引",
                        "",
                        "| ID | 重要性 | 实验名 | 进度 | 文件夹 | 简要说明 | 标记 |",
                        "| ---: | --- | --- | --- | --- | --- | --- |",
                        "| 03 | `T3` | `扩容实验` | `2／4` | `20260730-expand-exp` | `demo` | `是` |",
                        "",
                        "### 03. `扩容实验`",
                        "",
                        "- 目录：`exp/03-20260730-expand-exp/`",
                        "- 当前状态：部分完成。",
                    ]
                ),
                encoding="utf-8",
            )

            with mock.patch.object(setting, "TARGET_EXP_PATH", exp_root):
                stdout = io.StringIO()
                with redirect_stdout(stdout):
                    exit_code = zpexp.main(["3"])

        self.assertEqual(exit_code, 0)
        self.assertEqual(
            stdout.getvalue(),
            f"Target exp path: {exp_root}\n"
            "\n"
            "ID: 03\n"
            "名称: 扩容实验\n"
            "重要性: T3\n"
            "进度: 2/4\n"
            "目录: exp/03-20260730-expand-exp/\n"
            "简要说明: demo\n"
            "\n"
            "### 03. `扩容实验`\n"
            "\n"
            "- 目录：`exp/03-20260730-expand-exp/`\n"
            "- 当前状态：部分完成。\n",
        )

    def test_main_rejects_unknown_selected_experiment(self) -> None:
        with TemporaryDirectory() as tmp_dir:
            exp_root = Path(tmp_dir) / "exp"
            exp_root.mkdir()
            (exp_root / "exp_versions.md").write_text(
                "\n".join(
                    [
                        "# exp 版本索引",
                        "",
                        "| ID | 重要性 | 实验名 | 进度 | 文件夹 | 简要说明 | 标记 |",
                        "| ---: | --- | --- | --- | --- | --- | --- |",
                        "| 03 | `T3` | `扩容实验` | `2／4` | `20260730-expand-exp` | `demo` | `是` |",
                    ]
                ),
                encoding="utf-8",
            )

            with mock.patch.object(setting, "TARGET_EXP_PATH", exp_root):
                stdout = io.StringIO()
                with redirect_stdout(stdout):
                    exit_code = zpexp.main(["4"])

        self.assertEqual(exit_code, 1)
        self.assertEqual(stdout.getvalue(), "unknown exp number: 4\n")

    def test_main_reports_missing_exp_versions_file(self) -> None:
        with TemporaryDirectory() as tmp_dir:
            exp_root = Path(tmp_dir) / "exp"
            exp_root.mkdir()

            with mock.patch.object(setting, "TARGET_EXP_PATH", exp_root):
                stdout = io.StringIO()
                with redirect_stdout(stdout):
                    exit_code = zpexp.main([])

        self.assertEqual(exit_code, 1)
        self.assertEqual(stdout.getvalue(), f"missing exp versions file: {exp_root / 'exp_versions.md'}\n")


if __name__ == "__main__":
    unittest.main()
