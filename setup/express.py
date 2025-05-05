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

        self.USA = QRadioButton(self.tr("North America (NTSC-U)"))
        self.PAL = QRadioButton(self.tr("Europe (PAL)"))
        self.Japan = QRadioButton(self.tr("Japan (NTSC-J)"))

        self.regions = [self.USA, self.PAL, self.Japan]

        # Group radio buttons
        self.buttonGroup = QButtonGroup(self)
        for region in self.regions:
            self.buttonGroup.addButton(region)

        layout = QVBoxLayout()
        layout.addWidget(self.label)

        # Add widgets to layout
        for button in self.regions:
            layout.addWidget(button)

        self.setLayout(layout)

        for button in self.regions:
            button.toggled.connect(lambda: self.completeChanged.emit())

    def isComplete(self):
        """Enable Next button only if a radio button is selected"""
        global region

        if self.USA.isChecked():
            PatchingPage.region = Regions.USA
            region = "us"
            return True
        elif self.PAL.isChecked():
            PatchingPage.region = Regions.PAL
            region = "eu"
            return True
        elif self.Japan.isChecked():
            PatchingPage.region = Regions.Japan
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

        self.buttonGroup = QButtonGroup(self)
        self.buttonGroup.addButton(self.Yes)
        self.buttonGroup.addButton(self.No)

        layout = QVBoxLayout()
        layout.addWidget(self.label)
        layout.addWidget(self.Yes)
        layout.addWidget(self.No)

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

        self.buttonGroup = QButtonGroup(self)
        self.buttonGroup.addButton(self.Translated)
        self.buttonGroup.addButton(self.Japanese)

        layout = QVBoxLayout()
        layout.addWidget(self.label)
        layout.addWidget(self.Translated)
        layout.addWidget(self.Japanese)

        self.setLayout(layout)

        self.Translated.toggled.connect(lambda: self.completeChanged.emit())
        self.Japanese.toggled.connect(lambda: self.completeChanged.emit())

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
    language = Languages.Japan
    languages = {
        Languages.English: "🇺🇸 English",
        Languages.Spanish: "🇪🇸 Español",
        Languages.French: "🇫🇷 Français",
        Languages.German: "🇩🇪 Deutsch",
        Languages.Italian: "🇮🇹 Italiano", 
        Languages.Dutch: "🇳🇱 Nederlands",
        Languages.Portuguese: "🇧🇷 Português (Brasil)",
        Languages.Russian: "🇷🇺 Русский"
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

        # Set layout
        self.setLayout(self.layout)

        self.buttons[Languages.Russian].clicked.connect(self.russian_notice)

    def isComplete(self):
        """Enable Next button only if a radio button is selected"""
        global wiiroom_lang
        if self.buttons[Languages.English].isChecked():
            wiiroom_lang = "en"
            return True
        elif self.buttons[Languages.Spanish].isChecked():
            wiiroom_lang = "es"
            return True
        elif self.buttons[Languages.French].isChecked():
            wiiroom_lang = "fr"
            return True
        elif self.buttons[Languages.German].isChecked():
            wiiroom_lang = "de"
            return True
        elif self.buttons[Languages.Italian].isChecked():
            wiiroom_lang = "it"
            return True
        elif self.buttons[Languages.Dutch].isChecked():
            wiiroom_lang = "nl"
            return True
        elif self.buttons[Languages.Portuguese].isChecked():
            wiiroom_lang = "ptbr"
            return True
        elif self.buttons[Languages.Russian].isChecked():
            wiiroom_lang = "ru"
            return True
        elif self.buttons[Languages.Japan].isChecked():
            wiiroom_lang = "jp"
            return True
        
        return False

    def russian_notice(self):
        if self.buttons[Languages.Russian].isChecked:
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

        self.Standard = QRadioButton(self.tr("Standard (Fake Ordering)"))
        self.Dominos = QRadioButton(self.tr("Domino's (US and Canada only)"))

        self.buttonGroup = QButtonGroup(self)
        self.buttonGroup.addButton(self.Standard)
        self.buttonGroup.addButton(self.Dominos)

        layout = QVBoxLayout()
        layout.addWidget(self.label)
        layout.addWidget(self.Standard)
        layout.addWidget(self.Dominos)

        self.setLayout(layout)

        self.Standard.toggled.connect(lambda: self.completeChanged.emit())
        self.Dominos.toggled.connect(lambda: self.completeChanged.emit())

    def isComplete(self):
        global demae
        global regional_lang

        if self.Standard.isChecked():
            demae = f"food_{regional_lang}"
            return True
        elif self.Dominos.isChecked():
            demae = "dominos"
            return True
        return False


class ExpressPlatformConfiguration(QWizardPage):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle(self.tr("Step 3: Express Setup"))
        self.setSubTitle(self.tr("Choose console platform."))

        self.label = QLabel(self.tr("Which platform will you be installing WiiLink onto?"))

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
            PatchingPage.platform = Platforms.Wii
            return True
        elif self.vWii.isChecked():
            PatchingPage.platform = Platforms.vWii
            return True
        elif self.Dolphin.isChecked():
            PatchingPage.platform = Platforms.Dolphin
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