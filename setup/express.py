from PySide6.QtWidgets import QWizardPage, QLabel, QVBoxLayout, QRadioButton, QButtonGroup, QMessageBox

from .patch import PatchingPage
from .enums import *

regional_channels = False
regional_lang = ""
wiiroom_lang = ""
demae = ""
region = ""


class ExpressRegion(QWizardPage):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle(self.tr("Step 1: Express Setup"))
        self.setSubTitle(self.tr("Choose your region for WiiConnect24 services."))

        self.label = QLabel(self.tr("For the WiiConnect24 services, which region would you like to install?"))

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
        global region

        for key, button in self.buttons.items():
            if button.isChecked():
                PatchingPage.region = key
                match key:
                    case Regions.USA:
                        region = "us"
                    case Regions.PAL:
                        region = "eu"
                    case Regions.Japan:
                        region = "jp"
                return True

        return False


class ExpressRegionalChannels(QWizardPage):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle(self.tr("Step 2: Express Setup"))
        self.setSubTitle(self.tr("Choose if you'd like to install additional regional channels."))

        self.label = QLabel(self.tr("""Would you like to install WiiLink's regional channel services?

Services that would be installed:

- Wii Room (Wii no Ma)
- Photo Prints Channel (Digicam Print Channel)
- Food Channel (Demae Channel)
- Kirby TV Channel"""))

        self.Yes = QRadioButton(self.tr("Yes"))
        self.No = QRadioButton(self.tr("No"))

        layout = QVBoxLayout()

        layout.addWidget(self.label)

        layout.addWidget(self.Yes)
        layout.addWidget(self.No)

        self.Yes.setChecked(True)

        self.setLayout(layout)

        self.Yes.toggled.connect(lambda: self.completeChanged.emit())
        self.No.toggled.connect(lambda: self.completeChanged.emit())

    def isComplete(self):
        global regional_channels
        if self.Yes.isChecked():
            regional_channels = True
            return True
        elif self.No.isChecked():
            regional_channels = False
            return True
        return False

    def nextId(self):
        if self.Yes.isChecked():
            return 102
        elif self.No.isChecked():
            return 105
        return 0


class ExpressRegionalChannelTranslation(QWizardPage):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle(self.tr("Step 2A: Express Setup"))
        self.setSubTitle(self.tr("Choose if you'd like translations for WiiLink's regional channels."))

        self.label = QLabel(self.tr(
            "Would you like <b>Wii Room</b>, <b>Photo Prints Channel</b>, and the <b>Food Channel</b> to be translated?"))

        self.Translated = QRadioButton(self.tr("Translated (eg. English, French, etc.)"))
        self.Japanese = QRadioButton(self.tr("Japanese"))

        layout = QVBoxLayout()

        layout.addWidget(self.label)

        layout.addWidget(self.Translated)
        layout.addWidget(self.Japanese)

        self.Translated.setChecked(True)

        self.setLayout(layout)

        self.Translated.clicked.connect(self.completeChanged.emit)
        self.Japanese.clicked.connect(self.completeChanged.emit)

    def isComplete(self):
        global regional_lang
        if self.Translated.isChecked():
            regional_lang = "en"
            return True
        elif self.Japanese.isChecked():
            regional_lang = "jp"
            return True
        return False

    def nextId(self):
        if self.Translated.isChecked():
            return 103
        elif self.Japanese.isChecked():
            return 104
        return 0


class ExpressRegionalChannelLanguage(QWizardPage):
    languages = {
        "en": "🇺🇸 English",
        "es": "🇪🇸 Español",
        "fr": "🇫🇷 Français",
        "de": "🇩🇪 Deutsch",
        "it": "🇮🇹 Italiano", 
        "nl": "🇳🇱 Nederlands",
        "ptbr": "🇧🇷 Português (Brasil)",
        "ru": "🇷🇺 Русский"
    }

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle(self.tr("Step 2B: Express Setup"))
        self.setSubTitle(self.tr("Choose the language for Wii Room."))

        self.label = QLabel(self.tr("What language would you like <b>Wii Room</b> to be in?"))

        # Layout
        self.layout = QVBoxLayout()

        self.layout.addWidget(self.label)

        # Dictionary to hold buttons
        self.buttons = {}

        # Add buttons to layout
        for key, label in self.languages.items():
            button = QRadioButton(label)
            self.layout.addWidget(button)
            self.buttons[key] = button
            button.clicked.connect(self.completeChanged.emit)

        # Select the first option
        next(iter(self.buttons.values())).setChecked(True)

        # Set layout
        self.setLayout(self.layout)

        self.buttons["ru"].clicked.connect(self.russian_notice)

    def isComplete(self):
        """Enable Next button only if a radio button is selected"""
        global wiiroom_lang

        for key, button in self.buttons.items():
            if button.isChecked:
                wiiroom_lang = key
                return True
        
        return False

    def russian_notice(self):
        if self.buttons["ru"].isChecked:
            QMessageBox.warning(self,
                                self.tr("Russian notice for Wii Room"),
                                self.tr("""You have selected the Russian translation for Wii Room
Proper functionality is not guaranteed for systems without the Russian Wii Menu.
Follow the installation guide at https://wii.zazios.ru/rus_menu if you have not already done so.
(The guide is only available in Russian for now)""")
                                )


class ExpressDemaeConfiguration(QWizardPage):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle(self.tr("Step 2C: Express Setup"))
        self.setSubTitle(self.tr("Choose Food Channel version."))

        self.label = QLabel(self.tr("Which version of the <b>Food Channel</b> would you like to install?"))

        self.demae_configs = {
            DemaeConfigs.Standard: self.tr("Standard (Fake Ordering)"),
            DemaeConfigs.Dominos: self.tr("Domino's (US and Canada only)")
        }

        self.layout = QVBoxLayout()

        self.layout.addWidget(self.label)

        # Dictionary to hold buttons
        self.buttons = {}

        # Add buttons to layout
        for key, label in self.demae_configs.items():
            button = QRadioButton(label)
            self.layout.addWidget(button)
            self.buttons[key] = button
            button.clicked.connect(self.completeChanged.emit)

        # Select the first option
        next(iter(self.buttons.values())).setChecked(True)

        self.setLayout(self.layout)

    def isComplete(self):
        global demae
        global regional_lang

        if self.buttons[DemaeConfigs.Standard].isChecked():
            demae = f"food_{regional_lang}"
            return True
        elif self.buttons[DemaeConfigs.Dominos].isChecked():
            demae = "dominos"
            return True
        return False


class ExpressPlatformConfiguration(QWizardPage):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle(self.tr("Step 3: Express Setup"))
        self.setSubTitle(self.tr("Choose console platform."))

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

    def validatePage(self):
        global regional_lang
        global wiiroom_lang
        global demae
        global regional_channels
        global region

        selected_channels = [
            "download",
            f"nc_{region}",
            f"forecast_{region}",
            f"news_{region}",
            f"evc_{region}",
            f"cmoc_{region}"
        ]

        if regional_channels:
            selected_channels.extend([
                f"wiiroom_{wiiroom_lang}",
                f"digicam_{regional_lang}",
                demae,
                "ktv"
            ])

        PatchingPage.regional_channels = regional_channels
        PatchingPage.selected_channels = selected_channels

        return True

    def nextId(self):
        return 10
