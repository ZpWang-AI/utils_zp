from __future__ import annotations

import io
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import mock
import yaml

from utils_zp import setting
from utils_zp.cli import zppremodel


class ZPPreModelCLITests(unittest.TestCase):
    def test_main_prints_configured_pretrained_model_versions_summary(self) -> None:
        with TemporaryDirectory() as tmp_dir:
            index_path = Path(tmp_dir) / "model_versions.yaml"
            index_path.write_text(
                "title: demo\n"
                "versions:\n"
                "  - id: '1'\n"
                "    name: Qwen3-Reranker-0.6B\n"
                "    parameter_size: 0.6B\n"
                "    summary: reranker\n"
                "    target_path: pretrained_models/Qwen3-Reranker-0.6B/\n"
                "    marked: true\n"
                "  - id: '2'\n"
                "    name: Youtu-Embedding\n"
                "    parameter_size: 1.1B\n"
                "    summary: embedding\n"
                "    target_path: pretrained_models/Youtu-Embedding/\n"
                "    marked: true\n"
                "  - id: '3'\n"
                "    name: hidden-model\n"
                "    parameter_size: 9B\n"
                "    summary: hidden\n"
                "    target_path: pretrained_models/hidden-model/\n"
                "    marked: false\n",
                encoding="utf-8",
            )

            with mock.patch.object(setting, "TARGET_PRETRAINED_MODEL_VERSIONS_PATH", index_path):
                stdout = io.StringIO()
                with redirect_stdout(stdout):
                    exit_code = zppremodel.main([])

        self.assertEqual(exit_code, 0)
        self.assertEqual(
            stdout.getvalue(),
            f"Target pretrained model versions path: {index_path}\n"
            "id | 名称 | 参数量 | 简要说明\n"
            "1 | Qwen3-Reranker-0.6B | 0.6B | reranker\n"
            "2 | Youtu-Embedding | 1.1B | embedding\n",
        )

    def test_collect_pretrained_models_returns_only_marked_rows(self) -> None:
        with TemporaryDirectory() as tmp_dir:
            index_path = Path(tmp_dir) / "model_versions.yaml"
            index_path.write_text(
                "title: demo\n"
                "versions:\n"
                "  - id: '6'\n"
                "    name: Conan-embedding-v2\n"
                "    parameter_size: 1.5B\n"
                "    summary: foo\n"
                "    target_path: pretrained_models/Conan-embedding-v2/\n"
                "    marked: true\n"
                "  - id: '7'\n"
                "    name: xlm-roberta-base\n"
                "    parameter_size: 0.3B\n"
                "    summary: bar\n"
                "    target_path: pretrained_models/xlm-roberta-base/\n"
                "    marked: true\n"
                "  - id: '8'\n"
                "    name: skip-me\n"
                "    parameter_size: 8B\n"
                "    summary: baz\n"
                "    target_path: pretrained_models/skip-me/\n"
                "    marked: false\n",
                encoding="utf-8",
            )

            models = zppremodel.collect_pretrained_models(index_path)

        self.assertEqual(
            models,
            [
                zppremodel.PretrainedModelInfo(
                    model_id="6",
                    name="Conan-embedding-v2",
                    parameter_size="1.5B",
                    summary="foo",
                    target_path="pretrained_models/Conan-embedding-v2/",
                ),
                zppremodel.PretrainedModelInfo(
                    model_id="7",
                    name="xlm-roberta-base",
                    parameter_size="0.3B",
                    summary="bar",
                    target_path="pretrained_models/xlm-roberta-base/",
                ),
            ],
        )

    def test_collect_pretrained_models_reports_missing_yaml_list(self) -> None:
        with TemporaryDirectory() as tmp_dir:
            index_path = Path(tmp_dir) / "model_versions.yaml"
            index_path.write_text("title: demo\n", encoding="utf-8")

            with self.assertRaisesRegex(ValueError, "missing yaml item list `versions`"):
                zppremodel.collect_pretrained_models(index_path)

    def test_main_prints_selected_pretrained_model_detail(self) -> None:
        with TemporaryDirectory() as tmp_dir:
            index_path = Path(tmp_dir) / "model_versions.yaml"
            index_path.write_text(
                "title: demo\n"
                "versions:\n"
                "  - id: 2\n"
                "    name: Qwen3-Reranker-0.6B\n"
                "    parameter_size: 0.6B\n"
                "    summary: 首选 reranker baseline\n"
                "    target_path: pretrained_models/Qwen3-Reranker-0.6B/\n"
                "    marked: true\n"
                "    detail_markdown: |\n"
                "      ### 2. `Qwen3-Reranker-0.6B`\n"
                "\n"
                "      - 说明：首选 reranker baseline。\n",
                encoding="utf-8",
            )

            with mock.patch.object(setting, "TARGET_PRETRAINED_MODEL_VERSIONS_PATH", index_path):
                stdout = io.StringIO()
                with redirect_stdout(stdout):
                    exit_code = zppremodel.main(["2"])

        self.assertEqual(exit_code, 0)
        self.assertEqual(
            stdout.getvalue(),
            f"Target pretrained model versions path: {index_path}\n"
            "\n"
            "ID: 2\n"
            "模型名: Qwen3-Reranker-0.6B\n"
            "参数量: 0.6B\n"
            "简要说明: 首选 reranker baseline\n"
            "目标路径: pretrained_models/Qwen3-Reranker-0.6B/\n"
            "\n"
            "### 2. `Qwen3-Reranker-0.6B`\n"
            "\n"
            "- 说明：首选 reranker baseline。\n",
        )

    def test_main_prints_unmarked_selected_pretrained_model_detail(self) -> None:
        with TemporaryDirectory() as tmp_dir:
            index_path = Path(tmp_dir) / "model_versions.yaml"
            index_path.write_text(
                "title: demo\n"
                "versions:\n"
                "  - id: '3'\n"
                "    name: hidden-model\n"
                "    parameter_size: 9B\n"
                "    summary: hidden\n"
                "    target_path: pretrained_models/hidden-model/\n"
                "    marked: false\n"
                "    detail_markdown: |\n"
                "      ### 3. `hidden-model`\n"
                "\n"
                "      - 说明：未标记但可按编号读取。\n",
                encoding="utf-8",
            )

            with mock.patch.object(setting, "TARGET_PRETRAINED_MODEL_VERSIONS_PATH", index_path):
                stdout = io.StringIO()
                with redirect_stdout(stdout):
                    exit_code = zppremodel.main(["3"])

        self.assertEqual(exit_code, 0)
        self.assertEqual(
            stdout.getvalue(),
            f"Target pretrained model versions path: {index_path}\n"
            "\n"
            "ID: 3\n"
            "模型名: hidden-model\n"
            "参数量: 9B\n"
            "简要说明: hidden\n"
            "目标路径: pretrained_models/hidden-model/\n"
            "\n"
            "### 3. `hidden-model`\n"
            "\n"
            "- 说明：未标记但可按编号读取。\n",
        )

    def test_main_rejects_unknown_selected_pretrained_model(self) -> None:
        with TemporaryDirectory() as tmp_dir:
            index_path = Path(tmp_dir) / "model_versions.yaml"
            index_path.write_text(
                "title: demo\n"
                "versions:\n"
                "  - id: '2'\n"
                "    name: Qwen3-Reranker-0.6B\n"
                "    parameter_size: 0.6B\n"
                "    summary: foo\n"
                "    target_path: pretrained_models/Qwen3-Reranker-0.6B/\n"
                "    marked: true\n",
                encoding="utf-8",
            )

            with mock.patch.object(setting, "TARGET_PRETRAINED_MODEL_VERSIONS_PATH", index_path):
                stdout = io.StringIO()
                with redirect_stdout(stdout):
                    exit_code = zppremodel.main(["3"])

        self.assertEqual(exit_code, 1)
        self.assertEqual(stdout.getvalue(), "unknown pretrained model number: 3\n")

    def test_main_reports_missing_pretrained_model_versions_file(self) -> None:
        missing_path = Path("/tmp/utils_zp_missing_pretrained_model_versions.yaml")

        with mock.patch.object(setting, "TARGET_PRETRAINED_MODEL_VERSIONS_PATH", missing_path):
            stdout = io.StringIO()
            with redirect_stdout(stdout):
                exit_code = zppremodel.main([])

        self.assertEqual(exit_code, 1)
        self.assertEqual(
            stdout.getvalue(),
            f"missing pretrained model versions file: {missing_path}\n",
        )

    def test_main_prints_all_models_when_full_is_requested(self) -> None:
        with TemporaryDirectory() as tmp_dir:
            index_path = Path(tmp_dir) / "model_versions.yaml"
            index_path.write_text(
                "title: demo\n"
                "versions:\n"
                "  - id: 1\n"
                "    name: foo\n"
                "    parameter_size: 0.1B\n"
                "    summary: bar\n"
                "    target_path: pretrained_models/foo/\n"
                "    marked: true\n"
                "  - id: 2\n"
                "    name: hidden\n"
                "    parameter_size: 0.2B\n"
                "    summary: baz\n"
                "    target_path: pretrained_models/hidden/\n"
                "    marked: false\n",
                encoding="utf-8",
            )

            with mock.patch.object(setting, "TARGET_PRETRAINED_MODEL_VERSIONS_PATH", index_path):
                stdout = io.StringIO()
                with redirect_stdout(stdout):
                    exit_code = zppremodel.main(["--full"])

        self.assertEqual(exit_code, 0)
        self.assertEqual(
            stdout.getvalue(),
            f"Target pretrained model versions path: {index_path}\n"
            "id | 名称 | 参数量 | 简要说明\n"
            "1 | foo | 0.1B | bar\n"
            "2 | hidden | 0.2B | baz\n",
        )

    def test_main_marks_pretrained_model_when_requested(self) -> None:
        with TemporaryDirectory() as tmp_dir:
            index_path = Path(tmp_dir) / "model_versions.yaml"
            index_path.write_text(
                "title: demo\nversions:\n  - id: 3\n    name: foo\n    parameter_size: 0.1B\n    summary: bar\n    target_path: pretrained_models/foo/\n    marked: false\n",
                encoding="utf-8",
            )

            with mock.patch.object(setting, "TARGET_PRETRAINED_MODEL_VERSIONS_PATH", index_path):
                stdout = io.StringIO()
                with redirect_stdout(stdout):
                    exit_code = zppremodel.main(["-m", "3"])

            document = yaml.safe_load(index_path.read_text(encoding="utf-8"))

        self.assertEqual(exit_code, 0)
        self.assertEqual(stdout.getvalue(), "marked pretrained model 3: foo\n")
        self.assertTrue(document["versions"][0]["marked"])

    def test_main_unmarks_pretrained_model_when_requested(self) -> None:
        with TemporaryDirectory() as tmp_dir:
            index_path = Path(tmp_dir) / "model_versions.yaml"
            index_path.write_text(
                "title: demo\nversions:\n  - id: 3\n    name: foo\n    parameter_size: 0.1B\n    summary: bar\n    target_path: pretrained_models/foo/\n    marked: true\n",
                encoding="utf-8",
            )

            with mock.patch.object(setting, "TARGET_PRETRAINED_MODEL_VERSIONS_PATH", index_path):
                stdout = io.StringIO()
                with redirect_stdout(stdout):
                    exit_code = zppremodel.main(["-um", "3"])

            document = yaml.safe_load(index_path.read_text(encoding="utf-8"))

        self.assertEqual(exit_code, 0)
        self.assertEqual(stdout.getvalue(), "unmarked pretrained model 3: foo\n")
        self.assertFalse(document["versions"][0]["marked"])


if __name__ == "__main__":
    unittest.main()
