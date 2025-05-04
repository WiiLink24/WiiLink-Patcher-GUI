from PySide6.QtCore import QTimer, QThread
from PySide6.QtWidgets import QWizardPage, QLabel, QVBoxLayout, QRadioButton, QButtonGroup, QProgressBar, \
    QWizard, QCheckBox, QMessageBox, QWidget

from .enums import *
from .patch import PatchingWorker

system_channel_restorer = False
selected_channels = []


class ExtrasSystemChannelRestorer(QWizardPage):
    local_selected_channels: list

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle(self.tr("Step 1: Extras Setup"))
        self.setSubTitle(self.tr("Decide if you'd like to download System Channel Restorer"))

        self.label = QLabel(self.tr("<b>Would you like to download System Channel Restorer?</b>"))
        self.explanation = QLabel(self.tr("""System Channel Restorer is a homebrew application that allows for installation of Photo Channel 1.1 and the Internet Channel.
Use of System Channel Restorer requires an internet connection on your console."""))
        self.explanation.setWordWrap(True)

        self.yes = QRadioButton(self.tr("Yes, download System Channel Restorer"))
        self.no = QRadioButton(self.tr("No, I'd prefer offline WADs"))

        # Layout
        self.layout = QVBoxLayout()

        self.layout.addWidget(self.label)
        self.layout.addWidget(self.explanation)

        self.layout.addWidget(self.yes)
        self.layout.addWidget(self.no)

        self.setLayout(self.layout)

        self.yes.clicked.connect(self.completeChanged)
        self.no.clicked.connect(self.completeChanged)

    def isComplete(self):
        global system_channel_restorer
        if self.yes.isChecked():
            system_channel_restorer = True
            return True
        elif self.no.isChecked():
            system_channel_restorer = False
            return True
        return False

    def nextId(self):
        if self.yes.isChecked():
            return 301
        elif self.no.isChecked():
            return 302
        return 0


class MinimalExtraChannels(QWizardPage):
    local_selected_channels: list
    checkboxes: dict

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle(self.tr("Step 2: Extras Setup"))
        self.setSubTitle(self.tr("Select the extra channels you want to install"))

        label = QLabel(self.tr("Select the channels you'd like to install from the list below:"))

        layout = QVBoxLayout()

        layout.addWidget(label)

        # List of channels
        channels = {
            "ws_us": "Wii Speak Channel (USA)",
            "ws_eu": "Wii Speak Channel (PAL)",
            "ws_jp": "Wii Speak Channel (Japan)",
            "tatc_eu": "Today and Tomorrow Channel (PAL)",
            "tatc_jp": "Today and Tomorrow Channel (Japan)"
        }

        # Dictionary to hold checkboxes
        self.checkboxes = {}

        # Add checkboxes to layout
        for key, label in channels.items():
            checkbox = QCheckBox(label)
            layout.addWidget(checkbox)
            self.checkboxes[key] = checkbox
            checkbox.clicked.connect(self.completeChanged)

        # Set layout
        self.setLayout(layout)

    def validatePage(self):
        global selected_channels

        self.local_selected_channels = [
            key for key, checkbox in self.checkboxes.items() if checkbox.isChecked()
        ]

        selected_channels = []
        for item in self.local_selected_channels:
            selected_channels.append(item)

        return True

    def nextId(self):
        return 303

    def isComplete(self):
        global selected_channels

        for checkbox in self.checkboxes.values():
            if checkbox.isChecked():
                return True
        return False


class FullExtraChannels(QWizardPage):
    local_selected_channels: list
    checkboxes: dict

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle(self.tr("Step 2: Extras Setup"))
        self.setSubTitle(self.tr("Select the extra channels you want to install"))

        label = QLabel(self.tr("Select the channels you'd like to install from the list below:"))

        layout = QVBoxLayout()

        layout.addWidget(label)

        # List of channels
        channels = {
            "ws_us": "Wii Speak Channel (USA)",
            "ws_eu": "Wii Speak Channel (PAL)",
            "ws_jp": "Wii Speak Channel (Japan)",
            "tatc_eu": "Today and Tomorrow Channel (PAL)",
            "tatc_jp": "Today and Tomorrow Channel (Japan)",
            "ic_us": "Internet Channel (USA)",
            "ic_eu": "Internet Channel (PAL)",
            "ic_jp": "Internet Channel (Japan)"
        }

        # Dictionary to hold checkboxes
        self.checkboxes = {}

        # Add checkboxes to layout
        for key, label in channels.items():
            checkbox = QCheckBox(label)
            layout.addWidget(checkbox)
            self.checkboxes[key] = checkbox
            checkbox.clicked.connect(self.completeChanged)

        # Set layout
        self.setLayout(layout)

    def validatePage(self):
        global selected_channels

        self.local_selected_channels = [
            key for key, checkbox in self.checkboxes.items() if checkbox.isChecked()
        ]

        selected_channels = []
        for item in self.local_selected_channels:
            selected_channels.append(item)

        return True

    def nextId(self):
        return 303

    def isComplete(self):
        global selected_channels

        for checkbox in self.checkboxes.values():
            if checkbox.isChecked():
                return True
        return False


class ExtrasPlatformConfiguration(QWizardPage):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle(self.tr("Step 3: Extras Setup"))
        self.setSubTitle(self.tr("Choose console platform"))

        self.label = QLabel(self.tr("Which platform will you be installing the channels onto?"))

        self.Wii = QRadioButton(self.tr("Wii"))
        self.vWii = QRadioButton(self.tr("vWii (Wii U)"))
        self.Dolphin = QRadioButton(self.tr("Dolphin Emulator"))

        self.buttonGroup = QButtonGroup(self)
        self.buttonGroup.addButton(self.Wii)
        self.buttonGroup.addButton(self.vWii)
        self.buttonGroup.addButton(self.Dolphin)

        layout = QVBoxLayout()
        layout.addWidget(self.label)
        layout.addWidget(self.Wii)
        layout.addWidget(self.vWii)
        layout.addWidget(self.Dolphin)

        self.setLayout(layout)

        self.Wii.clicked.connect(self.completeChanged.emit)
        self.vWii.clicked.connect(self.completeChanged.emit)
        self.Dolphin.clicked.connect(self.completeChanged.emit)

    def isComplete(self):
        if self.Wii.isChecked():
            ExtraPatchingPage.platform = Platforms.Wii
            return True
        elif self.vWii.isChecked():
            ExtraPatchingPage.platform = Platforms.vWii
            return True
        elif self.Dolphin.isChecked():
            ExtraPatchingPage.platform = Platforms.Dolphin
            return True
        return False


class ExtraPatchingPage(QWizardPage):
    patching_complete = False
    percentage: int
    status: str
    platform = Platforms.Wii

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setTitle(self.tr("Patching in progress"))
        self.setSubTitle(self.tr("Please wait while the patcher works its magic!"))

        self.label = QLabel(self.tr("Downloading files..."))
        self.progress_bar = QProgressBar(self)

        layout = QVBoxLayout()
        layout.addWidget(self.label)
        layout.addWidget(self.progress_bar)

        self.setLayout(layout)

        # Create thread to perform patching
        self.logic_thread = QThread()
        self.logic_worker = PatchingWorker()

    def initializePage(self):
        global selected_channels
        QTimer.singleShot(0, self.disable_back_button)

        # Pass variables to instance of logic thread
        self.logic_worker.setup_type = SetupTypes.Extras
        self.logic_worker.platform = self.platform

        if self.platform != Platforms.Dolphin:
            self.logic_worker.selected_channels = ["download"] + selected_channels
        else:
            self.logic_worker.selected_channels = selected_channels

        self.logic_worker.moveToThread(self.logic_thread)
        self.logic_thread.started.connect(self.logic_worker.patching_functions)

        # Connect thread signals
        self.logic_worker.broadcast_percentage.connect(self.set_percentage)
        self.logic_worker.broadcast_status.connect(self.set_status)
        self.logic_worker.error.connect(self.handle_error)

        self.logic_worker.finished.connect(self.logic_finished)
        self.logic_worker.finished.connect(self.logic_thread.quit)
        self.logic_thread.finished.connect(self.logic_worker.deleteLater)
        self.logic_thread.finished.connect(self.logic_thread.deleteLater)

        # Start thread
        self.logic_thread.start()

    def isComplete(self):
        return self.patching_complete

    def disable_back_button(self):
        self.wizard().button(QWizard.WizardButton.BackButton).setEnabled(False)

    def logic_finished(self):
        self.patching_complete = True
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
    
    def handle_error(self, error: str):
        """Display errors thrown from the patching logic to the user"""
        QMessageBox.warning(QWidget(),
                             "WiiLink Patcher - Warning",
                             f"""An exception was encountered while patching.
Exception: '{error}'
Please report this issue in the WiiLink Discord Server (discord.gg/wiilink)."""
        )