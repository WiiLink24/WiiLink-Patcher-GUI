import pathlib
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

from .patch import PatchingPage
from .enums import *
from modules.widgets import CollapsibleBox

selected_wc24_channels = []


class CustomWiiConnect24Channels(QWizardPage):
    channels = {
        "Forecast Channel": {
            "forecast_us": "Forecast Channel (USA)",
            "forecast_eu": "Forecast Channel (PAL)",
            "forecast_jp": "Forecast Channel (Japan)",
        },
        "News Channel": {
            "news_us": "News Channel (USA)",
            "news_eu": "News Channel (PAL)",
            "news_jp": "News Channel (Japan)",
        },
        "Nintendo Channel": {
            "nc_us": "Nintendo Channel (USA)",
            "nc_eu": "Nintendo Channel (PAL)",
            "nc_jp": "Minna no Nintendo Channel (Japan)",
        },
        "Everybody Votes Channel": {
            "evc_us": "Everybody Votes Channel (USA)",
            "evc_eu": "Everybody Votes Channel (PAL)",
            "evc_jp": "Everybody Votes Channel (Japan)",
        },
        "Check Mii Out Channel": {
            "cmoc_us": "Check Mii Out Channel (USA)",
            "cmoc_eu": "Mii Contest Channel (PAL)",
            "cmoc_jp": "Mii Contest Channel (Japan)",
        },
    }

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle(self.tr("Step 1: Custom Setup"))
        self.setSubTitle(
            self.tr("Select the WiiConnect24 channels you want to install")
        )

        self.label = QLabel(
            self.tr("Select the channels you'd like to install from the list below:")
        )

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFixedHeight(300)

        container = QWidget()
        container_layout = QVBoxLayout(container)
        container_layout.setContentsMargins(0, 0, 0, 0)
        container_layout.setSpacing(0)

        for category, channels in self.channels.items():
            box = CollapsibleBox(title=category)
            box.toggle_button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
            box.toggle_button.setMinimumWidth(0)
            for key, label in channels.items():
                checkbox = QCheckBox(label)
                box.content_layout.addWidget(checkbox)
                self.registerField(key, checkbox)
            container_layout.addWidget(box)

        container_layout.addStretch()
        scroll_area.setWidget(container)

        layout = QVBoxLayout()

        layout.addWidget(self.label)
        layout.addWidget(scroll_area)

        self.setLayout(layout)

    def validatePage(self):
        global selected_wc24_channels

        for category in self.channels.values():
            for channel in category.keys():
                if self.wizard().field(channel):
                    selected_wc24_channels.append(channel)

        return True


class CustomRegionalChannels(QWizardPage):
    channels = {
        "Wii Room": {
            "wiiroom_en": "Wii Room (English)",
            "wiiroom_es": "Wii Room (Español)",
            "wiiroom_fr": "Wii Room (Français)",
            "wiiroom_de": "Wii Room (Deutsch)",
            "wiiroom_it": "Wii Room (Italiano)",
            "wiiroom_nl": "Wii Room (Nederlands)",
            "wiiroom_ptbr": "Wii Room (Português (Brasil))",
            "wiiroom_ru": "Wii Room (Русский)",
            "wiiroom_jp": "Wii no Ma (Japanese)",
        },
        "Photo Prints Channel": {
            "digicam_en": "Photo Prints Channel (English)",
            "digicam_jp": "Digicam Print Channel (Japanese)",
        },
        "Food Channel": {
            "food_en": "Food Channel (Standard) (English)",
            "food_jp": "Demae Channel (Standard) (Japanese)",
            "dominos": "Food Channel (Domino's) (English)",
        },
        "Kirby TV Channel": {"ktv": "Kirby TV Channel"},
    }

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle(self.tr("Step 2: Custom Setup"))
        self.setSubTitle(self.tr("Select the regional channels you want to install"))

        self.label = QLabel(
            self.tr("Select the channels you'd like to install from the list below:")
        )

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)

        container = QWidget()
        container_layout = QVBoxLayout(container)
        container_layout.setContentsMargins(0, 0, 0, 0)

        for category, channels in self.channels.items():
            box = CollapsibleBox(title=category)
            box.toggle_button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
            box.toggle_button.setMinimumWidth(0)
            box.toggle_button.setMaximumWidth(16777215)  # Max int for width
            for key, label in channels.items():
                checkbox = QCheckBox(label)
                box.content_layout.addWidget(checkbox)
                self.registerField(key, checkbox)
                checkbox.clicked.connect(self.completeChanged.emit)
            container_layout.addWidget(box)

        container_layout.addStretch()
        scroll_area.setWidget(container)

        layout = QVBoxLayout()

        layout.addWidget(self.label)
        layout.addWidget(scroll_area)

        self.setLayout(layout)

    def validatePage(self):
        global selected_wc24_channels

        selected_regional_channels = []
        for category in self.channels.values():
            for channel in category.keys():
                if self.wizard().field(channel):
                    selected_regional_channels.append(channel)

        if len(selected_regional_channels) > 0:
            PatchingPage.regional_channels = True

        PatchingPage.selected_channels = (
            selected_wc24_channels + selected_regional_channels
        )

        return True

    def isComplete(self):
        for channel in CustomWiiConnect24Channels.channels.values():
            for key in channel.keys():
                if self.wizard().field(key):
                    return True

        for channel in self.channels.values():
            for key in channel.keys():
                if self.wizard().field(key):
                    return True

        return False


class CustomPlatformConfiguration(QWizardPage):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle(self.tr("Step 3: Custom Setup"))
        self.setSubTitle(self.tr("Choose console platform"))

        self.label = QLabel(
            self.tr("Which platform will you be installing WiiLink onto?")
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


class CustomRegionConfiguration(QWizardPage):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle(self.tr("Step 4: Custom Setup"))
        self.setSubTitle(self.tr("Choose console region"))

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
        if pathlib.Path().joinpath("WiiLink").exists():
            return 10

        return 11
