from PySide6.QtWidgets import QWidget, QToolButton, QFrame, QVBoxLayout, QLabel
from PySide6.QtCore import Qt, Signal


class CollapsibleBox(QWidget):
    def __init__(self, title: str, parent=None):
        super().__init__(parent)

        self.toggle_button = QToolButton(text=title, checkable=True)

        self.toggle_button.setToolButtonStyle(
            Qt.ToolButtonStyle.ToolButtonTextBesideIcon
        )
        self.toggle_button.setArrowType(Qt.ArrowType.RightArrow)
        self.toggle_button.clicked.connect(self.on_toggle)

        self.content_area = QFrame()
        self.toggle_button.setProperty("collapsible", True)

        self.content_layout = QVBoxLayout()
        self.content_area.setLayout(self.content_layout)
        self.content_area.setVisible(False)

        main_layout = QVBoxLayout()
        main_layout.addWidget(self.toggle_button)
        main_layout.addWidget(self.content_area)
        self.setLayout(main_layout)

    def on_toggle(self):
        checked = self.toggle_button.isChecked()
        if checked:
            self.toggle_button.setArrowType(Qt.ArrowType.DownArrow)
        else:
            self.toggle_button.setArrowType(Qt.ArrowType.RightArrow)

        self.content_area.setVisible(checked)


class ClickableLabel(QLabel):
    clicked = Signal()

    def __init__(self, text="", parent=None):
        super().__init__(text, parent)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit()
