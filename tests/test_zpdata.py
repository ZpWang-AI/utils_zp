from __future__ import annotations

import io
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import mock

from utils_zp import setting
from utils_zp.cli import zpdata


class ZPDataCLITests(unittest.TestCase):
    def test_main_prints_configured_dataset_versions_summary(self) -> None:
        with TemporaryDirectory() as tmp_dir:
            index_path = Path(tmp_dir) / "dataset_versions.md"
            index_path.write_text(
                "# demo\n\n"
                "| ID | 版本名 | 数据量（train+valid+eval） | 简要说明 | 标记 |\n"
                "| ---: | --- | ---: | --- | --- |\n"
                "| 1 | `old v2 data v1.0` | `157K` | `foo` | 否 |\n"
                "| 2 | `old v3 data v1.0` | `19K` | `bar` | 是 |\n"
                "| 3 | `old v2 data v2 trainset` | `537K` | `baz` | 是 |\n",
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
            index_path = Path(tmp_dir) / "dataset_versions.md"
            index_path.write_text(
                "# demo\n\n"
                "| ID | 版本名 | 数据量（train+valid+eval） | 简要说明 | 标记 |\n"
                "| ---: | --- | ---: | --- | --- |\n"
                "| 6 | `old v3 data v1.1` | `19K` | `foo` | 是 |\n"
                "| 7 | `old v2 data v2 trainset` | `537K` | `bar` | 是 |\n"
                "| 8 | `old v2 data v1.2 balanced` | `68K` | `baz` | 否 |\n",
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
                ),
                zpdata.DatasetInfo(
                    dataset_id="7",
                    name="old v2 data v2 trainset",
                    size="537K",
                    summary="bar",
                ),
            ],
        )

    def test_collect_datasets_reports_missing_table(self) -> None:
        with TemporaryDirectory() as tmp_dir:
            index_path = Path(tmp_dir) / "dataset_versions.md"
            index_path.write_text("# demo\n", encoding="utf-8")

            with self.assertRaisesRegex(ValueError, "missing dataset table"):
                zpdata.collect_datasets(index_path)

    def test_main_prints_selected_dataset_detail(self) -> None:
        with TemporaryDirectory() as tmp_dir:
            index_path = Path(tmp_dir) / "dataset_versions.md"
            index_path.write_text(
                "# demo\n\n"
                "| ID | 版本名 | 数据量（train+valid+eval） | 简要说明 | 标记 |\n"
                "| ---: | --- | ---: | --- | --- |\n"
                "| 6 | `old v3 data v1.1` | `19K` | `foo` | 是 |\n"
                "| 7 | `old v2 data v2 trainset` | `537K` | `bar` | 是 |\n"
                "\n"
                "### 7. `old v2 data v2 trainset`\n\n"
                "- 目标：扩容训练集。\n"
                "- 说明：不带 eval。\n",
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
            "\n"
            "### 7. `old v2 data v2 trainset`\n"
            "\n"
            "- 目标：扩容训练集。\n"
            "- 说明：不带 eval。\n",
        )

    def test_main_rejects_unknown_selected_dataset(self) -> None:
        with TemporaryDirectory() as tmp_dir:
            index_path = Path(tmp_dir) / "dataset_versions.md"
            index_path.write_text(
                "# demo\n\n"
                "| ID | 版本名 | 数据量（train+valid+eval） | 简要说明 | 标记 |\n"
                "| ---: | --- | ---: | --- | --- |\n"
                "| 7 | `old v2 data v2 trainset` | `537K` | `bar` | 是 |\n",
                encoding="utf-8",
            )

            with mock.patch.object(setting, "TARGET_DATASET_VERSIONS_PATH", index_path):
                stdout = io.StringIO()
                with redirect_stdout(stdout):
                    exit_code = zpdata.main(["8"])

        self.assertEqual(exit_code, 1)
        self.assertEqual(stdout.getvalue(), "unknown dataset number: 8\n")

    def test_main_reports_missing_dataset_versions_file(self) -> None:
        missing_path = Path("/tmp/utils_zp_missing_dataset_versions.md")

        with mock.patch.object(setting, "TARGET_DATASET_VERSIONS_PATH", missing_path):
            stdout = io.StringIO()
            with redirect_stdout(stdout):
                exit_code = zpdata.main([])

        self.assertEqual(exit_code, 1)
        self.assertEqual(stdout.getvalue(), f"missing dataset versions file: {missing_path}\n")


if __name__ == "__main__":
    unittest.main()
