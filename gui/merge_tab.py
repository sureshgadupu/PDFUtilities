from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QProgressBar, QListWidget, QListWidgetItem,
    QHBoxLayout, QFileDialog, QMessageBox, QGroupBox, QMenu
)
from PyQt6.QtCore import Qt, QStandardPaths, QMimeData
from PyQt6.QtGui import QFont, QAction, QDrag
from workers import MergeWorker
import os

class DragDropListWidget(QListWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setDragDropMode(QListWidget.DragDropMode.InternalMove)
        self.setDefaultDropAction(Qt.DropAction.MoveAction)
        self.setAcceptDrops(True)

    def startDrag(self, supportedActions):
        if not self.currentItem():
            return

        drag = QDrag(self)
        mimeData = QMimeData()
        mimeData.setText(self.currentItem().text())
        drag.setMimeData(mimeData)
        drag.exec(Qt.DropAction.MoveAction)

    def dragEnterEvent(self, event):
        if event.mimeData().hasText():
            event.acceptProposedAction()

    def dragMoveEvent(self, event):
        if event.mimeData().hasText():
            event.acceptProposedAction()

    def dropEvent(self, event):
        if event.mimeData().hasText():
            source = self.currentRow()
            target = self.row(self.itemAt(event.position().toPoint()))
            
            if source < target:
                target += 1
            
            item = self.takeItem(source)
            self.insertItem(target, item)
            self.setCurrentItem(item)
            event.acceptProposedAction()

class MergeTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.worker = None
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)

        # Title
        title_label = QLabel("PDF Merge")
        title_label.setFont(QFont('Arial', 20, QFont.Weight.Bold))
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("""
            color: #000000;
            background-color: #f0f0f0;
            padding: 22px 0 16px 0;
            border-bottom: 1.5px solid #cccccc;
            border-radius: 8px 8px 0 0;
        """)
        layout.addWidget(title_label)

        # File list
        self.file_list = DragDropListWidget()
        self.file_list.setSelectionMode(QListWidget.SelectionMode.ExtendedSelection)
        self.file_list.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.file_list.customContextMenuRequested.connect(self._show_context_menu)
        self.file_list.setStyleSheet("""
            QListWidget {
                background-color: #ffffff;
                color: #222222;
                border: 1.5px solid #a0a0a0;
                border-radius: 4px;
                padding: 8px;
                font-size: 15px;
            }
            QListWidget::item {
                padding: 6px 2px;
            }
            QListWidget::item:selected {
                background: #b7d6fb;
                color: #222222;
            }
        """)
        layout.addWidget(self.file_list)

        # File selection buttons
        button_layout = QHBoxLayout()
        self.select_button = QPushButton("Select PDF Files")
        self.select_button.clicked.connect(self._select_files)
        self.select_button.setStyleSheet("color: white;")
        button_layout.addWidget(self.select_button)

        self.remove_button = QPushButton("Remove Selected")
        self.remove_button.clicked.connect(self._remove_selected_files)
        self.remove_button.setStyleSheet("color: white;")
        self.remove_button.setEnabled(False)
        button_layout.addWidget(self.remove_button)
        layout.addLayout(button_layout)

        # Merge button
        self.merge_button = QPushButton("Merge PDFs")
        self.merge_button.clicked.connect(self._start_merge)
        self.merge_button.setEnabled(False)
        self.merge_button.setStyleSheet("color: white;")
        layout.addWidget(self.merge_button)

        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)

        # Status label
        self.status_label = QLabel("Select at least 2 PDF files to begin.")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setStyleSheet("color: white;")
        layout.addWidget(self.status_label)

        self.setLayout(layout)
        self._apply_styles()

    def _apply_styles(self):
        self.setStyleSheet("""
            MergeTab {
                background-color: #f3f4f6;
            }
            QPushButton {
                background-color: #808080;
                color: #FFFFFF;
                border: 1px solid #606060;
                padding: 12px 20px;
                border-radius: 6px;
                font-size: 15px;
                font-weight: 500;
            }
            QPushButton:hover {
                background-color: #888888;
                color: #FFFFFF;
                border-color: #686868;
            }
            QPushButton:pressed {
                background-color: #707070;
                color: #FFFFFF;
                border-color: #686868;
            }
            QPushButton:disabled {
                background-color: #808080;
                color: #cccccc;
                border-color: #707070;
            }
            QProgressBar {
                border: 1px solid #b0b0b0;
                border-radius: 6px;
                text-align: center;
                background: #e0e0e0;
                font-size: 14px;
            }
            QProgressBar::chunk {
                background-color: #606060;
                border-radius: 5px;
            }
            QLabel {
                color: #000000;
            }
        """)

    def _update_merge_button_state(self):
        file_count = self.file_list.count()
        self.merge_button.setEnabled(file_count >= 2)
        self.remove_button.setEnabled(file_count > 0)
        if file_count == 0:
            self.status_label.setText("Select at least 2 PDF files to begin.")
        elif file_count == 1:
            self.status_label.setText("Select at least one more PDF file to merge.")
        else:
            self.status_label.setText(f"{file_count} file(s) selected. Ready to merge.")
        self.status_label.setStyleSheet("color: white;")

    def _show_context_menu(self, position):
        if self.file_list.count() > 0:
            menu = QMenu()
            remove_action = QAction("Remove Selected", self)
            remove_action.triggered.connect(self._remove_selected_files)
            menu.addAction(remove_action)
            menu.exec(self.file_list.mapToGlobal(position))

    def _remove_selected_files(self):
        selected_items = self.file_list.selectedItems()
        if not selected_items:
            return

        for item in selected_items:
            self.file_list.takeItem(self.file_list.row(item))

        self._update_merge_button_state()

    def _select_files(self):
        files, _ = QFileDialog.getOpenFileNames(
            self,
            "Select PDF Files",
            QStandardPaths.writableLocation(QStandardPaths.StandardLocation.DocumentsLocation),
            "PDF Files (*.pdf)"
        )
        if files:
            for f in files:
                item = QListWidgetItem(f)
                item.setToolTip(f)
                self.file_list.addItem(item)
            self._update_merge_button_state()

    def _start_merge(self):
        pdf_files = [self.file_list.item(i).text() for i in range(self.file_list.count())]
        if len(pdf_files) < 2:
            self.status_label.setText("At least 2 PDF files are required for merging.")
            self.status_label.setStyleSheet("color: orange;")
            return

        # Get output file name based on first file
        output_dir_name = "MergedPDFs_from_App"
        documents_path = QStandardPaths.writableLocation(QStandardPaths.StandardLocation.DocumentsLocation)
        output_directory = os.path.join(documents_path, output_dir_name)
        if not os.path.exists(output_directory):
            os.makedirs(output_directory)

        # Get the first file's name without extension
        first_file = os.path.basename(pdf_files[0])
        base_name = os.path.splitext(first_file)[0]
        output_file = os.path.join(output_directory, f"{base_name}_merged.pdf")

        # Handle duplicate files using Windows naming convention
        counter = 1
        while os.path.exists(output_file):
            output_file = os.path.join(output_directory, f"{base_name}_merged ({counter}).pdf")
            counter += 1

        # Start worker
        self.progress_bar.setValue(0)
        self.progress_bar.setVisible(True)
        self.status_label.setText("Starting merge...")
        self.status_label.setStyleSheet("color: white;")
        self.worker = MergeWorker(pdf_files, output_file, parent=self)
        self.worker.progress.connect(self._update_progress_bar)
        self.worker.status_update.connect(self._update_status_label)
        self.worker.finished.connect(self._handle_merge_finished)
        self.worker.error.connect(self._handle_merge_error)
        self.worker.start()
        self.merge_button.setEnabled(False)
        self.select_button.setEnabled(False)

    def _update_progress_bar(self, value):
        self.progress_bar.setValue(value)

    def _update_status_label(self, message):
        self.status_label.setText(message)
        if "Error" in message or "Failed" in message:
            self.status_label.setStyleSheet("color: red;")
        elif "Merged" in message or "Created output directory" in message:
            self.status_label.setStyleSheet("color: green;")
        else:
            self.status_label.setStyleSheet("color: white;")

    def _handle_merge_finished(self, success):
        self.progress_bar.setValue(100)
        if success:
            self.status_label.setText("PDF files merged successfully.")
            self.status_label.setStyleSheet("color: green;")
        else:
            self.status_label.setText("Merge process finished with errors.")
            self.status_label.setStyleSheet("color: red;")
        self.worker = None
        self.merge_button.setEnabled(True)
        self.select_button.setEnabled(True)

    def _handle_merge_error(self, error_message):
        self.status_label.setText(f"Critical Error: {error_message}")
        self.status_label.setStyleSheet("color: red;")
        self.progress_bar.setVisible(False)
        self.worker = None
        self.merge_button.setEnabled(True)
        self.select_button.setEnabled(True) 