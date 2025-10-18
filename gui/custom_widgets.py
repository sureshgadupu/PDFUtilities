from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QHBoxLayout, QLineEdit, QListWidget, QPushButton, QWidget


class ToggleListWidget(QListWidget):
    def mousePressEvent(self, event):
        item = self.itemAt(event.pos())
        if item is not None:
            # Toggle selection: if already selected, deselect; otherwise select.
            # This overrides the default behavior which might require Ctrl for deselection
            # depending on the selection mode.
            current_selection_mode = self.selectionMode()
            if (
                current_selection_mode == QListWidget.SelectionMode.MultiSelection
                or current_selection_mode == QListWidget.SelectionMode.ExtendedSelection
            ):
                item.setSelected(not item.isSelected())
            else:  # SingleSelection or NoSelection
                super().mousePressEvent(event)  # Default behavior for other modes
        else:
            # If clicked outside an item, clear selection if in a multi-selection mode
            if self.selectionMode() != QListWidget.SelectionMode.SingleSelection:
                self.clearSelection()
            super().mousePressEvent(event)


class PasswordInputWidget(QWidget):
    """Custom widget for password input with toggle visibility button"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        
    def setup_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(2)
        
        # Password input field
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setPlaceholderText("Enter password...")
        self.password_input.setStyleSheet("""
            QLineEdit {
                background: #fff;
                color: #000;
                border: 1px solid #b2e0f7;
                border-radius: 4px;
                padding: 4px 8px;
                font-size: 12px;
            }
            QLineEdit:focus {
                border: 2px solid #00bfff;
            }
        """)
        
        # Toggle visibility button
        self.toggle_btn = QPushButton()
        self.toggle_btn.setFixedSize(24, 24)
        self.toggle_btn.setStyleSheet("""
            QPushButton {
                background: #b2e0f7;
                border: 1px solid #a2d4ec;
                border-radius: 4px;
                font-size: 12px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: #a2d4ec;
            }
            QPushButton:pressed {
                background: #92c8dc;
            }
        """)
        self.toggle_btn.setText("👁")
        self.toggle_btn.setToolTip("Show/Hide password")
        self.toggle_btn.clicked.connect(self.toggle_password_visibility)
        
        layout.addWidget(self.password_input)
        layout.addWidget(self.toggle_btn)
        
    def toggle_password_visibility(self):
        """Toggle between showing and hiding the password"""
        if self.password_input.echoMode() == QLineEdit.EchoMode.Password:
            self.password_input.setEchoMode(QLineEdit.EchoMode.Normal)
            self.toggle_btn.setText("🙈")
            self.toggle_btn.setToolTip("Hide password")
        else:
            self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
            self.toggle_btn.setText("👁")
            self.toggle_btn.setToolTip("Show password")
    
    def get_password(self):
        """Get the current password text"""
        return self.password_input.text()
    
    def set_password(self, password):
        """Set the password text"""
        self.password_input.setText(password)
    
    def clear_password(self):
        """Clear the password field"""
        self.password_input.clear()
