from PyQt6.QtWidgets import QListWidget, QListWidgetItem


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
