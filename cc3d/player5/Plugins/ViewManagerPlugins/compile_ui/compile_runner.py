from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path

from PyQt5.QtCore import QObject, pyqtSignal


class CompiledSteppableCompileRunner(QObject):
    finished = pyqtSignal(dict, str)
    failed = pyqtSignal(str, str)
    canceled = pyqtSignal()

    def __init__(self, project_path: str, parent=None):
        super().__init__(parent)
        self.project_path = project_path
        self._process = None
        self._cancel_requested = False

    def cancel(self) -> None:
        self._cancel_requested = True
        if self._process is None or self._process.poll() is not None:
            return

        self._process.terminate()
        try:
            self._process.wait(timeout=3)
        except subprocess.TimeoutExpired:
            self._process.kill()
            self._process.wait()

    def run(self) -> None:
        with tempfile.TemporaryDirectory(prefix="cc3d_compile_") as tmp_dir:
            result_path = Path(tmp_dir) / "compiled_steppable_summary.json"
            command = [
                sys.executable,
                "-m",
                "cc3d.player5.Plugins.ViewManagerPlugins.compile_ui.compile_project",
                "--project",
                self.project_path,
                "--result-json",
                str(result_path),
            ]

            self._process = subprocess.Popen(
                command,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            stdout, stderr = self._process.communicate()

            if self._cancel_requested:
                self.canceled.emit()
                return

            if result_path.exists():
                result = json.loads(result_path.read_text(encoding="utf-8"))
                formatted_summary = result.get("formatted_summary") or ""
                extra_output = "\n".join(part for part in (stdout, stderr) if part)
                if extra_output:
                    formatted_summary = "\n".join(part for part in (formatted_summary, extra_output) if part)
                if result.get("success"):
                    self.finished.emit(result.get("summary") or {}, formatted_summary)
                else:
                    self.failed.emit(result.get("error") or "Compilation failed.", formatted_summary)
                return

            detail = "\n".join(part for part in (stdout, stderr) if part)
            self.failed.emit("Compilation process did not produce a result.", detail)
