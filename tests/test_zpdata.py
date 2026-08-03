from __future__ import annotations

import io
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import mock
import yaml

from utils_zp import setting
from utils_zp.cli import zpdata


class ZPDataCLITests(unittest.TestCase):
    def test_main_prints_configured_dataset_versions_summary(self) -> None:
        with TemporaryDirectory() as tmp_dir:
            index_path = Path(tmp_dir) / "dataset_versions.yaml"
            index_path.write_text(
                "title: demo\n"
                "versions:\n"
                "  - id: 1\n"
                "    name: old v2 data v1.0\n"
                "    size: 157K\n"
                "    summary: foo\n"
                "    target_path: data/old_v2_data_v1_0/\n"
                "    marked: false\n"
                "  - id: 2\n"
                "    name: old v3 data v1.0\n"
                "    size: 19K\n"
                "    summary: bar\n"
                "    target_path: data/old_v3_data_v1_0/\n"
                "    marked: true\n"
                "  - id: 3\n"
                "    name: old v2 data v2 trainset\n"
                "    size: 537K\n"
                "    summary: baz\n"
                "    target_path: data/old_v2_data_v2_trainset/\n"
                "    marked: true\n",
                encoding="utf-8",
            )

            with mock.patch.object(setting, "TARGET_DATASET_VERSIONS_PATH", index_path):
                stdout = io.StringIO()
                with redirect_stdout(stdout):
                    exit_code = zpdata.main([])

        self.assertEqual(exit_code, 0)
        self.assertEqual(
            stdout.getvalue(),
            f"Target dataset versions path: {index_path}\n"
            "id | 名称 | 数据量 | 简要说明\n"
            "2 | old v3 data v1.0 | 19K | bar\n"
            "3 | old v2 data v2 trainset | 537K | baz\n",
        )

    def test_collect_datasets_returns_only_marked_rows(self) -> None:
        with TemporaryDirectory() as tmp_dir:
            index_path = Path(tmp_dir) / "dataset_versions.yaml"
            index_path.write_text(
                "title: demo\n"
                "versions:\n"
                "  - id: '6'\n"
                "    name: old v3 data v1.1\n"
                "    size: 19K\n"
                "    summary: foo\n"
                "    target_path: data/old_v3_data_v1_1/\n"
                "    marked: true\n"
                "  - id: '7'\n"
                "    name: old v2 data v2 trainset\n"
                "    size: 537K\n"
                "    summary: bar\n"
                "    target_path: data/old_v2_data_v2_trainset/\n"
                "    marked: true\n"
                "  - id: '8'\n"
                "    name: old v2 data v1.2 balanced\n"
                "    size: 68K\n"
                "    summary: baz\n"
                "    target_path: data/old_v2_data_v1_2_balanced/\n"
                "    marked: false\n",
                encoding="utf-8",
            )

            datasets = zpdata.collect_datasets(index_path)

        self.assertEqual(
            datasets,
            [
                zpdata.DatasetInfo(
                    dataset_id="6",
                    name="old v3 data v1.1",
                    size="19K",
                    summary="foo",
                    target_path="data/old_v3_data_v1_1/",
                ),
                zpdata.DatasetInfo(
                    dataset_id="7",
                    name="old v2 data v2 trainset",
                    size="537K",
                    summary="bar",
                    target_path="data/old_v2_data_v2_trainset/",
                ),
            ],
        )

    def test_collect_datasets_reports_missing_yaml_list(self) -> None:
        with TemporaryDirectory() as tmp_dir:
            index_path = Path(tmp_dir) / "dataset_versions.yaml"
            index_path.write_text("title: demo\n", encoding="utf-8")

            with self.assertRaisesRegex(ValueError, "missing yaml item list `versions`"):
                zpdata.collect_datasets(index_path)

    def test_main_prints_selected_dataset_detail(self) -> None:
        with TemporaryDirectory() as tmp_dir:
            index_path = Path(tmp_dir) / "dataset_versions.yaml"
            index_path.write_text(
                "title: demo\n"
                "versions:\n"
                "  - id: '6'\n"
                "    name: old v3 data v1.1\n"
                "    size: 19K\n"
                "    summary: foo\n"
                "    target_path: data/old_v3_data_v1_1/\n"
                "    marked: true\n"
                "  - id: 7\n"
                "    name: old v2 data v2 trainset\n"
                "    size: 537K\n"
                "    summary: bar\n"
                "    target_path: data/old_v2_data_v2_trainset/\n"
                "    marked: true\n"
                "    detail_markdown: |\n"
                "      ### 7. `old v2 data v2 trainset`\n"
                "\n"
                "      - 目标：扩容训练集。\n"
                "      - 说明：不带 eval。\n",
                encoding="utf-8",
            )

            with mock.patch.object(setting, "TARGET_DATASET_VERSIONS_PATH", index_path):
                stdout = io.StringIO()
                with redirect_stdout(stdout):
                    exit_code = zpdata.main(["7"])

        self.assertEqual(exit_code, 0)
        self.assertEqual(
            stdout.getvalue(),
            f"Target dataset versions path: {index_path}\n"
            "\n"
            "ID: 7\n"
            "名称: old v2 data v2 trainset\n"
            "数据量: 537K\n"
            "简要说明: bar\n"
            "目标路径: data/old_v2_data_v2_trainset/\n"
            "\n"
            "### 7. `old v2 data v2 trainset`\n"
            "\n"
            "- 目标：扩容训练集。\n"
            "- 说明：不带 eval。\n",
        )

    def test_main_prints_unmarked_selected_dataset_detail(self) -> None:
        with TemporaryDirectory() as tmp_dir:
            index_path = Path(tmp_dir) / "dataset_versions.yaml"
            index_path.write_text(
                "title: demo\n"
                "versions:\n"
                "  - id: '8'\n"
                "    name: old v2 data v1.2 balanced\n"
                "    size: 68K\n"
                "    summary: baz\n"
                "    target_path: data/old_v2_data_v1_2_balanced/\n"
                "    marked: false\n"
                "    detail_markdown: |\n"
                "      ### 8. `old v2 data v1.2 balanced`\n"
                "\n"
                "      - 说明：未标记但可按编号读取。\n",
                encoding="utf-8",
            )

            with mock.patch.object(setting, "TARGET_DATASET_VERSIONS_PATH", index_path):
                stdout = io.StringIO()
                with redirect_stdout(stdout):
                    exit_code = zpdata.main(["8"])

        self.assertEqual(exit_code, 0)
        self.assertEqual(
            stdout.getvalue(),
            f"Target dataset versions path: {index_path}\n"
            "\n"
            "ID: 8\n"
            "名称: old v2 data v1.2 balanced\n"
            "数据量: 68K\n"
            "简要说明: baz\n"
            "目标路径: data/old_v2_data_v1_2_balanced/\n"
            "\n"
            "### 8. `old v2 data v1.2 balanced`\n"
            "\n"
            "- 说明：未标记但可按编号读取。\n",
        )

    def test_main_rejects_unknown_selected_dataset(self) -> None:
        with TemporaryDirectory() as tmp_dir:
            index_path = Path(tmp_dir) / "dataset_versions.yaml"
            index_path.write_text(
                "title: demo\n"
                "versions:\n"
                "  - id: '7'\n"
                "    name: old v2 data v2 trainset\n"
                "    size: 537K\n"
                "    summary: bar\n"
                "    target_path: data/old_v2_data_v2_trainset/\n"
                "    marked: true\n",
                encoding="utf-8",
            )

            with mock.patch.object(setting, "TARGET_DATASET_VERSIONS_PATH", index_path):
                stdout = io.StringIO()
                with redirect_stdout(stdout):
                    exit_code = zpdata.main(["8"])

        self.assertEqual(exit_code, 1)
        self.assertEqual(stdout.getvalue(), "unknown dataset number: 8\n")

    def test_main_reports_missing_dataset_versions_file(self) -> None:
        missing_path = Path("/tmp/utils_zp_missing_dataset_versions.yaml")

        with mock.patch.object(setting, "TARGET_DATASET_VERSIONS_PATH", missing_path):
            stdout = io.StringIO()
            with redirect_stdout(stdout):
                exit_code = zpdata.main([])

        self.assertEqual(exit_code, 1)
        self.assertEqual(stdout.getvalue(), f"missing dataset versions file: {missing_path}\n")

    def test_main_prints_all_datasets_when_full_is_requested(self) -> None:
        with TemporaryDirectory() as tmp_dir:
            index_path = Path(tmp_dir) / "dataset_versions.yaml"
            index_path.write_text(
                "title: demo\n"
                "versions:\n"
                "  - id: 1\n"
                "    name: foo\n"
                "    size: 1K\n"
                "    summary: bar\n"
                "    target_path: data/foo/\n"
                "    marked: true\n"
                "  - id: 2\n"
                "    name: hidden\n"
                "    size: 2K\n"
                "    summary: baz\n"
                "    target_path: data/hidden/\n"
                "    marked: false\n",
                encoding="utf-8",
            )

            with mock.patch.object(setting, "TARGET_DATASET_VERSIONS_PATH", index_path):
                stdout = io.StringIO()
                with redirect_stdout(stdout):
                    exit_code = zpdata.main(["--full"])

        self.assertEqual(exit_code, 0)
        self.assertEqual(
            stdout.getvalue(),
            f"Target dataset versions path: {index_path}\n"
            "id | 名称 | 数据量 | 简要说明\n"
            "1 | foo | 1K | bar\n"
            "2 | hidden | 2K | baz\n",
        )

    def test_main_marks_dataset_when_requested(self) -> None:
        with TemporaryDirectory() as tmp_dir:
            index_path = Path(tmp_dir) / "dataset_versions.yaml"
            index_path.write_text(
                "title: demo\nversions:\n  - id: 7\n    name: foo\n    size: 1K\n    summary: bar\n    target_path: data/foo/\n    marked: false\n",
                encoding="utf-8",
            )

            with mock.patch.object(setting, "TARGET_DATASET_VERSIONS_PATH", index_path):
                stdout = io.StringIO()
                with redirect_stdout(stdout):
                    exit_code = zpdata.main(["-m", "7"])

            document = yaml.safe_load(index_path.read_text(encoding="utf-8"))

        self.assertEqual(exit_code, 0)
        self.assertEqual(stdout.getvalue(), "marked dataset 7: foo\n")
        self.assertTrue(document["versions"][0]["marked"])

    def test_main_unmarks_dataset_when_requested(self) -> None:
        with TemporaryDirectory() as tmp_dir:
            index_path = Path(tmp_dir) / "dataset_versions.yaml"
            index_path.write_text(
                "title: demo\nversions:\n  - id: 7\n    name: foo\n    size: 1K\n    summary: bar\n    target_path: data/foo/\n    marked: true\n",
                encoding="utf-8",
            )

            with mock.patch.object(setting, "TARGET_DATASET_VERSIONS_PATH", index_path):
                stdout = io.StringIO()
                with redirect_stdout(stdout):
                    exit_code = zpdata.main(["-um", "7"])

            document = yaml.safe_load(index_path.read_text(encoding="utf-8"))

        self.assertEqual(exit_code, 0)
        self.assertEqual(stdout.getvalue(), "unmarked dataset 7: foo\n")
        self.assertFalse(document["versions"][0]["marked"])


if __name__ == "__main__":
    unittest.main()
