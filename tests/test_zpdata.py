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

    def test_collect_datasets_includes_marked_derived_rows(self) -> None:
        with TemporaryDirectory() as tmp_dir:
            index_path = Path(tmp_dir) / "dataset_versions.yaml"
            index_path.write_text(
                "title: demo\n"
                "versions:\n"
                "  - id: '10'\n"
                "    name: old v2 data v2.0\n"
                "    size: 49K\n"
                "    summary: base\n"
                "    target_path: data/old_v2_data_v2_0/\n"
                "    marked: false\n"
                "    derived_versions:\n"
                "      - id: '10.1'\n"
                "        name: old v2 data v2.0 teacher softlabel\n"
                "        size: 49K\n"
                "        summary: derived\n"
                "        target_path: data/old_v2_data_v2_0_teacher_softlabel/\n"
                "        marked: true\n",
                encoding="utf-8",
            )

            datasets = zpdata.collect_datasets(index_path)

        self.assertEqual(
            datasets,
            [
                zpdata.DatasetInfo(
                    dataset_id="10.1",
                    name="old v2 data v2.0 teacher softlabel",
                    size="49K",
                    summary="derived",
                    target_path="data/old_v2_data_v2_0_teacher_softlabel/",
                )
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

    def test_main_lists_related_derived_versions_for_root_dataset(self) -> None:
        with TemporaryDirectory() as tmp_dir:
            index_path = Path(tmp_dir) / "dataset_versions.yaml"
            index_path.write_text(
                "title: demo\n"
                "versions:\n"
                "  - id: '10'\n"
                "    name: old v2 data v2.0\n"
                "    size: 49K\n"
                "    summary: base\n"
                "    target_path: data/old_v2_data_v2_0/\n"
                "    marked: true\n"
                "    derived_versions:\n"
                "      - id: '10.1'\n"
                "        name: old v2 data v2.0 teacher softlabel\n"
                "        relation: teacher_softlabel\n"
                "        size: 49K\n"
                "        summary: derived\n"
                "        target_path: data/old_v2_data_v2_0_teacher_softlabel/\n"
                "        marked: false\n"
                "    detail_markdown: |\n"
                "      ### 10. `old v2 data v2.0`\n"
                "\n"
                "      - 说明：有派生版。\n",
                encoding="utf-8",
            )

            with mock.patch.object(setting, "TARGET_DATASET_VERSIONS_PATH", index_path):
                stdout = io.StringIO()
                with redirect_stdout(stdout):
                    exit_code = zpdata.main(["10"])

        self.assertEqual(exit_code, 0)
        self.assertEqual(
            stdout.getvalue(),
            f"Target dataset versions path: {index_path}\n"
            "\n"
            "ID: 10\n"
            "名称: old v2 data v2.0\n"
            "数据量: 49K\n"
            "简要说明: base\n"
            "目标路径: data/old_v2_data_v2_0/\n"
            "\n"
            "相关派生版本:\n"
            "- 10.1 | teacher_softlabel | old v2 data v2.0 teacher softlabel | derived\n"
            "\n"
            "### 10. `old v2 data v2.0`\n"
            "\n"
            "- 说明：有派生版。\n",
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

    def test_main_prints_selected_derived_dataset_detail_with_legacy_detail_fallback(self) -> None:
        with TemporaryDirectory() as tmp_dir:
            index_path = Path(tmp_dir) / "dataset_versions.yaml"
            index_path.write_text(
                "title: demo\n"
                "versions:\n"
                "  - id: '11'\n"
                "    name: old v3 data v1.2\n"
                "    size: 23K\n"
                "    summary: base\n"
                "    target_path: data/old_v3_data_v1_2/\n"
                "    marked: true\n"
                "    derived_versions:\n"
                "      - id: '11.1'\n"
                "        legacy_version_id: 12\n"
                "        name: old v3 data v1.2 teacher softlabel\n"
                "        size: 23K\n"
                "        summary: derived\n"
                "        target_path: data/old_v3_data_v1_2_teacher_softlabel/\n"
                "        marked: false\n"
                "  - id: '12'\n"
                "    derived_id: '11.1'\n"
                "    relation: teacher_softlabel\n"
                "    name: old v3 data v1.2 teacher softlabel\n"
                "    size: 23K\n"
                "    summary: derived\n"
                "    target_path: data/old_v3_data_v1_2_teacher_softlabel/\n"
                "    marked: false\n"
                "    detail_markdown: |\n"
                "      ### 12. `old v3 data v1.2 teacher softlabel`\n"
                "\n"
                "      - 说明：来自 legacy 顶层条目。\n",
                encoding="utf-8",
            )

            with mock.patch.object(setting, "TARGET_DATASET_VERSIONS_PATH", index_path):
                stdout = io.StringIO()
                with redirect_stdout(stdout):
                    exit_code = zpdata.main(["11.1"])

        self.assertEqual(exit_code, 0)
        self.assertEqual(
            stdout.getvalue(),
            f"Target dataset versions path: {index_path}\n"
            "\n"
            "ID: 11.1\n"
            "名称: old v3 data v1.2 teacher softlabel\n"
            "数据量: 23K\n"
            "简要说明: derived\n"
            "目标路径: data/old_v3_data_v1_2_teacher_softlabel/\n"
            "\n"
            "父版本: 11 | old v3 data v1.2\n"
            "派生关系: teacher_softlabel\n"
            "\n"
            "### 12. `old v3 data v1.2 teacher softlabel`\n"
            "\n"
            "- 说明：来自 legacy 顶层条目。\n",
        )

    def test_main_prints_legacy_dataset_detail_from_structured_derived_item(self) -> None:
        with TemporaryDirectory() as tmp_dir:
            index_path = Path(tmp_dir) / "dataset_versions.yaml"
            index_path.write_text(
                "title: demo\n"
                "versions:\n"
                "  - id: '5'\n"
                "    name: old v3 data v1.0\n"
                "    size: 19K\n"
                "    summary: root\n"
                "    target_path: data/root/\n"
                "    marked: false\n"
                "    derived_versions:\n"
                "      - id: '5.2'\n"
                "        legacy_version_id: 11\n"
                "        name: old v3 data v1.2\n"
                "        relation: rebuild_no_dedup\n"
                "        size: 23K\n"
                "        summary: derived\n"
                "        target_path: data/root_v1_2/\n"
                "        marked: true\n"
                "        detail_markdown: |\n"
                "          ### 5.2 `old v3 data v1.2`\n"
                "\n"
                "          - 说明：结构化派生节点承载完整说明。\n"
                "  - id: '11'\n"
                "    name: old v3 data v1.2\n"
                "    derived_id: '5.2'\n"
                "    derived_from_version_id: 5\n"
                "    relation: rebuild_no_dedup\n",
                encoding="utf-8",
            )

            with mock.patch.object(setting, "TARGET_DATASET_VERSIONS_PATH", index_path):
                stdout = io.StringIO()
                with redirect_stdout(stdout):
                    exit_code = zpdata.main(["11"])

        self.assertEqual(exit_code, 0)
        self.assertEqual(
            stdout.getvalue(),
            f"Target dataset versions path: {index_path}\n"
            "\n"
            "ID: 11\n"
            "名称: old v3 data v1.2\n"
            "数据量: 23K\n"
            "简要说明: derived\n"
            "目标路径: data/root_v1_2/\n"
            "\n"
            "父版本: 5 | old v3 data v1.0\n"
            "派生关系: rebuild_no_dedup\n"
            "\n"
            "### 5.2 `old v3 data v1.2`\n"
            "\n"
            "- 说明：结构化派生节点承载完整说明。\n",
        )

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

    def test_main_prints_dataset_tree(self) -> None:
        with TemporaryDirectory() as tmp_dir:
            index_path = Path(tmp_dir) / "dataset_versions.yaml"
            index_path.write_text(
                "title: demo\n"
                "versions:\n"
                "  - id: '1'\n"
                "    name: old v2 data v1.0\n"
                "    size: 157K\n"
                "    summary: root\n"
                "    target_path: data/root/\n"
                "    marked: false\n"
                "    derived_versions:\n"
                "      - id: '1.1'\n"
                "        legacy_version_id: 2\n"
                "        name: old v2 data v1.0 balanced\n"
                "        size: 68K\n"
                "        summary: child\n"
                "        target_path: data/root_balanced/\n"
                "        marked: false\n"
                "      - id: '1.2'\n"
                "        legacy_version_id: 3\n"
                "        name: old v2 data v1.1\n"
                "        size: 157K\n"
                "        summary: child2\n"
                "        target_path: data/root_v1_1/\n"
                "        marked: false\n"
                "        derived_versions:\n"
                "          - id: '1.2.1'\n"
                "            legacy_version_id: 4\n"
                "            name: old v2 data v1.1 balanced\n"
                "            size: 68K\n"
                "            summary: child3\n"
                "            target_path: data/root_v1_1_balanced/\n"
                "            marked: false\n"
                "  - id: '3'\n"
                "    derived_id: '1.2'\n"
                "    derived_from_version_id: 1\n"
                "    name: old v2 data v1.1\n"
                "    size: 157K\n"
                "    summary: legacy child2\n"
                "    target_path: data/root_v1_1/\n"
                "    marked: false\n"
                "  - id: '4'\n"
                "    derived_id: '1.2.1'\n"
                "    derived_from_version_id: 3\n"
                "    name: old v2 data v1.1 balanced\n"
                "    size: 68K\n"
                "    summary: legacy child3\n"
                "    target_path: data/root_v1_1_balanced/\n"
                "    marked: false\n"
                "    derived_versions:\n"
                "      - id: '1.2.1.1'\n"
                "        legacy_version_id: 8\n"
                "        name: old v2 data v1.2 balanced\n"
                "        size: 68K\n"
                "        summary: child4\n"
                "        target_path: data/root_v1_2_balanced/\n"
                "        marked: false\n"
                "  - id: '5'\n"
                "    name: old v3 data v1.0\n"
                "    size: 19K\n"
                "    summary: root3\n"
                "    target_path: data/root3/\n"
                "    marked: false\n"
                "    derived_versions:\n"
                "      - id: '5.1'\n"
                "        legacy_version_id: 6\n"
                "        name: old v3 data v1.1\n"
                "        size: 19K\n"
                "        summary: child5\n"
                "        target_path: data/root3_v1_1/\n"
                "        marked: false\n"
                "  - id: '6'\n"
                "    derived_id: '5.1'\n"
                "    derived_from_version_id: 5\n"
                "    name: old v3 data v1.1\n"
                "    size: 19K\n"
                "    summary: legacy child5\n"
                "    target_path: data/root3_v1_1/\n"
                "    marked: false\n"
                "    derived_versions:\n"
                "      - id: '5.1.1'\n"
                "        legacy_version_id: 9\n"
                "        name: old v3 data v1.1 teacher softlabel\n"
                "        size: 19K\n"
                "        summary: child6\n"
                "        target_path: data/root3_v1_1_teacher/\n"
                "        marked: false\n"
                "  - id: '10'\n"
                "    name: old v2 data v2.0\n"
                "    size: 49K\n"
                "    summary: root2\n"
                "    target_path: data/root2/\n"
                "    marked: true\n"
                "    derived_versions:\n"
                "      - id: '10.1'\n"
                "        name: old v2 data v2.0 teacher softlabel\n"
                "        size: 49K\n"
                "        summary: child4\n"
                "        target_path: data/root2_teacher/\n"
                "        marked: false\n",
                encoding="utf-8",
            )

            with mock.patch.object(setting, "TARGET_DATASET_VERSIONS_PATH", index_path):
                stdout = io.StringIO()
                with redirect_stdout(stdout):
                    exit_code = zpdata.main(["-tree"])

        self.assertEqual(exit_code, 0)
        self.assertEqual(
            stdout.getvalue(),
            f"Target dataset versions path: {index_path}\n"
            "\n"
            "1 old v2 data v1.0\n"
            "├── 1.1 old v2 data v1.0 balanced (legacy: 2)\n"
            "└── 1.2 old v2 data v1.1 (legacy: 3)\n"
            "    └── 1.2.1 old v2 data v1.1 balanced (legacy: 4)\n"
            "        └── 1.2.1.1 old v2 data v1.2 balanced (legacy: 8)\n"
            "\n"
            "5 old v3 data v1.0\n"
            "└── 5.1 old v3 data v1.1 (legacy: 6)\n"
            "    └── 5.1.1 old v3 data v1.1 teacher softlabel (legacy: 9)\n"
            "\n"
            "10 old v2 data v2.0\n"
            "└── 10.1 old v2 data v2.0 teacher softlabel\n",
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

    def test_main_marks_derived_dataset_when_requested(self) -> None:
        with TemporaryDirectory() as tmp_dir:
            index_path = Path(tmp_dir) / "dataset_versions.yaml"
            index_path.write_text(
                "title: demo\n"
                "versions:\n"
                "  - id: '10'\n"
                "    name: foo\n"
                "    size: 1K\n"
                "    summary: bar\n"
                "    target_path: data/foo/\n"
                "    marked: false\n"
                "    derived_versions:\n"
                "      - id: '10.1'\n"
                "        name: foo derived\n"
                "        size: 1K\n"
                "        summary: baz\n"
                "        target_path: data/foo_derived/\n"
                "        marked: false\n",
                encoding="utf-8",
            )

            with mock.patch.object(setting, "TARGET_DATASET_VERSIONS_PATH", index_path):
                stdout = io.StringIO()
                with redirect_stdout(stdout):
                    exit_code = zpdata.main(["-m", "10.1"])

            document = yaml.safe_load(index_path.read_text(encoding="utf-8"))

        self.assertEqual(exit_code, 0)
        self.assertEqual(stdout.getvalue(), "marked dataset 10.1: foo derived\n")
        self.assertTrue(document["versions"][0]["derived_versions"][0]["marked"])

    def test_main_marks_legacy_dataset_alias_on_structured_derived_item(self) -> None:
        with TemporaryDirectory() as tmp_dir:
            index_path = Path(tmp_dir) / "dataset_versions.yaml"
            index_path.write_text(
                "title: demo\n"
                "versions:\n"
                "  - id: '5'\n"
                "    name: root\n"
                "    size: 1K\n"
                "    summary: root summary\n"
                "    target_path: data/root/\n"
                "    marked: false\n"
                "    derived_versions:\n"
                "      - id: '5.2'\n"
                "        legacy_version_id: 11\n"
                "        name: derived\n"
                "        size: 1K\n"
                "        summary: derived summary\n"
                "        target_path: data/derived/\n"
                "        marked: false\n"
                "  - id: '11'\n"
                "    name: derived legacy alias\n"
                "    derived_id: '5.2'\n"
                "    derived_from_version_id: 5\n",
                encoding="utf-8",
            )

            with mock.patch.object(setting, "TARGET_DATASET_VERSIONS_PATH", index_path):
                stdout = io.StringIO()
                with redirect_stdout(stdout):
                    exit_code = zpdata.main(["-m", "11"])

            document = yaml.safe_load(index_path.read_text(encoding="utf-8"))

        self.assertEqual(exit_code, 0)
        self.assertEqual(stdout.getvalue(), "marked dataset 5.2: derived\n")
        self.assertTrue(document["versions"][0]["derived_versions"][0]["marked"])
        self.assertNotIn("marked", document["versions"][1])


if __name__ == "__main__":
    unittest.main()
