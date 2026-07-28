from __future__ import annotations

import io
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import mock

from utils_zp.cli import zprules


class ZPRulesCLITests(unittest.TestCase):
    def test_main_prints_entry_path_and_rules_content(self) -> None:
        with TemporaryDirectory() as tmp_dir:
            rules_path = Path(tmp_dir) / "README.agent.md"
            rules_path.write_text("# demo rules\nline 2\n", encoding="utf-8")

            with mock.patch.object(zprules, "RULES_PATH", rules_path):
                stdout = io.StringIO()
                with redirect_stdout(stdout):
                    exit_code = zprules.main()

        self.assertEqual(exit_code, 0)
        self.assertEqual(
            stdout.getvalue(),
            f"Agent Entry Path: {rules_path}\n\n# demo rules\nline 2\n",
        )

    def test_main_reports_missing_rules_file(self) -> None:
        missing_path = Path("/tmp/utils_zp_missing_rules.md")

        with mock.patch.object(zprules, "RULES_PATH", missing_path):
            stdout = io.StringIO()
            with redirect_stdout(stdout):
                exit_code = zprules.main()

        self.assertEqual(exit_code, 1)
        self.assertEqual(stdout.getvalue(), f"missing rules file: {missing_path}\n")


if __name__ == "__main__":
    unittest.main()
