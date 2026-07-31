from __future__ import annotations

import io
import unittest
from contextlib import redirect_stdout

from utils_zp import __version__
from utils_zp.cli import main


class MainCLITests(unittest.TestCase):
    def test_main_prints_commands_with_summaries(self) -> None:
        stdout = io.StringIO()
        with redirect_stdout(stdout):
            exit_code = main.main()

        self.assertEqual(exit_code, 0)
        self.assertEqual(
            stdout.getvalue(),
            "\n".join(
                [
                    "utils_zp",
                    f"version: {__version__}",
                    "commands:",
                    "  zpbashrc: 更新 ~/.bashrc",
                    "  zpburn: 持续占用指定 GPU 到目标利用率",
                    "  zpdata: 查看 data/dataset_versions.md 里标记的数据集",
                    "  zpexp: 查看 exp/exp_versions.md 里标记的实验",
                    "  zpjobs: 查看当前 jobs 清单",
                    "  zppremodel/zppremodels: 查看当前支持的预训练模型",
                    "  zprules: 查看当前 agent 规则入口",
                    "",
                ]
            ),
        )


if __name__ == "__main__":
    unittest.main()
