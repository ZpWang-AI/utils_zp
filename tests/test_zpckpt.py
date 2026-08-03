from __future__ import annotations

import io
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import mock
import yaml

from utils_zp import setting
from utils_zp.cli import zpckpt


class ZPCkptCLITests(unittest.TestCase):
    def test_main_prints_supported_checkpoint_summary(self) -> None:
        with TemporaryDirectory() as tmp_dir:
            index_path = Path(tmp_dir) / "checkpoint_versions.yaml"
            index_path.write_text(
                "title: demo\n"
                "versions:\n"
                "  - id: '1'\n"
                "    name: 线上模型\n"
                "    parameter_size: 0.6B\n"
                "    summary: 当前线上 relevance 模型 checkpoint\n"
                "    target_path: model/online_model/\n"
                "    marked: true\n"
                "  - id: '2'\n"
                "    name: Qwen3.5 teacher\n"
                "    parameter_size: 9B\n"
                "    summary: Qwen3.5 teacher 模型 checkpoint\n"
                "    target_path: model/qwen35_teacher/\n"
                "    marked: true\n",
                encoding="utf-8",
            )

            with mock.patch.object(setting, "TARGET_CHECKPOINT_VERSIONS_PATH", index_path):
                stdout = io.StringIO()
                with redirect_stdout(stdout):
                    exit_code = zpckpt.main([])

        self.assertEqual(exit_code, 0)
        self.assertEqual(
            stdout.getvalue(),
            f"Target checkpoint versions path: {index_path}\n"
            "id | 名称 | 参数量 | 简要说明\n"
            "1 | 线上模型 | 0.6B | 当前线上 relevance 模型 checkpoint\n"
            "2 | Qwen3.5 teacher | 9B | Qwen3.5 teacher 模型 checkpoint\n",
        )

    def test_collect_checkpoints_returns_configured_items(self) -> None:
        with TemporaryDirectory() as tmp_dir:
            index_path = Path(tmp_dir) / "checkpoint_versions.yaml"
            index_path.write_text(
                "title: demo\n"
                "versions:\n"
                "  - id: '1'\n"
                "    name: 线上模型\n"
                "    parameter_size: 0.6B\n"
                "    summary: 当前线上 relevance 模型 checkpoint\n"
                "    target_path: model/online_model/\n"
                "    marked: true\n"
                "  - id: '2'\n"
                "    name: Qwen3.5 teacher\n"
                "    parameter_size: 9B\n"
                "    summary: Qwen3.5 teacher 模型 checkpoint\n"
                "    target_path: model/qwen35_teacher/\n"
                "    marked: true\n",
                encoding="utf-8",
            )

            result = zpckpt.collect_checkpoints(index_path)

        self.assertEqual(
            result,
            [
                zpckpt.CheckpointInfo(
                    checkpoint_id="1",
                    name="线上模型",
                    parameter_size="0.6B",
                    summary="当前线上 relevance 模型 checkpoint",
                    target_path="model/online_model/",
                ),
                zpckpt.CheckpointInfo(
                    checkpoint_id="2",
                    name="Qwen3.5 teacher",
                    parameter_size="9B",
                    summary="Qwen3.5 teacher 模型 checkpoint",
                    target_path="model/qwen35_teacher/",
                ),
            ],
        )

    def test_main_prints_selected_checkpoint_detail(self) -> None:
        with TemporaryDirectory() as tmp_dir:
            index_path = Path(tmp_dir) / "checkpoint_versions.yaml"
            index_path.write_text(
                "title: demo\n"
                "versions:\n"
                "  - id: '1'\n"
                "    name: 线上模型\n"
                "    parameter_size: 0.6B\n"
                "    summary: 当前线上 relevance 模型 checkpoint\n"
                "    target_path: model/online_model/\n"
                "    marked: true\n"
                "  - id: '2'\n"
                "    name: Qwen3.5 teacher\n"
                "    parameter_size: 9B\n"
                "    summary: Qwen3.5 teacher 模型 checkpoint\n"
                "    target_path: model/qwen35_teacher/\n"
                "    marked: true\n"
                "    detail_markdown: |\n"
                "      ### 2. `Qwen3.5 teacher`\n"
                "\n"
                "      - 路径：`model/qwen35_teacher/`\n"
                "      - 说明：Qwen3.5 teacher 模型 checkpoint。\n",
                encoding="utf-8",
            )

            with mock.patch.object(setting, "TARGET_CHECKPOINT_VERSIONS_PATH", index_path):
                stdout = io.StringIO()
                with redirect_stdout(stdout):
                    exit_code = zpckpt.main(["2"])

        self.assertEqual(exit_code, 0)
        self.assertEqual(
            stdout.getvalue(),
            f"Target checkpoint versions path: {index_path}\n"
            "\n"
            "ID: 2\n"
            "名称: Qwen3.5 teacher\n"
            "参数量: 9B\n"
            "简要说明: Qwen3.5 teacher 模型 checkpoint\n"
            "目标路径: model/qwen35_teacher/\n"
            "\n"
            "### 2. `Qwen3.5 teacher`\n"
            "\n"
            "- 路径：`model/qwen35_teacher/`\n"
            "- 说明：Qwen3.5 teacher 模型 checkpoint。\n",
        )

    def test_main_rejects_unknown_checkpoint_number(self) -> None:
        with TemporaryDirectory() as tmp_dir:
            index_path = Path(tmp_dir) / "checkpoint_versions.yaml"
            index_path.write_text(
                "title: demo\n"
                "versions:\n"
                "  - id: '1'\n"
                "    name: 线上模型\n"
                "    parameter_size: 0.6B\n"
                "    summary: 当前线上 relevance 模型 checkpoint\n"
                "    target_path: model/online_model/\n"
                "    marked: true\n",
                encoding="utf-8",
            )

            with mock.patch.object(setting, "TARGET_CHECKPOINT_VERSIONS_PATH", index_path):
                stdout = io.StringIO()
                with redirect_stdout(stdout):
                    exit_code = zpckpt.main(["9"])

        self.assertEqual(exit_code, 1)
        self.assertEqual(stdout.getvalue(), "unknown checkpoint number: 9\n")

    def test_main_reports_missing_checkpoint_versions_file(self) -> None:
        missing_path = Path("/tmp/utils_zp_missing_checkpoint_versions.yaml")

        with mock.patch.object(setting, "TARGET_CHECKPOINT_VERSIONS_PATH", missing_path):
            stdout = io.StringIO()
            with redirect_stdout(stdout):
                exit_code = zpckpt.main([])

        self.assertEqual(exit_code, 1)
        self.assertEqual(stdout.getvalue(), f"missing checkpoint versions file: {missing_path}\n")

    def test_main_prints_all_checkpoints_when_full_is_requested(self) -> None:
        with TemporaryDirectory() as tmp_dir:
            index_path = Path(tmp_dir) / "checkpoint_versions.yaml"
            index_path.write_text(
                "title: demo\n"
                "versions:\n"
                "  - id: 1\n"
                "    name: foo\n"
                "    parameter_size: 0.1B\n"
                "    summary: bar\n"
                "    target_path: model/foo/\n"
                "    marked: true\n"
                "  - id: 2\n"
                "    name: hidden\n"
                "    parameter_size: 0.2B\n"
                "    summary: baz\n"
                "    target_path: model/hidden/\n"
                "    marked: false\n",
                encoding="utf-8",
            )

            with mock.patch.object(setting, "TARGET_CHECKPOINT_VERSIONS_PATH", index_path):
                stdout = io.StringIO()
                with redirect_stdout(stdout):
                    exit_code = zpckpt.main(["--full"])

        self.assertEqual(exit_code, 0)
        self.assertEqual(
            stdout.getvalue(),
            f"Target checkpoint versions path: {index_path}\n"
            "id | 名称 | 参数量 | 简要说明\n"
            "1 | foo | 0.1B | bar\n"
            "2 | hidden | 0.2B | baz\n",
        )

    def test_main_marks_checkpoint_when_requested(self) -> None:
        with TemporaryDirectory() as tmp_dir:
            index_path = Path(tmp_dir) / "checkpoint_versions.yaml"
            index_path.write_text(
                "title: demo\nversions:\n  - id: 2\n    name: foo\n    parameter_size: 0.1B\n    summary: bar\n    target_path: model/foo/\n    marked: false\n",
                encoding="utf-8",
            )

            with mock.patch.object(setting, "TARGET_CHECKPOINT_VERSIONS_PATH", index_path):
                stdout = io.StringIO()
                with redirect_stdout(stdout):
                    exit_code = zpckpt.main(["-m", "2"])

            document = yaml.safe_load(index_path.read_text(encoding="utf-8"))

        self.assertEqual(exit_code, 0)
        self.assertEqual(stdout.getvalue(), "marked checkpoint 2: foo\n")
        self.assertTrue(document["versions"][0]["marked"])

    def test_main_unmarks_checkpoint_when_requested(self) -> None:
        with TemporaryDirectory() as tmp_dir:
            index_path = Path(tmp_dir) / "checkpoint_versions.yaml"
            index_path.write_text(
                "title: demo\nversions:\n  - id: 2\n    name: foo\n    parameter_size: 0.1B\n    summary: bar\n    target_path: model/foo/\n    marked: true\n",
                encoding="utf-8",
            )

            with mock.patch.object(setting, "TARGET_CHECKPOINT_VERSIONS_PATH", index_path):
                stdout = io.StringIO()
                with redirect_stdout(stdout):
                    exit_code = zpckpt.main(["-um", "2"])

            document = yaml.safe_load(index_path.read_text(encoding="utf-8"))

        self.assertEqual(exit_code, 0)
        self.assertEqual(stdout.getvalue(), "unmarked checkpoint 2: foo\n")
        self.assertFalse(document["versions"][0]["marked"])


if __name__ == "__main__":
    unittest.main()
