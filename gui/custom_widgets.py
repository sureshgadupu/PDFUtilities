from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import (
    QHBoxLayout, QLineEdit, QListWidget, QPushButton, QWidget,
    QMenu, QDialog, QVBoxLayout, QLabel, QDialogButtonBox,
    QMessageBox, QFormLayout, QTableWidget, QTableWidgetItem,
    QHeaderView, QAbstractItemView
)


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
    """Custom widget for password input with toggle visibility and saved passwords"""
    
    def __init__(self, parent=None, password_manager=None):
        super().__init__(parent)
        self.password_manager = password_manager
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
        
        # Dropdown button for saved passwords (only if password manager is available)
        if self.password_manager:
            self.dropdown_btn = QPushButton()
            self.dropdown_btn.setFixedSize(24, 24)
            self.dropdown_btn.setText("▼")
            self.dropdown_btn.setToolTip("Select from saved passwords")
            self.dropdown_btn.setStyleSheet("""
                QPushButton {
                    background: #b2e0f7;
                    border: 1px solid #a2d4ec;
                    border-radius: 4px;
                    font-size: 10px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background: #a2d4ec;
                }
                QPushButton:pressed {
                    background: #92c8dc;
                }
            """)
            self.dropdown_btn.clicked.connect(self.show_password_menu)
        
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
        
        # Save password button (only if password manager is available)
        if self.password_manager:
            self.save_btn = QPushButton()
            self.save_btn.setFixedSize(24, 24)
            self.save_btn.setText("💾")
            self.save_btn.setToolTip("Save this password")
            self.save_btn.setStyleSheet("""
                QPushButton {
                    background: #d4edda;
                    border: 1px solid #c3e6cb;
                    border-radius: 4px;
                    font-size: 12px;
                }
                QPushButton:hover {
                    background: #c3e6cb;
                }
                QPushButton:pressed {
                    background: #b1dfbb;
                }
            """)
            self.save_btn.clicked.connect(self.save_current_password)
        
        layout.addWidget(self.password_input)
        if self.password_manager:
            layout.addWidget(self.dropdown_btn)
        layout.addWidget(self.toggle_btn)
        if self.password_manager:
            layout.addWidget(self.save_btn)
    
    def show_password_menu(self):
        """Show menu with saved passwords"""
        if not self.password_manager:
            return
        
        menu = QMenu(self)
        menu.setStyleSheet("""
            QMenu {
                background: #ffffff;
                color: #000000;
                border: 1px solid #b2e0f7;
                font-size: 13px;
            }
            QMenu::item {
                padding: 6px 12px;
            }
            QMenu::item:selected {
                background: #b7d6fb;
            }
            QMenu::separator {
                background: #b2e0f7;
                height: 1px;
                margin: 4px 8px;
            }
        """)
        
        passwords = self.password_manager.get_all_passwords()
        
        if passwords:
            for name, pwd in sorted(passwords.items()):
                action = menu.addAction(f"🔑 {name}")
                action.setData(pwd)
                action.triggered.connect(lambda checked, p=pwd: self.set_password(p))
            
            menu.addSeparator()
        
        # Add manage passwords option
        manage_action = menu.addAction("⚙️ Manage Passwords...")
        manage_action.triggered.connect(self.show_password_manager)
        
        if not passwords:
            menu.insertAction(manage_action, menu.addAction("No saved passwords"))
            menu.actions()[0].setEnabled(False)
            menu.insertSeparator(manage_action)
        
        menu.exec(self.dropdown_btn.mapToGlobal(self.dropdown_btn.rect().bottomLeft()))
    
    def save_current_password(self):
        """Save the current password to the manager"""
        if not self.password_manager:
            return
        
        password = self.password_input.text()
        if not password:
            QMessageBox.warning(self, "No Password", "Please enter a password first.")
            return
        
        dialog = SavePasswordDialog(self, self.password_manager, password)
        dialog.exec()
    
    def show_password_manager(self):
        """Show dialog to manage saved passwords"""
        if not self.password_manager:
            return
        
        dialog = PasswordManagerDialog(self, self.password_manager)
        dialog.exec()
        
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


class SavePasswordDialog(QDialog):
    """Dialog for saving a password with a name"""
    
    def __init__(self, parent, password_manager, password):
        super().__init__(parent)
        self.password_manager = password_manager
        self.password = password
        self.setWindowTitle("Save Password")
        self.setModal(True)
        self.resize(400, 150)
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Info label
        info = QLabel("Enter a name for this password:")
        info.setStyleSheet("font-size: 13px; color: #000;")
        layout.addWidget(info)
        
        # Form layout
        form = QFormLayout()
        
        # Name label with black color
        name_label = QLabel("Name:")
        name_label.setStyleSheet("color: #000; font-size: 13px;")
        
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("e.g., Work Documents, Client PDFs")
        self.name_input.setStyleSheet("""
            QLineEdit {
                background: #fff;
                color: #000;
                border: 1px solid #b2e0f7;
                border-radius: 4px;
                padding: 6px 8px;
                font-size: 13px;
            }
            QLineEdit:focus {
                border: 2px solid #00bfff;
            }
        """)
        
        form.addRow(name_label, self.name_input)
        layout.addLayout(form)
        
        # Warning label
        warning = QLabel("⚠️ Passwords are stored in plain text on your computer.")
        warning.setStyleSheet("""
            color: #856404; 
            background: #fff3cd; 
            padding: 8px; 
            border-radius: 4px;
            font-size: 11px;
        """)
        layout.addWidget(warning)
        
        # Dialog buttons
        dialog_btns = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save | 
            QDialogButtonBox.StandardButton.Cancel
        )
        dialog_btns.accepted.connect(self.save_password)
        dialog_btns.rejected.connect(self.reject)
        dialog_btns.setStyleSheet("""
            QPushButton {
                background: #b2e0f7;
                color: black;
                border: 1px solid #a2d4ec;
                border-radius: 4px;
                padding: 6px 16px;
                font-size: 13px;
            }
            QPushButton:hover {
                background: #a2d4ec;
            }
        """)
        layout.addWidget(dialog_btns)
    
    def save_password(self):
        """Save the password with the entered name"""
        name = self.name_input.text().strip()
        if not name:
            QMessageBox.warning(self, "Invalid Name", "Please enter a name for the password.")
            return
        
        if self.password_manager.add_password(name, self.password):
            msg = QMessageBox(self)
            msg.setIcon(QMessageBox.Icon.Information)
            msg.setWindowTitle("Success")
            msg.setText(f"Password '{name}' saved successfully!")
            msg.setStyleSheet("QLabel { color: #000; } QPushButton { background: #b2e0f7; color: #000; border: 1px solid #a2d4ec; border-radius: 4px; padding: 6px 16px; }")
            msg.exec()
            self.accept()
        else:
            msg = QMessageBox(self)
            msg.setIcon(QMessageBox.Icon.Question)
            msg.setWindowTitle("Name Exists")
            msg.setText(f"A password named '{name}' already exists. Do you want to replace it?")
            msg.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            msg.setStyleSheet("QLabel { color: #000; } QPushButton { background: #b2e0f7; color: #000; border: 1px solid #a2d4ec; border-radius: 4px; padding: 6px 16px; }")
            reply = msg.exec()
            if reply == QMessageBox.StandardButton.Yes:
                self.password_manager.update_password(name, name, self.password)
                msg = QMessageBox(self)
                msg.setIcon(QMessageBox.Icon.Information)
                msg.setWindowTitle("Success")
                msg.setText(f"Password '{name}' updated successfully!")
                msg.setStyleSheet("QLabel { color: #000; } QPushButton { background: #b2e0f7; color: #000; border: 1px solid #a2d4ec; border-radius: 4px; padding: 6px 16px; }")
                msg.exec()
                self.accept()


class PasswordManagerDialog(QDialog):
    """Dialog for managing saved passwords"""
    
    def __init__(self, parent, password_manager):
        super().__init__(parent)
        self.password_manager = password_manager
        self.setWindowTitle("Manage Saved Passwords")
        self.setModal(True)
        self.resize(550, 400)
        self.setup_ui()
        self.load_passwords()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Warning label
        warning = QLabel("⚠️ Passwords are stored in plain text. Use at your own risk.")
        warning.setStyleSheet("""
            color: #856404; 
            background: #fff3cd; 
            padding: 8px; 
            border-radius: 4px;
            font-size: 12px;
        """)
        layout.addWidget(warning)
        
        # Table of passwords
        self.password_table = QTableWidget()
        self.password_table.setColumnCount(2)
        self.password_table.setHorizontalHeaderLabels(["Name", "Password"])
        self.password_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.password_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.password_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.password_table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.password_table.setStyleSheet("""
            QTableWidget {
                background: #ffffff;
                border: 1px solid #b2e0f7;
                border-radius: 4px;
                font-size: 13px;
            }
            QTableWidget::item:selected {
                background: #b7d6fb;
            }
            QHeaderView::section {
                background-color: #b2e0f7;
                color: #000;
                font-weight: bold;
                border: 1px solid #a2d4ec;
                padding: 6px;
                font-size: 13px;
            }
        """)
        layout.addWidget(self.password_table)
        
        # Buttons
        btn_layout = QHBoxLayout()
        
        self.add_btn = QPushButton("Add New")
        self.add_btn.clicked.connect(self.add_new_password)
        self.add_btn.setStyleSheet("""
            QPushButton {
                background: #d4edda;
                color: #155724;
                border: 1px solid #c3e6cb;
                border-radius: 4px;
                padding: 6px 12px;
                font-size: 13px;
            }
            QPushButton:hover {
                background: #c3e6cb;
            }
        """)
        
        self.edit_btn = QPushButton("Edit Selected")
        self.edit_btn.clicked.connect(self.edit_selected)
        self.edit_btn.setStyleSheet("""
            QPushButton {
                background: #d1ecf1;
                color: #0c5460;
                border: 1px solid #bee5eb;
                border-radius: 4px;
                padding: 6px 12px;
                font-size: 13px;
            }
            QPushButton:hover {
                background: #bee5eb;
            }
        """)
        
        self.remove_btn = QPushButton("Remove Selected")
        self.remove_btn.clicked.connect(self.remove_selected)
        self.remove_btn.setStyleSheet("""
            QPushButton {
                background: #f8d7da;
                color: #721c24;
                border: 1px solid #f5c6cb;
                border-radius: 4px;
                padding: 6px 12px;
                font-size: 13px;
            }
            QPushButton:hover {
                background: #f1b0b7;
            }
        """)
        
        self.clear_btn = QPushButton("Clear All")
        self.clear_btn.clicked.connect(self.clear_all)
        self.clear_btn.setStyleSheet("""
            QPushButton {
                background: #f8d7da;
                color: #721c24;
                border: 1px solid #f5c6cb;
                border-radius: 4px;
                padding: 6px 12px;
                font-size: 13px;
            }
            QPushButton:hover {
                background: #f1b0b7;
            }
        """)
        
        btn_layout.addWidget(self.add_btn)
        btn_layout.addWidget(self.edit_btn)
        btn_layout.addWidget(self.remove_btn)
        btn_layout.addWidget(self.clear_btn)
        btn_layout.addStretch()
        
        layout.addLayout(btn_layout)
        
        # Dialog buttons
        dialog_btns = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
        dialog_btns.rejected.connect(self.accept)
        dialog_btns.setStyleSheet("""
            QPushButton {
                background: #b2e0f7;
                color: black;
                border: 1px solid #a2d4ec;
                border-radius: 4px;
                padding: 6px 16px;
                font-size: 13px;
            }
            QPushButton:hover {
                background: #a2d4ec;
            }
        """)
        layout.addWidget(dialog_btns)
    
    def load_passwords(self):
        """Load passwords into the table"""
        self.password_table.setRowCount(0)
        passwords = self.password_manager.get_all_passwords()
        
        for name, password in sorted(passwords.items()):
            row = self.password_table.rowCount()
            self.password_table.insertRow(row)
            
            name_item = QTableWidgetItem(name)
            password_item = QTableWidgetItem(password)
            
            self.password_table.setItem(row, 0, name_item)
            self.password_table.setItem(row, 1, password_item)
    
    def add_new_password(self):
        """Add a new password"""
        dialog = EditPasswordDialog(self, self.password_manager, None, None)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.load_passwords()
    
    def edit_selected(self):
        """Edit selected password"""
        current_row = self.password_table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "No Selection", "Please select a password to edit.")
            return
        
        name = self.password_table.item(current_row, 0).text()
        password = self.password_table.item(current_row, 1).text()
        
        dialog = EditPasswordDialog(self, self.password_manager, name, password)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.load_passwords()
    
    def remove_selected(self):
        """Remove selected password"""
        current_row = self.password_table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "No Selection", "Please select a password to remove.")
            return
        
        name = self.password_table.item(current_row, 0).text()
        
        reply = QMessageBox.question(
            self, 
            "Confirm Remove", 
            f"Remove password '{name}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            self.password_manager.remove_password(name)
            self.load_passwords()
    
    def clear_all(self):
        """Clear all passwords"""
        reply = QMessageBox.question(
            self,
            "Confirm Clear All",
            "Are you sure you want to remove all saved passwords?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            self.password_manager.clear_all()
            self.load_passwords()


class EditPasswordDialog(QDialog):
    """Dialog for editing or adding a password"""
    
    def __init__(self, parent, password_manager, name=None, password=None):
        super().__init__(parent)
        self.password_manager = password_manager
        self.original_name = name
        self.is_edit = name is not None
        
        self.setWindowTitle("Edit Password" if self.is_edit else "Add Password")
        self.setModal(True)
        self.resize(450, 180)
        self.setup_ui(name, password)
    
    def setup_ui(self, name, password):
        layout = QVBoxLayout(self)
        
        # Form layout
        form = QFormLayout()
        
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("e.g., Work Documents, Client PDFs")
        if name:
            self.name_input.setText(name)
        self.name_input.setStyleSheet("""
            QLineEdit {
                background: #fff;
                color: #000;
                border: 1px solid #b2e0f7;
                border-radius: 4px;
                padding: 6px 8px;
                font-size: 13px;
            }
            QLineEdit:focus {
                border: 2px solid #00bfff;
            }
        """)
        
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Enter password")
        if password:
            self.password_input.setText(password)
        self.password_input.setStyleSheet("""
            QLineEdit {
                background: #fff;
                color: #000;
                border: 1px solid #b2e0f7;
                border-radius: 4px;
                padding: 6px 8px;
                font-size: 13px;
            }
            QLineEdit:focus {
                border: 2px solid #00bfff;
            }
        """)
        
        form.addRow("Name:", self.name_input)
        form.addRow("Password:", self.password_input)
        layout.addLayout(form)
        
        # Warning label
        warning = QLabel("⚠️ Passwords are stored in plain text on your computer.")
        warning.setStyleSheet("""
            color: #856404; 
            background: #fff3cd; 
            padding: 8px; 
            border-radius: 4px;
            font-size: 11px;
        """)
        layout.addWidget(warning)
        
        # Dialog buttons
        dialog_btns = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save | 
            QDialogButtonBox.StandardButton.Cancel
        )
        dialog_btns.accepted.connect(self.save_password)
        dialog_btns.rejected.connect(self.reject)
        dialog_btns.setStyleSheet("""
            QPushButton {
                background: #b2e0f7;
                color: black;
                border: 1px solid #a2d4ec;
                border-radius: 4px;
                padding: 6px 16px;
                font-size: 13px;
            }
            QPushButton:hover {
                background: #a2d4ec;
            }
        """)
        layout.addWidget(dialog_btns)
    
    def save_password(self):
        """Save the password"""
        name = self.name_input.text().strip()
        password = self.password_input.text()
        
        if not name:
            QMessageBox.warning(self, "Invalid Name", "Please enter a name for the password.")
            return
        
        if not password:
            QMessageBox.warning(self, "Invalid Password", "Please enter a password.")
            return
        
        if self.is_edit:
            # Update existing password
            self.password_manager.update_password(self.original_name, name, password)
            self.accept()
        else:
            # Add new password
            if self.password_manager.add_password(name, password):
                self.accept()
            else:
                msg = QMessageBox(self)
                msg.setIcon(QMessageBox.Icon.Question)
                msg.setWindowTitle("Name Exists")
                msg.setText(f"A password named '{name}' already exists. Do you want to replace it?")
                msg.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
                msg.setStyleSheet("QLabel { color: #000; } QPushButton { background: #b2e0f7; color: #000; border: 1px solid #a2d4ec; border-radius: 4px; padding: 6px 16px; }")
                reply = msg.exec()
                if reply == QMessageBox.StandardButton.Yes:
                    self.password_manager.update_password(name, name, password)
                    self.accept()
