from PyQt6.QtCore import QEasingCurve, QPropertyAnimation, QRect, QTimer, Qt
from PyQt6.QtWidgets import QFrame, QGraphicsOpacityEffect, QHBoxLayout, QLabel, QWidget


class NotificationWidget(QFrame):
    """A toast-like notification widget that fades in and out."""

    def __init__(self, parent: QWidget):
        super().__init__(parent)
        self.parent = parent
        self.setFrameShape(QFrame.Shape.StyledPanel)
        self.setObjectName("notificationFrame")
        self.setMinimumWidth(250)
        self.setMaximumWidth(400)

        # Layout
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(15, 10, 15, 10)
        self.message_label = QLabel()
        self.message_label.setObjectName("notificationLabel")
        self.message_label.setWordWrap(True)
        self.layout.addWidget(self.message_label)

        # Opacity effect for fading
        self.opacity_effect = QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(self.opacity_effect)

        # Animation setup
        self.animation = QPropertyAnimation(self.opacity_effect, b"opacity")
        self.animation.setDuration(300)
        self.animation.setEasingCurve(QEasingCurve.Type.InOutQuad)
        self.animation.finished.connect(self._on_animation_finished)

        # Timer for hiding the notification
        self.hide_timer = QTimer(self)
        self.hide_timer.setSingleShot(True)
        self.hide_timer.timeout.connect(self.fade_out)

        self.hiding = False
        self.hide()

    def show_message(self, message: str, level: str = "info", duration: int = 6000):
        """
        Show the notification with a message.
        Levels: 'info', 'success', 'error'.
        """
        self.message_label.setText(message)

        # Stop any ongoing animations or timers
        self.animation.stop()
        self.hide_timer.stop()
        self.hiding = False

        # Base stylesheet
        base_stylesheet = """
            #notificationFrame {{
                border-radius: 8px;
                border: 1px solid {border_color};
                background-color: {bg_color};
            }}
            #notificationLabel {{
                color: {text_color};
                background-color: transparent;
            }}
        """

        # Set style based on level
        if level == "success":
            style = base_stylesheet.format(
                bg_color="#d4edda", border_color="#c3e6cb", text_color="#155724"
            )
        elif level == "error":
            style = base_stylesheet.format(
                bg_color="#f8d7da", border_color="#f5c6cb", text_color="#721c24"
            )
        else:  # 'info'
            style = base_stylesheet.format(
                bg_color="#d1ecf1", border_color="#bee5eb", text_color="#0c5460"
            )
        self.setStyleSheet(style)

        # Adjust size and position
        self.adjustSize()
        self._reposition()
        self.fade_in()

        # Set timer to hide
        self.hide_timer.start(duration)

    def _reposition(self):
        """Move notification to the center of the parent."""
        parent_rect = self.parent.rect()
        self.move(
            (parent_rect.width() - self.width()) // 2,
            (parent_rect.height() - self.height()) // 2,
        )

    def fade_in(self):
        self.hiding = False
        self.show()
        self.animation.setStartValue(0.0)
        self.animation.setEndValue(1.0)
        self.animation.start()

    def fade_out(self):
        self.hiding = True
        self.animation.setStartValue(1.0)
        self.animation.setEndValue(0.0)
        self.animation.start()

    def _on_animation_finished(self):
        """Called when any animation finishes."""
        if self.hiding:
            self.hide()
            self.hiding = False

    def resizeEvent(self, event):
        """Handle parent resize events to stay centered."""
        super().resizeEvent(event)
        if self.isVisible():
            self._reposition() 