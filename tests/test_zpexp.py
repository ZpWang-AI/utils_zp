from __future__ import annotations

import io
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import mock
import yaml

from utils_zp import setting
from utils_zp.cli import zpexp


class ZPExpCLITests(unittest.TestCase):
    def test_main_prints_configured_exp_versions_summary(self) -> None:
        with TemporaryDirectory() as tmp_dir:
            exp_root = Path(tmp_dir) / "exp"
            exp_root.mkdir()
            versions_path = exp_root / "exp_versions.yaml"
            versions_path.write_text(
                "title: exp 版本索引\n"
                "versions:\n"
                "  - id: 3\n"
                "    importance: 低\n"
                "    name: 不会输出\n"
                "    progress: 1／4\n"
                "    summary: hidden\n"
                "    target_path: exp/03-20260729-hidden-exp/\n"
                "    marked: false\n"
                "  - id: 4\n"
                "    importance: 高\n"
                "    name: demo 实验任务\n"
                "    progress: 4／4\n"
                "    summary: demo\n"
                "    target_path: exp/04-20260730-demo-exp/\n"
                "    marked: true\n",
                encoding="utf-8",
            )

            with mock.patch.object(setting, "TARGET_EXP_PATH", exp_root):
                stdout = io.StringIO()
                with redirect_stdout(stdout):
                    exit_code = zpexp.main([])

        self.assertEqual(exit_code, 0)
        self.assertEqual(
            stdout.getvalue(),
            f"Target exp versions path: {versions_path}\n"
            "id | 重要性 | 进度 | 名称 | 简要说明\n"
            "4 | 高 | 4/4 | demo 实验任务 | demo\n",
        )

    def test_collect_experiments_reads_exp_versions_yaml(self) -> None:
        with TemporaryDirectory() as tmp_dir:
            exp_root = Path(tmp_dir) / "exp"
            exp_root.mkdir()
            (exp_root / "exp_versions.yaml").write_text(
                "title: exp 版本索引\n"
                "versions:\n"
                "  - id: 1\n"
                "    importance: 中\n"
                "    name: baseline\n"
                "    progress: 2／4\n"
                "    summary: demo\n"
                "    target_path: exp/01-20260724-demo-exp/\n"
                "    marked: true\n"
                "  - id: 2\n"
                "    importance: 低\n"
                "    name: skip me\n"
                "    progress: 4／4\n"
                "    summary: skip\n"
                "    target_path: exp/02-20260725-skip-exp/\n"
                "    marked: false\n",
                encoding="utf-8",
            )

            experiments = zpexp.collect_experiments(exp_root)

        self.assertEqual(
            experiments,
            [
                zpexp.ExperimentInfo(
                    exp_id="1",
                    importance="中",
                    name="baseline",
                    progress="2/4",
                    summary="demo",
                    target_path="exp/01-20260724-demo-exp/",
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
        missing_versions_path = Path("/tmp/utils_zp_missing_exp/exp_versions.yaml")

        with mock.patch.object(setting, "TARGET_EXP_PATH", missing_versions_path.parent):
            stdout = io.StringIO()
            with redirect_stdout(stdout):
                exit_code = zpexp.main([])

        self.assertEqual(exit_code, 1)
        self.assertEqual(stdout.getvalue(), f"missing exp versions file: {missing_versions_path}\n")

    def test_main_prints_selected_experiment_detail(self) -> None:
        with TemporaryDirectory() as tmp_dir:
            exp_root = Path(tmp_dir) / "exp"
            exp_root.mkdir()
            versions_path = exp_root / "exp_versions.yaml"
            versions_path.write_text(
                "title: exp 版本索引\n"
                "versions:\n"
                "  - id: 3\n"
                "    importance: T3\n"
                "    name: 扩容实验\n"
                "    progress: 2／4\n"
                "    summary: demo\n"
                "    target_path: exp/03-20260730-expand-exp/\n"
                "    marked: true\n"
                "    detail_markdown: |\n"
                "      ### 3. `扩容实验`\n"
                "\n"
                "      - 目录：`exp/03-20260730-expand-exp/`\n"
                "      - 当前状态：部分完成。\n",
                encoding="utf-8",
            )

            with mock.patch.object(setting, "TARGET_EXP_PATH", exp_root):
                stdout = io.StringIO()
                with redirect_stdout(stdout):
                    exit_code = zpexp.main(["3"])

        self.assertEqual(exit_code, 0)
        self.assertEqual(
            stdout.getvalue(),
            f"Target exp versions path: {versions_path}\n"
            "\n"
            "ID: 3\n"
            "名称: 扩容实验\n"
            "重要性: T3\n"
            "进度: 2/4\n"
            "简要说明: demo\n"
            "目标路径: exp/03-20260730-expand-exp/\n"
            "\n"
            "### 3. `扩容实验`\n"
            "\n"
            "- 目录：`exp/03-20260730-expand-exp/`\n"
            "- 当前状态：部分完成。\n",
        )

    def test_main_prints_unmarked_selected_experiment_detail(self) -> None:
        with TemporaryDirectory() as tmp_dir:
            exp_root = Path(tmp_dir) / "exp"
            exp_root.mkdir()
            versions_path = exp_root / "exp_versions.yaml"
            versions_path.write_text(
                "title: exp 版本索引\n"
                "versions:\n"
                "  - id: 5\n"
                "    importance: T2\n"
                "    name: 未标记实验\n"
                "    progress: 8／8\n"
                "    summary: demo\n"
                "    target_path: exp/05-20260730-unmarked-exp/\n"
                "    marked: false\n"
                "    detail_markdown: |\n"
                "      ### 5. `未标记实验`\n"
                "\n"
                "      - 当前状态：已收口。\n",
                encoding="utf-8",
            )

            with mock.patch.object(setting, "TARGET_EXP_PATH", exp_root):
                stdout = io.StringIO()
                with redirect_stdout(stdout):
                    exit_code = zpexp.main(["5"])

        self.assertEqual(exit_code, 0)
        self.assertEqual(
            stdout.getvalue(),
            f"Target exp versions path: {versions_path}\n"
            "\n"
            "ID: 5\n"
            "名称: 未标记实验\n"
            "重要性: T2\n"
            "进度: 8/8\n"
            "简要说明: demo\n"
            "目标路径: exp/05-20260730-unmarked-exp/\n"
            "\n"
            "### 5. `未标记实验`\n"
            "\n"
            "- 当前状态：已收口。\n",
        )

    def test_main_rejects_unknown_selected_experiment(self) -> None:
        with TemporaryDirectory() as tmp_dir:
            exp_root = Path(tmp_dir) / "exp"
            exp_root.mkdir()
            versions_path = exp_root / "exp_versions.yaml"
            versions_path.write_text(
                "title: exp 版本索引\n"
                "versions:\n"
                "  - id: 3\n"
                "    importance: T3\n"
                "    name: 扩容实验\n"
                "    progress: 2／4\n"
                "    summary: demo\n"
                "    target_path: exp/03-20260730-expand-exp/\n"
                "    marked: true\n",
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
            versions_path = exp_root / "exp_versions.yaml"

            with mock.patch.object(setting, "TARGET_EXP_PATH", exp_root):
                stdout = io.StringIO()
                with redirect_stdout(stdout):
                    exit_code = zpexp.main([])

        self.assertEqual(exit_code, 1)
        self.assertEqual(stdout.getvalue(), f"missing exp versions file: {versions_path}\n")

    def test_main_prints_all_experiments_when_full_is_requested(self) -> None:
        with TemporaryDirectory() as tmp_dir:
            exp_root = Path(tmp_dir) / "exp"
            exp_root.mkdir()
            versions_path = exp_root / "exp_versions.yaml"
            versions_path.write_text(
                "title: demo\n"
                "versions:\n"
                "  - id: 2\n"
                "    name: hidden\n"
                "    importance: T2\n"
                "    progress: 1/1\n"
                "    summary: baz\n"
                "    target_path: exp/02-hidden/\n"
                "    marked: false\n"
                "  - id: 1\n"
                "    name: foo\n"
                "    importance: T1\n"
                "    progress: 1/1\n"
                "    summary: bar\n"
                "    target_path: exp/01-foo/\n"
                "    marked: true\n",
                encoding="utf-8",
            )

            with mock.patch.object(setting, "TARGET_EXP_PATH", exp_root):
                stdout = io.StringIO()
                with redirect_stdout(stdout):
                    exit_code = zpexp.main(["--full"])

        self.assertEqual(exit_code, 0)
        self.assertEqual(
            stdout.getvalue(),
            f"Target exp versions path: {versions_path}\n"
            "id | 重要性 | 进度 | 名称 | 简要说明\n"
            "1 | T1 | 1/1 | foo | bar\n"
            "2 | T2 | 1/1 | hidden | baz\n",
        )

    def test_main_accepts_summary_starting_with_markdown_backticks(self) -> None:
        with TemporaryDirectory() as tmp_dir:
            exp_root = Path(tmp_dir) / "exp"
            exp_root.mkdir()
            versions_path = exp_root / "exp_versions.yaml"
            versions_path.write_text(
                "title: demo\n"
                "versions:\n"
                "  - id: 7\n"
                "    name: data6 蒸馏消融\n"
                "    importance: T1\n"
                "    progress: 5／7\n"
                "    summary: `zpdata 10` softlabel 已生成完成；当前已完成 teacher\n"
                "    target_path: exp/07-data6-distill_ablation/\n"
                "    marked: true\n",
                encoding="utf-8",
            )

            with mock.patch.object(setting, "TARGET_EXP_PATH", exp_root):
                stdout = io.StringIO()
                with redirect_stdout(stdout):
                    exit_code = zpexp.main([])

        self.assertEqual(exit_code, 0)
        self.assertEqual(
            stdout.getvalue(),
            f"Target exp versions path: {versions_path}\n"
            "id | 重要性 | 进度 | 名称 | 简要说明\n"
            "7 | T1 | 5/7 | data6 蒸馏消融 | `zpdata 10` softlabel 已生成完成；当前已完成 teacher\n",
        )

    def test_main_marks_experiment_when_requested(self) -> None:
        with TemporaryDirectory() as tmp_dir:
            exp_root = Path(tmp_dir) / "exp"
            exp_root.mkdir()
            versions_path = exp_root / "exp_versions.yaml"
            versions_path.write_text(
                "title: demo\nversions:\n  - id: 3\n    name: foo\n    importance: T1\n    progress: 1/1\n    summary: bar\n    target_path: exp/03-foo/\n    marked: false\n",
                encoding="utf-8",
            )

            with mock.patch.object(setting, "TARGET_EXP_PATH", exp_root):
                stdout = io.StringIO()
                with redirect_stdout(stdout):
                    exit_code = zpexp.main(["-m", "3"])

            document = yaml.safe_load(versions_path.read_text(encoding="utf-8"))

        self.assertEqual(exit_code, 0)
        self.assertEqual(stdout.getvalue(), "marked exp 3: foo\n")
        self.assertTrue(document["versions"][0]["marked"])

    def test_main_unmarks_experiment_when_requested(self) -> None:
        with TemporaryDirectory() as tmp_dir:
            exp_root = Path(tmp_dir) / "exp"
            exp_root.mkdir()
            versions_path = exp_root / "exp_versions.yaml"
            versions_path.write_text(
                "title: demo\nversions:\n  - id: 3\n    name: foo\n    importance: T1\n    progress: 1/1\n    summary: bar\n    target_path: exp/03-foo/\n    marked: true\n",
                encoding="utf-8",
            )

            with mock.patch.object(setting, "TARGET_EXP_PATH", exp_root):
                stdout = io.StringIO()
                with redirect_stdout(stdout):
                    exit_code = zpexp.main(["-um", "3"])

            document = yaml.safe_load(versions_path.read_text(encoding="utf-8"))

        self.assertEqual(exit_code, 0)
        self.assertEqual(stdout.getvalue(), "unmarked exp 3: foo\n")
        self.assertFalse(document["versions"][0]["marked"])


if __name__ == "__main__":
    unittest.main()
