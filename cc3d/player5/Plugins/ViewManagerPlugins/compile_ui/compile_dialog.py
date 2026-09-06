from __future__ import annotations

from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtWidgets import QDialog, QDialogButtonBox, QLabel, QProgressBar, QVBoxLayout

from .compile_runner import CompiledSteppableCompileRunner


class CompiledSteppableCompileDialog(QDialog):
    succeeded = pyqtSignal(dict, str)
    failed = pyqtSignal(str, str)
    canceled = pyqtSignal()

    def __init__(self, project_path: str, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Compiling C++ Steppables")
        self.setModal(True)
        self.setWindowModality(Qt.ApplicationModal)
        self.setMinimumWidth(520)

        self._thread = QThread(self)
        self._worker = CompiledSteppableCompileRunner(project_path)
        self._worker.moveToThread(self._thread)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 16, 18, 14)
        layout.setSpacing(10)

        title = QLabel("<b>Compiling C++ steppables...</b>", self)
        title.setTextInteractionFlags(Qt.TextSelectableByMouse)
        layout.addWidget(title)

        message = QLabel("Please wait while Player builds the compiled steppables required by this simulation.", self)
        message.setWordWrap(True)
        message.setTextInteractionFlags(Qt.TextSelectableByMouse)
        layout.addWidget(message)

        progress = QProgressBar(self)
        progress.setRange(0, 0)
        layout.addWidget(progress)

        button_box = QDialogButtonBox(self)
        self._interrupt_button = button_box.addButton("Interrupt Compilation", QDialogButtonBox.RejectRole)
        self._interrupt_button.clicked.connect(self._interrupt)
        layout.addWidget(button_box)

        self._thread.started.connect(self._worker.run)
        self._worker.finished.connect(self._finish_success)
        self._worker.failed.connect(self._finish_failure)
        self._worker.canceled.connect(self._finish_canceled)
        self._worker.finished.connect(self._thread.quit)
        self._worker.failed.connect(self._thread.quit)
        self._worker.canceled.connect(self._thread.quit)
        self._thread.finished.connect(self._worker.deleteLater)

    def start(self) -> None:
        self.show()
        self._thread.start()

    def closeEvent(self, event):
        self._interrupt()
        event.ignore()

    def _interrupt(self) -> None:
        self._interrupt_button.setEnabled(False)
        self._interrupt_button.setText("Interrupting...")
        self._worker.cancel()

    def _finish_success(self, summary: dict, formatted_summary: str) -> None:
        self.accept()
        self.succeeded.emit(summary, formatted_summary)

    def _finish_failure(self, error: str, formatted_summary: str) -> None:
        self.reject()
        self.failed.emit(error, formatted_summary)

    def _finish_canceled(self) -> None:
        self.reject()
        self.canceled.emit()
