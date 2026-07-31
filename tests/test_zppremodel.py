from __future__ import annotations

import io
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import mock

from utils_zp import setting
from utils_zp.cli import zppremodel


class ZPPreModelCLITests(unittest.TestCase):
    def test_main_prints_configured_pretrained_model_versions_summary(self) -> None:
        with TemporaryDirectory() as tmp_dir:
            index_path = Path(tmp_dir) / "model_versions.md"
            index_path.write_text(
                "# demo\n\n"
                "| ID | 模型名 | 参数量 | 标记 |\n"
                "| ---: | --- | --- | --- |\n"
                "| 1 | `Qwen3-Reranker-0.6B` | `0.6B` | 是 |\n"
                "| 2 | `Youtu-Embedding` | `1.1B` | 是 |\n"
                "| 3 | `hidden-model` | `9B` | 否 |\n",
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
            "id | name | 参数量\n"
            "1 | Qwen3-Reranker-0.6B | 0.6B\n"
            "2 | Youtu-Embedding | 1.1B\n",
        )

    def test_collect_pretrained_models_returns_only_marked_rows(self) -> None:
        with TemporaryDirectory() as tmp_dir:
            index_path = Path(tmp_dir) / "model_versions.md"
            index_path.write_text(
                "# demo\n\n"
                "| ID | 模型名 | 参数量 | 标记 |\n"
                "| ---: | --- | --- | --- |\n"
                "| 6 | `Conan-embedding-v2` | `1.5B` | 是 |\n"
                "| 7 | `xlm-roberta-base` | `0.3B` | 是 |\n"
                "| 8 | `skip-me` | `8B` | 否 |\n",
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
                ),
                zppremodel.PretrainedModelInfo(
                    model_id="7",
                    name="xlm-roberta-base",
                    parameter_size="0.3B",
                ),
            ],
        )

    def test_collect_pretrained_models_reports_missing_table(self) -> None:
        with TemporaryDirectory() as tmp_dir:
            index_path = Path(tmp_dir) / "model_versions.md"
            index_path.write_text("# demo\n", encoding="utf-8")

            with self.assertRaisesRegex(ValueError, "missing pretrained model table"):
                zppremodel.collect_pretrained_models(index_path)

    def test_main_prints_selected_pretrained_model_detail(self) -> None:
        with TemporaryDirectory() as tmp_dir:
            index_path = Path(tmp_dir) / "model_versions.md"
            index_path.write_text(
                "# demo\n\n"
                "| ID | 模型名 | 参数量 | 标记 |\n"
                "| ---: | --- | --- | --- |\n"
                "| 2 | `Qwen3-Reranker-0.6B` | `0.6B` | 是 |\n"
                "\n"
                "### 2. `Qwen3-Reranker-0.6B`\n\n"
                "- 说明：首选 reranker baseline。\n",
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
            "\n"
            "### 2. `Qwen3-Reranker-0.6B`\n"
            "\n"
            "- 说明：首选 reranker baseline。\n",
        )

    def test_main_rejects_unknown_selected_pretrained_model(self) -> None:
        with TemporaryDirectory() as tmp_dir:
            index_path = Path(tmp_dir) / "model_versions.md"
            index_path.write_text(
                "# demo\n\n"
                "| ID | 模型名 | 参数量 | 标记 |\n"
                "| ---: | --- | --- | --- |\n"
                "| 2 | `Qwen3-Reranker-0.6B` | `0.6B` | 是 |\n",
                encoding="utf-8",
            )

            with mock.patch.object(setting, "TARGET_PRETRAINED_MODEL_VERSIONS_PATH", index_path):
                stdout = io.StringIO()
                with redirect_stdout(stdout):
                    exit_code = zppremodel.main(["3"])

        self.assertEqual(exit_code, 1)
        self.assertEqual(stdout.getvalue(), "unknown pretrained model number: 3\n")

    def test_main_reports_missing_pretrained_model_versions_file(self) -> None:
        missing_path = Path("/tmp/utils_zp_missing_pretrained_model_versions.md")

        with mock.patch.object(setting, "TARGET_PRETRAINED_MODEL_VERSIONS_PATH", missing_path):
            stdout = io.StringIO()
            with redirect_stdout(stdout):
                exit_code = zppremodel.main([])

        self.assertEqual(exit_code, 1)
        self.assertEqual(
            stdout.getvalue(),
            f"missing pretrained model versions file: {missing_path}\n",
        )


if __name__ == "__main__":
    unittest.main()
