import pathlib
import hashlib
import sys
import traceback

from PySide6.QtCore import QTimer, QThread, QObject, Signal
from PySide6.QtGui import QFont, Qt
from PySide6.QtWidgets import (
    QWizardPage,
    QFileDialog,
    QLineEdit,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QHBoxLayout,
    QMessageBox,
    QRadioButton,
    QProgressBar,
    QTextEdit,
    QWizard,
)

from modules.widgets import ConsoleOutput
from setup.enums import Languages
from setup.newsRenderer import NewsRenderer
from setup.patch import patch_dokodemo

rom = b""
language = Languages.English


class DokodemoSelectFile(QWizardPage):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.valid_rom = False

        self.setTitle(self.tr("Step 1: Wii Room Anywhere"))
        self.setSubTitle(self.tr("Select 'Dokodemo Wii no Ma' ROM."))

        label = QLabel(
            self.tr(
                "To get Wii Room Anywhere, you need to provide your own ROM for Revision 1 of 'Dokodemo Wii no Ma'."
            )
        )
        label.setWordWrap(True)

        self.path = QLineEdit()
        self.path.setReadOnly(True)
        self.path.setPlaceholderText(self.tr("Select your ROM..."))

        self.select = QPushButton(self.tr("Browse..."))
        self.select.pressed.connect(self.select_dokodemo_rom)

        sublayout = QHBoxLayout()
        sublayout.addWidget(self.path)
        sublayout.addWidget(self.select)

        layout = QVBoxLayout()
        layout.addWidget(label)
        layout.addLayout(sublayout)

        self.setLayout(layout)

    def select_dokodemo_rom(self):
        dokodemo = QFileDialog(self).getOpenFileName(
            self,
            self.tr("Select 'Dokodemo Wii no Ma' ROM"),
            "~",
            self.tr("Nintendo DS ROMs (*.nds)"),
        )
        self.path.setText(dokodemo[0])
        self.validate_rom()

    def validate_rom(self):
        global rom

        self.valid_rom = False
        rom = pathlib.Path(self.path.text()).read_bytes()
        rom_hash = hashlib.sha512(rom).hexdigest()

        dokodemo_hash = "86441ecaf2337039173beee9ede34b557df18e2e1d180c02bde20dac633de1ca244acca34468a93fc4208d8ad64c14727def41e48ba50766ed1eba657a8d3adb"
        if rom_hash == dokodemo_hash:
            self.valid_rom = True
        else:
            QMessageBox.warning(
                self,
                self.tr("Invalid ROM"),
                self.tr(
                    """The ROM you provided is not a valid 'Dokodemo Wii no Ma' ROM!
            
Ensure the ROM you selected is of Revision 1 of 'Dokodemo Wii no Ma'."""
                ),
            )

        self.completeChanged.emit()

    def isComplete(self):
        return self.valid_rom


class DokodemoSelectLanguage(QWizardPage):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.language = Languages.English

        self.setTitle(self.tr("Step 2: Wii Room Anywhere"))
        self.setSubTitle(self.tr("Choose the language for Wii Room Anywhere."))

        label = QLabel(
            self.tr("What language would you like <b>Wii Room Anywhere</b> to be in?")
        )

        self.languages = {
            Languages.English: QRadioButton(self.tr("English")),
            Languages.Japan: QRadioButton(self.tr("Japanese")),
        }

        layout = QVBoxLayout()

        layout.addWidget(label)
        for button in self.languages.values():
            layout.addWidget(button)

        # Select the first option
        next(iter(self.languages.values())).setChecked(True)

        self.setLayout(layout)

    def validatePage(self):
        global rom
        global language

        for button_language, button in self.languages.items():
            if button.isChecked():
                language = button_language

        return True


class DokodemoPatchingPage(QWizardPage):
    patching_complete = False
    percentage: int
    status: str

    def __init__(self, parent=None):
        global language
        super().__init__(parent)

        self.setTitle(self.tr("Patching in progress"))
        self.setSubTitle(self.tr("Please wait while the patcher works its magic!"))

        self.label = QLabel(self.tr(f"Patching Wii Room Anywhere ({language.name})..."))
        self.label.setWordWrap(True)
        self.progress_bar = QProgressBar(self)

        self.news_box = NewsRenderer.createNewsBox(self)

        layout = QVBoxLayout()
        layout.addWidget(self.label)
        layout.addWidget(self.progress_bar)
        layout.addSpacing(10)
        layout.addWidget(self.news_box)

        self.console = QTextEdit()
        self.console.setReadOnly(True)
        self.console.setHidden(True)
        self.console.setObjectName("console")

        layout.addWidget(self.console)

        self.toggle_console_label = QLabel(self.tr("Show Details"))

        font = QFont()
        font.setUnderline(True)
        self.toggle_console_label.setFont(font)
        self.toggle_console_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.toggle_console_label.setStyleSheet("color: #606060;")
        self.toggle_console_label.setCursor(Qt.CursorShape.PointingHandCursor)

        self.toggle_console_label.mousePressEvent = self.toggle_console

        layout.addWidget(self.toggle_console_label)

        self.setLayout(layout)

        QTimer.singleShot(0, lambda: NewsRenderer.getNews(self, self.news_box))

        # Start thread to perform patching
        self.logic_thread = QThread()
        self.logic_worker = DokodemoPatchingWorker()

    def initializePage(self):
        global rom
        QTimer.singleShot(0, self.disable_back_button)

        # Redirect outputs to the console
        sys.stdout = ConsoleOutput(self.console, sys.__stdout__)
        sys.stderr = ConsoleOutput(self.console, sys.__stderr__)

        # Setup variables
        self.logic_worker.rom = rom
        self.logic_worker.language = language

        self.logic_worker.moveToThread(self.logic_thread)
        self.logic_thread.started.connect(self.logic_worker.patching_functions)

        self.logic_worker.broadcast_percentage.connect(self.set_percentage)
        self.logic_worker.broadcast_status.connect(self.set_status)
        self.logic_worker.error.connect(self.handle_error)

        self.logic_worker.finished.connect(self.logic_finished)
        self.logic_worker.finished.connect(self.logic_thread.quit)
        self.logic_thread.finished.connect(self.logic_worker.deleteLater)
        self.logic_thread.finished.connect(self.logic_thread.deleteLater)

        self.logic_thread.start()

    def isComplete(self):
        return self.patching_complete

    def disable_back_button(self):
        self.wizard().button(QWizard.WizardButton.BackButton).setEnabled(False)

    def logic_finished(self):
        self.patching_complete = True

        # Remove output redirects
        sys.stdout = sys.__stdout__
        sys.stderr = sys.__stderr__

        self.completeChanged.emit()
        QTimer.singleShot(0, self.wizard().next)

    def nextId(self):
        return 1000

    def set_percentage(self, percentage: int):
        """Sets percentage in variable then runs separate function to update progress bar,
        so a QTimer can be used to allow the UI to refresh"""
        self.percentage = percentage
        QTimer.singleShot(0, self.update_percentage)

    def update_percentage(self):
        """Updates percentage in progress bar"""
        self.progress_bar.setValue(self.percentage)

    def set_status(self, status: str):
        """Sets status in variable then runs separate function to update the label,
        so a QTimer can be used to allow the UI to refresh"""
        self.status = status
        QTimer.singleShot(0, self.update_status)

    def update_status(self):
        """Updates status above progress bar"""
        self.label.setText(self.status)

    def handle_error(self, error):
        """Display errors thrown from the patching logic to the user"""
        error = error.replace("\n", "<br>")

        QMessageBox.warning(
            self,
            "WiiLink Patcher - Warning",
            f"An exception was encountered while patching.<br><br>{error}<br>Please report this issue in the WiiLink Discord Server (<a href='https://discord.gg/wiilink'>discord.gg/wiilink</a>).",
        )

    def toggle_console(self, event=None):
        is_visible = self.console.isVisible()
        self.console.setHidden(is_visible)
        self.news_box.setHidden(not is_visible)

        # Change the label text based on the current state
        if is_visible:
            self.toggle_console_label.setText(self.tr("Show Details"))
        else:
            self.toggle_console_label.setText(self.tr("Hide Details"))


class DokodemoPatchingWorker(QObject):
    rom: bytes
    language: Languages

    is_patching_complete: bool
    finished = Signal(bool)
    broadcast_percentage = Signal(int)
    broadcast_status = Signal(str)
    error = Signal(str)

    def patching_functions(self):
        try:
            patch_dokodemo(self.language, self.rom)
        except:
            exception_traceback = traceback.format_exc()
            print(exception_traceback)
            self.error.emit(f"{exception_traceback}")

        self.broadcast_percentage.emit(100)
        self.finished.emit(True)
