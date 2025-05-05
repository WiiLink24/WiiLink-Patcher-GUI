from PySide6.QtWidgets import QWizardPage, QLabel, QVBoxLayout, QRadioButton, QWizard, QCheckBox
from .patch import PatchingPage
from .enums import *

selected_wc24_channels = []


class CustomWiiConnect24Channels(QWizardPage):
    local_selected_channels: list
    channels = {
        "forecast_us": "Forecast Channel (USA)",
        "forecast_eu": "Forecast Channel (PAL)",
        "forecast_jp": "Forecast Channel (Japan)",
        "news_us": "News Channel (USA)",
        "news_eu": "News Channel (PAL)",
        "news_jp": "News Channel (Japan)",
        "nc_us": "Nintendo Channel (USA)",
        "nc_eu": "Nintendo Channel (PAL)",
        "nc_jp": "Minna no Nintendo Channel (Japan)",
        "evc_us": "Everybody Votes Channel (USA)",
        "evc_eu": "Everybody Votes Channel (PAL)",
        "evc_jp": "Everybody Votes Channel (Japan)",
        "cmoc_us": "Check Mii Out Channel (USA)",
        "cmoc_eu": "Mii Contest Channel (PAL)",
        "cmoc_jp": "Mii Contest Channel (Japan)"
    }

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle(self.tr("Step 1: Custom Setup"))
        self.setSubTitle(self.tr("Select the WiiConnect24 channels you want to install"))

        self.label = QLabel(self.tr("Select the channels you'd like to install from the list below:"))

        # Layout
        self.layout = QVBoxLayout()

        self.layout.addWidget(self.label)

        # Dictionary to hold checkboxes
        self.checkboxes = {}

        # Add checkboxes to layout
        for key, label in self.channels.items():
            checkbox = QCheckBox(label)
            self.layout.addWidget(checkbox)
            self.checkboxes[key] = checkbox
            self.registerField(key, checkbox)

        # Set layout
        self.setLayout(self.layout)

    def initializePage(self):
        self.wizard().button(QWizard.WizardButton.NextButton).clicked.connect(self.save_selected_channels)

    def save_selected_channels(self):
        global selected_wc24_channels
        self.local_selected_channels = [
            key for key, checkbox in self.checkboxes.items() if checkbox.isChecked()
        ]
        selected_wc24_channels = []
        for item in self.local_selected_channels:
            selected_wc24_channels.append(item)


class CustomRegionalChannels(QWizardPage):
    local_selected_channels: list
    channels = {
        "wiiroom_en": "Wii Room (English)",
        "wiiroom_es": "Wii Room (Español)",
        "wiiroom_fr": "Wii Room (Français)",
        "wiiroom_de": "Wii Room (Deutsch)",
        "wiiroom_it": "Wii Room (Italiano)",
        "wiiroom_nl": "Wii Room (Nederlands)",
        "wiiroom_ptbr": "Wii Room (Português (Brasil))",
        "wiiroom_ru": "Wii Room (Русский)",
        "wiiroom_jp": "Wii no Ma (Japanese)",
        "digicam_en": "Photo Prints Channel (English)",
        "digicam_jp": "Digicam Print Channel (Japanese)",
        "food_en": "Food Channel (Standard) (English)",
        "food_jp": "Demae Channel (Standard) (Japanese)",
        "dominos": "Food Channel (Domino's) (English)",
        "ktv": "Kirby TV Channel"
    }

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle(self.tr("Step 2: Custom Setup"))
        self.setSubTitle(self.tr("Select the regional channels you want to install"))

        self.label = QLabel(self.tr("Select the channels you'd like to install from the list below:"))

        # Layout
        self.layout = QVBoxLayout()

        self.layout.addWidget(self.label)

        # Dictionary to hold checkboxes
        self.checkboxes = {}

        # Add checkboxes to layout
        for key, label in self.channels.items():
            checkbox = QCheckBox(label)
            self.layout.addWidget(checkbox)
            self.checkboxes[key] = checkbox
            checkbox.clicked.connect(self.completeChanged)

        # Set layout
        self.setLayout(self.layout)

    def validatePage(self):
        global selected_wc24_channels

        self.local_selected_channels = [
            key for key, checkbox in self.checkboxes.items() if checkbox.isChecked()
        ]
        selected_regional_channels = []
        for item in self.local_selected_channels:
            selected_regional_channels.append(item)

        if len(selected_regional_channels) > 0:
            PatchingPage.regional_channels = True
        
        PatchingPage.selected_channels = selected_wc24_channels + selected_regional_channels

        return True

    def isComplete(self):
        for key in CustomWiiConnect24Channels.channels.keys():
            if self.wizard().field(key):
                return True

        for checkbox in self.checkboxes.values():
            if checkbox.isChecked():
                return True
        return False


class CustomPlatformConfiguration(QWizardPage):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle(self.tr("Step 3: Custom Setup"))
        self.setSubTitle(self.tr("Choose console platform"))

        self.label = QLabel(self.tr("Which platform will you be installing WiiLink onto?"))

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
        return 10