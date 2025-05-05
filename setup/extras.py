from PySide6.QtWidgets import QWizardPage, QLabel, QVBoxLayout, QRadioButton, QCheckBox

from .enums import *
from .patch import PatchingPage

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
        global system_channel_restorer

        self.local_selected_channels = [
            key for key, checkbox in self.checkboxes.items() if checkbox.isChecked()
        ]

        selected_channels = []
        for item in self.local_selected_channels:
            selected_channels.append(item)
        
        if system_channel_restorer:
            PatchingPage.selected_channels = ["scr"] + selected_channels
        else:
            PatchingPage.selected_channels = selected_channels

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
        global system_channel_restorer

        self.local_selected_channels = [
            key for key, checkbox in self.checkboxes.items() if checkbox.isChecked()
        ]

        selected_channels = []
        for item in self.local_selected_channels:
            selected_channels.append(item)
        
        if system_channel_restorer:
            PatchingPage.selected_channels = ["scr"] + selected_channels
        else:
            PatchingPage.selected_channels = selected_channels

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
        self.setSubTitle(self.tr("Choose console platform."))

        self.label = QLabel(self.tr("Which platform will you be installing the channels onto?"))

        self.platforms = {
            Platforms.Wii: "Wii",
            Platforms.vWii: "vWii (Wii U)",
            Platforms.Dolphin: self.tr("Dolphin Emulator")
        }

        # Layout
        self.layout = QVBoxLayout()

        self.layout.addWidget(self.label)

        # Dictionary to hold buttons
        self.buttons = {}

        # Add buttons to layout
        for key, label in self.platforms.items():
            button = QRadioButton(label)
            self.layout.addWidget(button)
            self.buttons[key] = button
            button.clicked.connect(self.completeChanged.emit)

        # Set layout
        self.setLayout(self.layout)

    def isComplete(self):
        for key, button in self.buttons.items():
            if button.isChecked():
                PatchingPage.platform = key
                return True

        return False


class ExtrasRegionConfiguration(QWizardPage):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle(self.tr("Step 4: Extras Setup"))
        self.setSubTitle(self.tr("Choose console region."))

        self.label = QLabel(self.tr("Which region is your console?"))

        self.regions = {
            Regions.USA: self.tr("North America (NTSC-U)"),
            Regions.PAL: self.tr("Europe (PAL)"),
            Regions.Japan: self.tr("Japan (NTSC-J)")
        }

        # Layout
        self.layout = QVBoxLayout()

        self.layout.addWidget(self.label)

        # Dictionary to hold buttons
        self.buttons = {}

        # Add buttons to layout
        for key, label in self.regions.items():
            button = QRadioButton(label)
            self.layout.addWidget(button)
            self.buttons[key] = button
            button.clicked.connect(self.completeChanged.emit)

        # Set layout
        self.setLayout(self.layout)

    def isComplete(self):
        for key, button in self.buttons.items():
            if button.isChecked():
                PatchingPage.region = key
                return True

        return False
    
    def nextId(self):
        return 10