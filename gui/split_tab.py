from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

class SplitTab(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        label = QLabel("Split PDF (Coming Soon)")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label.setFont(QFont('Arial', 16, QFont.Weight.Bold))
        layout.addWidget(label)
        self.setStyleSheet("background-color: #f0f0f0;") 