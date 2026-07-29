from __future__ import annotations

import builtins
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import mock

from utils_zp.cuda import monitor


class MonitorTests(unittest.TestCase):
    def test_plot_monitor_log_reports_missing_matplotlib(self) -> None:
        original_import = builtins.__import__

        def fake_import(name, globals=None, locals=None, fromlist=(), level=0):
            if name == "matplotlib.pyplot":
                error = ModuleNotFoundError("No module named 'matplotlib'")
                error.name = "matplotlib"
                raise error
            return original_import(name, globals, locals, fromlist, level)

        with TemporaryDirectory() as tmp_dir:
            tmp_root = Path(tmp_dir)
            log_path = tmp_root / "monitor.jsonl"
            output_path = tmp_root / "monitor.png"
            log_path.write_text(
                '{"type":"meta","device_indices":[0],"started_at":0,'
                '"gpus":[{"index":0,"total_mb":24000}]}\n'
                '{"type":"sample","elapsed_s":0.1,"memory_used_mb":{"0":1024}}\n',
                encoding="utf-8",
            )

            with mock.patch("builtins.__import__", side_effect=fake_import):
                with self.assertRaisesRegex(
                    RuntimeError,
                    "plot_monitor_log requires matplotlib",
                ):
                    monitor.plot_monitor_log(log_path, output_path)


if __name__ == "__main__":
    unittest.main()
