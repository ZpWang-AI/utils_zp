from __future__ import annotations

import io
import unittest
from contextlib import redirect_stdout
from unittest import mock

from utils_zp.cli import zpburn


class _FakeProgressBar:
    def __init__(self) -> None:
        self.total_updates = 0
        self.closed = False

    def update(self, value: int) -> None:
        self.total_updates += value

    def close(self) -> None:
        self.closed = True


class ZPBurnTests(unittest.TestCase):
    def test_main_passes_gpu_id_and_progress_callback(self) -> None:
        fake_progress = _FakeProgressBar()
        captured: dict[str, object] = {}

        def fake_stress_gpu_to_target_usage(*, gpu_id: int, progress_callback):
            captured["gpu_id"] = gpu_id
            captured["progress_callback"] = progress_callback
            progress_callback(3)

        with mock.patch.object(zpburn, "tqdm", return_value=fake_progress), mock.patch.object(
            zpburn, "stress_gpu_to_target_usage", side_effect=fake_stress_gpu_to_target_usage
        ):
            exit_code = zpburn.main(["7"])

        self.assertEqual(exit_code, 0)
        self.assertEqual(captured["gpu_id"], 7)
        self.assertIs(captured["progress_callback"].__self__, fake_progress)
        self.assertEqual(captured["progress_callback"].__name__, "update")
        self.assertEqual(fake_progress.total_updates, 3)
        self.assertTrue(fake_progress.closed)

    def test_main_returns_130_on_keyboard_interrupt(self) -> None:
        fake_progress = _FakeProgressBar()

        with mock.patch.object(zpburn, "tqdm", return_value=fake_progress), mock.patch.object(
            zpburn, "stress_gpu_to_target_usage", side_effect=KeyboardInterrupt
        ):
            exit_code = zpburn.main(["3"])

        self.assertEqual(exit_code, 130)
        self.assertTrue(fake_progress.closed)

    def test_main_reports_missing_torch_dependency(self) -> None:
        fake_progress = _FakeProgressBar()
        error = ModuleNotFoundError("No module named 'torch'")
        error.name = "torch"

        with mock.patch.object(zpburn, "tqdm", return_value=fake_progress), mock.patch.object(
            zpburn, "stress_gpu_to_target_usage", side_effect=error
        ):
            stdout = io.StringIO()
            with redirect_stdout(stdout):
                exit_code = zpburn.main(["3"])

        self.assertEqual(exit_code, 1)
        self.assertEqual(
            stdout.getvalue(),
            "zpburn requires torch. Please install torch in the current environment first.\n",
        )
        self.assertTrue(fake_progress.closed)


if __name__ == "__main__":
    unittest.main()
