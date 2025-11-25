import random
import sys
import time

from PySide6.QtWidgets import (
    QWidget,
    QToolButton,
    QFrame,
    QVBoxLayout,
    QLabel,
    QTextEdit,
    QSizePolicy,
)
from PySide6.QtCore import Qt, Signal, QObject, QThread
from PySide6.QtGui import QTextCursor


class CollapsibleBox(QWidget):
    def __init__(self, title: str, parent=None):
        super().__init__(parent)

        self.toggle_button = QToolButton(text=f"  {title}", checkable=True)

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


class ConsoleOutput(QObject):
    new_text = Signal(str)

    def __init__(self, text_edit: QTextEdit, console: sys):
        super().__init__()
        self.text_edit = text_edit
        self.console = console

        # We use a signal here because it otherwise crashes when
        # the text comes from a QThread for some reason
        self.new_text.connect(self._append_text)

    def write(self, message):
        if self.console:
            self.console.write(message)

        self.new_text.emit(message)

    def flush(self):
        if self.console:
            self.console.flush()

    def _append_text(self, message):
        cursor = self.text_edit.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        cursor.insertText(message)
        self.text_edit.setTextCursor(cursor)


class FunFacts(QLabel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWordWrap(True)
        self.setStyleSheet(
            """
            background-color: #333333;
            color: white;
            border: 1px solid #555555;
            border-radius: 5px;
            padding: 10px;
            font-size: 12px;
        """
        )
        self.setTextFormat(Qt.TextFormat.RichText)
        self.setOpenExternalLinks(True)

        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        self.adjustSize()

        self.setAlignment(Qt.AlignmentFlag.AlignLeft)

        self.fact_thread = QThread()
        self.fact_worker = FactWorker()

        self.fact_worker.moveToThread(self.fact_thread)
        self.fact_thread.started.connect(self.fact_worker.update_facts)

        self.fact_worker.emit_fact.connect(self.set_fact)

        self.fact_thread.start()

    def set_fact(self, fact: str):
        self.setText(
            self.tr(
                """<h3>Did you know?</h3>
{}"""
            ).format(fact)
        )


class FactWorker(QObject):
    emit_fact = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.facts = [
            self.tr("The Wii was the best selling game-console of 2006!"),
            self.tr('The Wii was called "Revolution" during development!'),
            self.tr(
                "The music used in many of the Wii's channels (including the Wii Shop, Mii, Check Mii Out, and Forecast Channel) was composed by Kazumi Totaka."
            ),
            self.tr(
                "The Internet Channel was initially a paid channel for 500 Wii Points."
            ),
            self.tr("You can use candles instead of a Wii sensor bar."),
            self.tr(
                "The blinking blue light that indicates Wii Mail has been received is actually synced to the bird call of the Japanese bush warbler!"
            ),
            self.tr(
                "Wii Sports is the most sold Wii game released, at a staggering 82.9 million copies sold!"
            ),
            self.tr(
                "We have a forum you can check out at <a href='https://forum.wiilink.ca'>forum.wiilink.ca</a>!"
            ),
            self.tr(
                "Japanese regions in the Forecast Channel uses different weather icons to other regions!"
            ),
            self.tr(
                'The WiiLink project began in 2020 under the name "Rii no Ma", with the goal of reviving Wii no Ma and the other Japan-exclusive channels.'
            ),
            self.tr(
                "RiiConnect24, the first WiiConnect24 revival project, was established in 2015, releasing the first News Channel revival in 2016!"
            ),
            self.tr(
                "Before 2024, there were 2 separate services reviving WiiConnect24 channels - WiiLink and RiiConnect24. The two services were merged at the end of 2023."
            ),
            self.tr(
                "The globe used in the News and Forecast Channels is based on NASA imagery, and is also used in Mario Kart Wii."
            ),
            self.tr(
                "You can press the Reset button while the Wii is in standby mode to turn off the disc drive light indicating that you have a new message."
            ),
        ]

    def update_facts(self):
        while True:
            current_fact = random.choice(self.facts)
            self.emit_fact.emit(current_fact)
            time.sleep(10)
