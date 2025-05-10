import os
from PySide6.QtWidgets import (
    QWizardPage,
    QLabel,
    QVBoxLayout,
    QRadioButton,
    QCheckBox,
    QScrollArea,
    QWidget,
    QSizePolicy,
)

from .enums import *
from .patch import PatchingPage
from modules.widgets import CollapsibleBox


class ExtrasSystemChannelRestorer(QWizardPage):
    local_selected_channels: list

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle(self.tr("Step 1: Extras Setup"))
        self.setSubTitle(
            self.tr("Decide if you'd like to download System Channel Restorer")
        )

        self.label = QLabel(
            self.tr("<b>Would you like to download System Channel Restorer?</b>")
        )
        self.explanation = QLabel(
            self.tr(
                """System Channel Restorer is a homebrew application that allows for installation of Photo Channel 1.1 and the Internet Channel.
Use of System Channel Restorer requires an internet connection on your console."""
            )
        )
        self.explanation.setWordWrap(True)

        self.yes = QRadioButton(self.tr("Yes, download System Channel Restorer"))
        self.no = QRadioButton(self.tr("No, I'd prefer offline WADs"))

        # Layout
        self.layout = QVBoxLayout()

        self.layout.addWidget(self.label)
        self.layout.addWidget(self.explanation)

        self.layout.addWidget(self.yes)
        self.layout.addWidget(self.no)

        self.yes.setChecked(True)

        self.setLayout(self.layout)

        self.yes.clicked.connect(self.completeChanged)
        self.no.clicked.connect(self.completeChanged)

    def isComplete(self):
        if self.yes.isChecked():
            return True
        elif self.no.isChecked():
            return True
        return False

    def nextId(self):
        if self.yes.isChecked():
            return 301
        elif self.no.isChecked():
            return 302
        return 0


class MinimalExtraChannels(QWizardPage):
    channels = {
        "Wii Speak Channel": {
            "ws_us": "Wii Speak Channel (USA)",
            "ws_eu": "Wii Speak Channel (PAL)",
            "ws_jp": "Wii Speak Channel (Japan)",
        },
        "Today and Tomorrow Channel": {
            "tatc_eu": "Today and Tomorrow Channel (PAL)",
            "tatc_jp": "Today and Tomorrow Channel (Japan)",
        },
    }

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle(self.tr("Step 2: Extras Setup"))
        self.setSubTitle(self.tr("Select the extra channels you want to install"))

        self.label = QLabel(
            self.tr("Select the channels you'd like to install from the list below:")
        )

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)

        container = QWidget()
        container_layout = QVBoxLayout(container)
        container_layout.setContentsMargins(0, 0, 0, 0)
        container_layout.setSpacing(0)

        self.checkboxes = {}

        for category, channels in self.channels.items():
            box = CollapsibleBox(title=category)
            # Make the toggle button full width
            box.toggle_button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
            box.toggle_button.setMinimumWidth(0)
            box.toggle_button.setMaximumWidth(16777215)
            for key, label in channels.items():
                checkbox = QCheckBox(label)
                box.content_layout.addWidget(checkbox)
                self.checkboxes[key] = checkbox
                checkbox.clicked.connect(self.completeChanged.emit)
            container_layout.addWidget(box)

        container_layout.addStretch()
        scroll_area.setWidget(container)

        layout = QVBoxLayout()

        layout.addWidget(self.label)
        layout.addWidget(scroll_area)

        self.setLayout(layout)

    def validatePage(self):
        selected_channels = []

        for key, checkbox in self.checkboxes.items():
            if checkbox.isChecked():
                selected_channels.append(key)

        PatchingPage.selected_channels = ["scr"] + selected_channels

        return True

    def nextId(self):
        return 303

    def isComplete(self):
        for checkbox in self.checkboxes.values():
            if checkbox.isChecked():
                return True

        return False


class FullExtraChannels(QWizardPage):
    channels = {
        "Wii Speak Channel": {
            "ws_us": "Wii Speak Channel (USA)",
            "ws_eu": "Wii Speak Channel (PAL)",
            "ws_jp": "Wii Speak Channel (Japan)",
        },
        "Today and Tomorrow Channel": {
            "tatc_eu": "Today and Tomorrow Channel (PAL)",
            "tatc_jp": "Today and Tomorrow Channel (Japan)",
        },
        "Internet Channel": {
            "ic_us": "Internet Channel (USA)",
            "ic_eu": "Internet Channel (PAL)",
            "ic_jp": "Internet Channel (Japan)",
        },
    }
    local_selected_channels: list
    checkboxes: dict

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle(self.tr("Step 2: Extras Setup"))
        self.setSubTitle(self.tr("Select the extra channels you want to install"))

        self.label = QLabel(
            self.tr("Select the channels you'd like to install from the list below:")
        )

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)

        container = QWidget()
        container_layout = QVBoxLayout(container)
        container_layout.setContentsMargins(0, 0, 0, 0)
        container_layout.setSpacing(0)

        self.checkboxes = {}

        for category, channels in self.channels.items():
            box = CollapsibleBox(title=category)
            # Make the toggle button full width
            box.toggle_button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
            box.toggle_button.setMinimumWidth(0)
            box.toggle_button.setMaximumWidth(16777215)
            for key, label in channels.items():
                checkbox = QCheckBox(label)
                box.content_layout.addWidget(checkbox)
                self.checkboxes[key] = checkbox
                checkbox.clicked.connect(self.completeChanged.emit)
            container_layout.addWidget(box)

        container_layout.addStretch()
        scroll_area.setWidget(container)

        layout = QVBoxLayout()

        layout.addWidget(self.label)
        layout.addWidget(scroll_area)

        self.setLayout(layout)

    def validatePage(self):
        selected_channels = []

        for key, checkbox in self.checkboxes.items():
            if checkbox.isChecked():
                selected_channels.append(key)

        PatchingPage.selected_channels = selected_channels

        return True

    def nextId(self):
        return 303

    def isComplete(self):
        for checkbox in self.checkboxes.values():
            if checkbox.isChecked():
                return True

        return False


class ExtrasPlatformConfiguration(QWizardPage):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle(self.tr("Step 3: Extras Setup"))
        self.setSubTitle(self.tr("Choose console platform."))

        self.label = QLabel(
            self.tr("Which platform will you be installing the channels onto?")
        )

        self.platforms = {
            Platforms.Wii: "Wii",
            Platforms.vWii: "vWii (Wii U)",
            Platforms.Dolphin: self.tr("Dolphin Emulator"),
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

        # Select the first option
        next(iter(self.buttons.values())).setChecked(True)

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
            Regions.Japan: self.tr("Japan (NTSC-J)"),
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

        # Select the first option
        next(iter(self.buttons.values())).setChecked(True)

        # Set layout
        self.setLayout(self.layout)

    def isComplete(self):
        for key, button in self.buttons.items():
            if button.isChecked():
                PatchingPage.region = key
                return True

        return False

    def nextId(self):
        if os.path.exists("WiiLink"):
            return 10

        return 11