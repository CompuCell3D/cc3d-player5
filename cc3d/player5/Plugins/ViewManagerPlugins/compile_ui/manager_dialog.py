from __future__ import annotations

from pathlib import Path

from PyQt5.QtCore import QObject, QThread, Qt, pyqtSignal
from PyQt5.QtGui import QColor, QBrush, QFont
from PyQt5.QtWidgets import (
    QAbstractItemView, QApplication, QDialog, QFormLayout, QHBoxLayout, QLabel, QMenu,
    QLineEdit, QProgressBar, QPushButton, QTabWidget, QTreeWidget, QTreeWidgetItem,
    QTextEdit,
    QVBoxLayout, QWidget,
)

from cc3d.core.CompiledSteppableAutoCompiler import compiled_steppable_project_status
from cc3d.core.CompiledSteppableCompilerSettings import (
    current_platform_key, load_settings, refresh_detected_compiler, save_settings, settings_path,
)
from cc3d.player5.Utilities import show_text_messagebox
from .compile_dialog import CompiledSteppableCompileDialog


class _CompilerDetectionWorker(QObject):
    finished = pyqtSignal(object)
    failed = pyqtSignal(str)

    def run(self):
        try:
            self.finished.emit(refresh_detected_compiler(load_settings()))
        except Exception as error:
            self.failed.emit(str(error))


class CompiledSteppablesDialog(QDialog):
    """Inspect and manage the compiled steppables for the selected project."""

    def __init__(self, project_path: str, simulation_running=False, parent=None):
        super().__init__(parent)
        self.project_path = Path(project_path).resolve()
        self.simulation_running = simulation_running
        self.status = None
        self._detection_thread = None
        self._detection_worker = None
        self.setWindowTitle("Compiled Steppables")
        self.resize(1050, 620)

        tabs = QTabWidget(self)
        self.tabs = tabs
        tabs.addTab(self._simulation_tab(), "Simulation")
        tabs.addTab(self._settings_tab(), "Compiler settings")
        tabs.currentChanged.connect(self._tab_changed)
        layout = QVBoxLayout(self)
        layout.addWidget(tabs)
        self.refresh_status()

    def _simulation_tab(self):
        page = QWidget(self)
        layout = QVBoxLayout(page)
        self.warning = QLabel(page)
        self.warning.setWordWrap(True)
        layout.addWidget(self.warning)
        self.tree = QTreeWidget(page)
        self.tree.setHeaderLabels(["Property", "Value", "Validation"])
        self.tree.setAlternatingRowColors(True)
        self.tree.setSelectionMode(QAbstractItemView.SingleSelection)
        self.tree.setUniformRowHeights(False)
        self.tree.setContextMenuPolicy(Qt.CustomContextMenu)
        self.tree.customContextMenuRequested.connect(self._show_tree_context_menu)
        self.tree.setStyleSheet(
            "QTreeWidget { border: 1px solid #c8cdd3; }"
            "QTreeWidget::item { padding: 2px; }"
            "QTreeWidget::item:selected { background: #cfe8ff; color: #1f2933; }"
        )
        self.tree.header().setStretchLastSection(False)
        self.tree.header().setSectionResizeMode(0, self.tree.header().ResizeToContents)
        self.tree.header().setSectionResizeMode(1, self.tree.header().Stretch)
        self.tree.header().setSectionResizeMode(2, self.tree.header().ResizeToContents)
        layout.addWidget(self.tree)

        self.details = QTextEdit(page)
        self.details.setReadOnly(True)
        self.details.setMaximumHeight(130)
        layout.addWidget(self.details)

        buttons = QHBoxLayout()
        self.refresh_button = QPushButton("Refresh")
        self.compile_button = QPushButton("Compile now")
        self.clean_button = QPushButton("Clean")
        for button in (self.clean_button, self.compile_button, self.refresh_button):
            buttons.addWidget(button)
        layout.addLayout(buttons)
        self.refresh_button.clicked.connect(self.refresh_status)
        self.compile_button.clicked.connect(lambda: self._compile(False))
        self.clean_button.clicked.connect(self.clean_artifacts)
        return page

    def _settings_tab(self):
        page = QWidget(self)
        layout = QVBoxLayout(page)
        form = QFormLayout()
        self.settings_path_label = QLabel(str(settings_path()))
        self.platform_label = QLabel(current_platform_key())
        self.compiler_label = QLabel("Not loaded")
        self.detected_label = QLabel("Switch to this tab to detect compilers")
        self.detection_status = QLabel()
        self.detection_spinner = QProgressBar()
        self.detection_spinner.setRange(0, 0)
        self.detection_spinner.setVisible(False)
        for label in (self.settings_path_label, self.platform_label, self.compiler_label,
                      self.detected_label, self.detection_status):
            label.setTextInteractionFlags(Qt.TextSelectableByMouse | Qt.TextSelectableByKeyboard)
            label.setWordWrap(True)
        form.addRow(self._settings_key_label("Settings file:"), self.settings_path_label)
        form.addRow(self._settings_key_label("Platform:"), self.platform_label)
        form.addRow(self._settings_key_label("Selected compiler:"), self.compiler_label)
        form.addRow(self._settings_key_label("Detected:"), self.detected_label)
        form.addRow(self._settings_key_label("Status:"), self.detection_status)
        form.addRow("", self.detection_spinner)
        layout.addLayout(form)
        buttons = QHBoxLayout()
        refresh = self.refresh_detection_button = QPushButton("Refresh detection")
        latest = self.latest_button = QPushButton("Use latest detected compiler")
        reset = self.reset_button = QPushButton("Reset to automatic")
        apply_button = self.apply_button = QPushButton("Apply / Save")
        for button in (refresh, latest, reset, apply_button):
            buttons.addWidget(button)
        layout.addLayout(buttons)
        refresh.clicked.connect(self.start_compiler_detection)
        latest.clicked.connect(lambda: self.set_policy("latest"))
        reset.clicked.connect(self.reset_settings)
        apply_button.clicked.connect(self.save_settings)
        self.settings = None
        return page

    @staticmethod
    def _settings_key_label(text):
        label = QLabel(text)
        font = label.font()
        font.setBold(True)
        label.setFont(font)
        return label

    def _tab_changed(self, index):
        if index == 1:
            self.start_compiler_detection()

    def _set_settings_controls_enabled(self, enabled):
        for button in (self.refresh_detection_button, self.latest_button,
                       self.reset_button, self.apply_button):
            button.setEnabled(enabled)

    def start_compiler_detection(self):
        if self._detection_thread is not None and self._detection_thread.isRunning():
            return
        self.detection_status.setText("Detecting compiler...")
        self.detection_spinner.setVisible(True)
        self._set_settings_controls_enabled(False)
        self._detection_thread = QThread(self)
        self._detection_worker = _CompilerDetectionWorker()
        self._detection_worker.moveToThread(self._detection_thread)
        self._detection_thread.started.connect(self._detection_worker.run)
        self._detection_worker.finished.connect(self._compiler_detection_finished)
        self._detection_worker.failed.connect(self._compiler_detection_failed)
        self._detection_worker.finished.connect(self._detection_thread.quit)
        self._detection_worker.failed.connect(self._detection_thread.quit)
        self._detection_thread.finished.connect(self._detection_worker.deleteLater)
        self._detection_thread.finished.connect(self._detection_complete)
        self._detection_thread.start()

    def _compiler_detection_finished(self, settings):
        self.settings = settings
        self._display_settings()

    def _compiler_detection_failed(self, error):
        self.detection_status.setText(f"Compiler detection failed: {error}")

    def _detection_complete(self):
        self.detection_spinner.setVisible(False)
        self._set_settings_controls_enabled(True)
        self._detection_thread = None
        self._detection_worker = None
        if self.detection_status.text() == "Detecting compiler...":
            self.detection_status.setText("Detection complete")

    def refresh_status(self):
        try:
            self.status = compiled_steppable_project_status(str(self.project_path))
        except Exception as error:
            self.warning.setText(f"Unable to inspect compiled steppables: {error}")
            self.tree.clear()
            return
        self.tree.clear()
        plans = self.status.plans
        self.warning.setText("" if all(plan.metadata_path.exists() for plan in plans)
                             else "Warning: one or more artifacts have no valid metadata sidecar and must be rebuilt.")
        root = QTreeWidgetItem(self.tree, ["Compiled Steppables", "", ""])
        root.setFont(0, self._heading_font())
        for plan in plans:
            branch = QTreeWidgetItem(root, [Path(plan.source_path).name, "", plan.reason])
            branch.setFont(0, self._heading_font())
            branch.setForeground(2, self._status_brush(plan.needs_compile))
            self._add_tree_property(branch, "Source", plan.source_path)
            self._add_build_inputs(branch, plan)
            self._add_tree_property(branch, "Output", plan.output_path,
                                    "present" if plan.output_path.exists() else "missing",
                                    valid=plan.output_path.exists())
            self._add_tree_property(branch, "Metadata", plan.metadata_path,
                                    "present" if plan.metadata_path.exists() else "missing",
                                    valid=plan.metadata_path.exists())
            self._add_tree_property(branch, "Status", plan.reason,
                                    "needs compile" if plan.needs_compile else "valid",
                                    valid=not plan.needs_compile)
            self._add_tree_property(branch, "Kernel ABI", getattr(plan, "kernel_abi_version", ""))
            self._add_tree_property(branch, "Include root", plan.include_root)
            self._add_tree_property(branch, "Kernel header", plan.kernel_header,
                                    "present" if Path(plan.kernel_header).exists() else "missing",
                                    valid=Path(plan.kernel_header).exists())
            self._add_tree_property(branch, "Source hash", plan.source_sha256,
                                    "present" if plan.source_sha256 else "missing",
                                    valid=bool(plan.source_sha256))
            output_hash_valid = plan.output_path.exists() and not plan.needs_compile
            self._add_tree_property(branch, "Header/output hashes", "see metadata",
                                    "current" if output_hash_valid else "needs validation",
                                    valid=output_hash_valid)
        root.setExpanded(True)
        for index in range(root.childCount()):
            root.child(index).setExpanded(True)
        self.compile_button.setEnabled(not self.simulation_running and self.status.needs_compile)
        self.clean_button.setEnabled(not self.simulation_running and bool(plans))
        self.details.setPlainText("\n".join(
            f"{plan.source_path}: {plan.reason}" for plan in plans
        ))

    def _add_build_inputs(self, parent, plan):
        source_root = Path(plan.source_root).resolve()
        source_path = Path(plan.source_path).resolve()
        input_paths = [Path(path) for path in plan.source_paths]
        input_paths.extend(Path(path) for path in plan.header_paths)
        input_paths = sorted({path.resolve() for path in input_paths}, key=lambda path: str(path).lower())

        inputs_branch = QTreeWidgetItem(parent, [f"Build inputs ({len(input_paths)} files)", "", ""])
        inputs_branch.setToolTip(0, "Source and header files discovered for this build target")
        inputs_branch.setExpanded(False)

        directories = {(): inputs_branch}
        for input_path in input_paths:
            try:
                relative_path = input_path.relative_to(source_root)
            except ValueError:
                relative_path = Path(input_path.name)

            parts = relative_path.parts
            directory_parts = parts[:-1]
            parent_item = inputs_branch
            for index in range(1, len(directory_parts) + 1):
                directory = directory_parts[:index]
                directory_item = directories.get(directory)
                if directory_item is None:
                    directory_item = QTreeWidgetItem(parent_item, [directory[-1], "", ""])
                    directories[directory] = directory_item
                parent_item = directory_item

            is_entry = input_path == source_path
            label = parts[-1] + (" [entry]" if is_entry else "")
            item = QTreeWidgetItem(parent_item, [label, "", "entry" if is_entry else ""])
            item.setData(0, Qt.UserRole, str(input_path))
            item.setToolTip(0, str(input_path))
            item.setToolTip(2, str(input_path))
            if is_entry:
                item.setForeground(0, self._status_brush(False))

    @staticmethod
    def _status_brush(needs_compile):
        return QBrush(QColor("#a94442" if needs_compile else "#26734d"))

    def _heading_font(self):
        font = QFont(self.tree.font())
        font.setBold(True)
        return font

    def _add_tree_property(self, parent, name, value, validation="", valid=None):
        item = QTreeWidgetItem(parent, [name, str(value), validation])
        value_text = str(value)
        value_editor = QLineEdit(value_text, self.tree)
        value_editor.setReadOnly(True)
        editor_font = self.tree.font()
        if editor_font.pointSize() > 1:
            editor_font.setPointSize(editor_font.pointSize() - 1)
        value_editor.setFont(editor_font)
        value_editor.setToolTip(value_text)
        value_editor.setClearButtonEnabled(False)
        value_editor.setFrame(False)
        self.tree.setItemWidget(item, 1, value_editor)
        item.setToolTip(2, str(item.text(2)))
        if valid is not None:
            color = QColor("#e8f8ef" if valid else "#fff0f0")
            item.setBackground(1, QBrush(color))
            item.setBackground(2, QBrush(color))
            item.setForeground(2, self._status_brush(not valid))
        return item

    def _show_tree_context_menu(self, position):
        item = self.tree.itemAt(position)
        if item is None:
            return
        column = self.tree.columnAt(position.x())
        value = item.text(column)
        if not value:
            return
        copy_value_text = item.data(column, Qt.UserRole) or value
        menu = QMenu(self.tree)
        copy_value = menu.addAction("Copy value")
        copy_row = menu.addAction("Copy row")
        action = menu.exec_(self.tree.viewport().mapToGlobal(position))
        if action == copy_value:
            QApplication.clipboard().setText(str(copy_value_text))
        elif action == copy_row:
            QApplication.clipboard().setText(" | ".join(item.text(i) for i in range(3)))

    def _compile(self, force):
        dialog = CompiledSteppableCompileDialog(str(self.project_path), force=force, parent=self)
        dialog.succeeded.connect(lambda _summary, text: self._compile_finished(text))
        dialog.failed.connect(lambda error, text: self._compile_failed(error, text))
        dialog.finished.connect(dialog.deleteLater)
        self._compile_dialog = dialog
        dialog.start()

    def _compile_finished(self, text):
        self.details.setPlainText(text)
        self.refresh_status()

    def _compile_failed(self, error, text):
        self.details.setPlainText(text)
        show_text_messagebox(
            title="Player Error",
            message="C++ steppable compilation failed.",
            informative_text="Compilation failed. See details for compiler output.",
            detailed_text=text or error,
            parent=self,
        )
        self.refresh_status()

    def clean_artifacts(self):
        if self.simulation_running:
            return
        for plan in self.status.plans:
            output = Path(plan.output_path)
            for path in (output, Path(plan.metadata_path), output.with_suffix(".obj"),
                         output.with_suffix(".exp"), output.with_suffix(".lib"),
                         output.with_suffix(".pdb")):
                try:
                    path.unlink(missing_ok=True)
                except OSError as error:
                    self.details.append(f"Could not remove {path}: {error}")
        self.refresh_status()

    def refresh_settings(self):
        self.settings = load_settings()
        self._display_settings()

    def _display_settings(self):
        if self.settings is None:
            return
        platform = self.settings["platforms"][current_platform_key()]
        detected = platform.get("detected") or {}
        preferred = platform.get("preferred") or {}
        self.compiler_label.setText(str(preferred or "automatic") + "\n" + str(platform.get("selection_policy")))
        self.detected_label.setText(str(detected or "No compiler detected"))

    def set_policy(self, policy):
        self.settings["platforms"][current_platform_key()]["selection_policy"] = policy
        self.refresh_settings()

    def reset_settings(self):
        platform = self.settings["platforms"][current_platform_key()]
        platform["selection_policy"] = "apple" if current_platform_key() == "macos" else "latest"
        for key in platform.get("preferred", {}):
            platform["preferred"][key] = "apple" if current_platform_key() == "macos" and key == "toolchain" else None
        self.refresh_settings()
        self.save_settings()

    def save_settings(self):
        save_settings(self.settings)
        self.refresh_settings()
