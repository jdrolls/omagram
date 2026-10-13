"""Blackbox regression test for telegram_tui/media_probe.py's exit code.

Textual's App.run() swallows an exception raised from compose() and still
exits 0, so a bad path or missing argument used to print a traceback yet
look like success to any script checking the exit code.
"""

from __future__ import annotations

import subprocess
import sys
import unittest


class MediaProbeExitCodeTests(unittest.TestCase):
    def _run(self, *args: str) -> subprocess.CompletedProcess:
        return subprocess.run(
            [sys.executable, "-m", "telegram_tui.media_probe", *args],
            capture_output=True,
            text=True,
            timeout=10,
        )

    def test_missing_argument_exits_nonzero(self):
        result = self._run()
        self.assertNotEqual(result.returncode, 0)

    def test_missing_file_exits_nonzero(self):
        result = self._run("/nonexistent/path/to/image.jpg")
        self.assertNotEqual(result.returncode, 0)


if __name__ == "__main__":
    unittest.main()
