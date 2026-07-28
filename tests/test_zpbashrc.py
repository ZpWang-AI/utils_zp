from __future__ import annotations

import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import mock

from utils_zp.cli import zpbashrc


class ZPBashrcTests(unittest.TestCase):
    def test_update_bashrc_appends_source_lines_and_is_idempotent(self) -> None:
        with TemporaryDirectory() as tmp_dir:
            tmp_root = Path(tmp_dir)
            bashrc_path = tmp_root / ".bashrc"
            bashrc_path.write_text("export DEMO=1\n", encoding="utf-8")

            shell_dir = tmp_root / "shell"
            shell_dir.mkdir()
            bashrc_zp_path = shell_dir / "bashrc_zp.sh"
            bashrc_zp_path.write_text("# shared config\n", encoding="utf-8")
            bashrc_local_path = shell_dir / "bashrc_zp.local.sh"

            with mock.patch.object(zpbashrc, "BASHRC_ZP_PATH", bashrc_zp_path), mock.patch.object(
                zpbashrc, "BASHRC_ZP_LOCAL_PATH", bashrc_local_path
            ):
                changed_first = zpbashrc.update_bashrc(bashrc_path)
                changed_second = zpbashrc.update_bashrc(bashrc_path)
                content = bashrc_path.read_text(encoding="utf-8")
                local_exists = bashrc_local_path.exists()

        self.assertTrue(changed_first)
        self.assertFalse(changed_second)
        self.assertTrue(local_exists)
        self.assertEqual(content.count(f". {bashrc_zp_path}\n"), 1)
        self.assertEqual(content.count(f". {bashrc_local_path}\n"), 1)

    def test_update_bashrc_replaces_stale_source_lines(self) -> None:
        with TemporaryDirectory() as tmp_dir:
            tmp_root = Path(tmp_dir)
            bashrc_path = tmp_root / ".bashrc"
            bashrc_path.write_text(
                ". /old/location/bashrc_zp.sh\n. /old/location/bashrc_zp.local.sh\n",
                encoding="utf-8",
            )

            shell_dir = tmp_root / "shell"
            shell_dir.mkdir()
            bashrc_zp_path = shell_dir / "bashrc_zp.sh"
            bashrc_zp_path.write_text("# shared config\n", encoding="utf-8")
            bashrc_local_path = shell_dir / "bashrc_zp.local.sh"

            with mock.patch.object(zpbashrc, "BASHRC_ZP_PATH", bashrc_zp_path), mock.patch.object(
                zpbashrc, "BASHRC_ZP_LOCAL_PATH", bashrc_local_path
            ):
                changed = zpbashrc.update_bashrc(bashrc_path)
                content = bashrc_path.read_text(encoding="utf-8")

        self.assertTrue(changed)
        self.assertEqual(content, f". {bashrc_zp_path}\n. {bashrc_local_path}\n")


if __name__ == "__main__":
    unittest.main()
