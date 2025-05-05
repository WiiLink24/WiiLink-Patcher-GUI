from PySide6.QtCore import QTimer, QThread
from PySide6.QtWidgets import QWizardPage, QLabel, QVBoxLayout, QRadioButton, QButtonGroup, QMessageBox, QProgressBar, QWizard, QWidget
from .newsRenderer import NewsRenderer

from .patch import PatchingWorker
from .enums import *


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
        if self.USA.isChecked():
            ExpressPatchingPage.region = Regions.USA
            return True
        elif self.PAL.isChecked():
            ExpressPatchingPage.region = Regions.PAL
            return True
        elif self.Japan.isChecked():
            ExpressPatchingPage.region = Regions.Japan
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
        if self.Yes.isChecked():
            ExpressPatchingPage.regional_channels = True
            return True
        elif self.No.isChecked():
            ExpressPatchingPage.regional_channels = False
            ExpressPatchingPage.wii_room_language = Languages.Japan
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
        if self.Translated.isChecked():
            ExpressPatchingPage.translated = True
            return True
        elif self.Japanese.isChecked():
            ExpressPatchingPage.translated = False
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

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle(self.tr("Step 2B: Express Setup"))
        self.setSubTitle(self.tr("Choose the language for Wii Room."))

        self.label = QLabel(self.tr("What language would you like <b>Wii Room</b> to be in?"))

        self.English = QRadioButton(self.tr("English"))
        self.Spanish = QRadioButton(self.tr("Español"))
        self.French = QRadioButton(self.tr("Français"))
        self.German = QRadioButton(self.tr("Deutsch"))
        self.Italian = QRadioButton(self.tr("Italiano"))
        self.Dutch = QRadioButton(self.tr("Nederlands"))
        self.Portuguese = QRadioButton(self.tr("Português (Brasil)"))
        self.Russian = QRadioButton(self.tr("Русский"))

        self.languages = [self.English, self.Spanish, self.French, self.German, self.Italian, self.Dutch,
                          self.Portuguese, self.Russian]

        self.buttonGroup = QButtonGroup(self)
        for button in self.languages:
            self.buttonGroup.addButton(button)

        layout = QVBoxLayout()
        layout.addWidget(self.label)
        for button in self.languages:
            layout.addWidget(button)

        self.setLayout(layout)

        for button in self.languages:
            button.toggled.connect(lambda: self.completeChanged.emit())

        self.Russian.clicked.connect(lambda: self.russian_notice())

    def isComplete(self):
        """Enable Next button only if a radio button is selected"""
        if self.English.isChecked():
            ExpressPatchingPage.wii_room_language = Languages.English
            return True
        elif self.Spanish.isChecked():
            ExpressPatchingPage.wii_room_language = Languages.Spanish
            return True
        elif self.French.isChecked():
            ExpressPatchingPage.wii_room_language = Languages.French
            return True
        elif self.German.isChecked():
            ExpressPatchingPage.wii_room_language = Languages.German
            return True
        elif self.Italian.isChecked():
            ExpressPatchingPage.wii_room_language = Languages.Italian
            return True
        elif self.Dutch.isChecked():
            ExpressPatchingPage.wii_room_language = Languages.Dutch
            return True
        elif self.Portuguese.isChecked():
            ExpressPatchingPage.wii_room_language = Languages.Portuguese
            return True
        elif self.Russian.isChecked():
            ExpressPatchingPage.wii_room_language = Languages.Russian
            return True
        return False

    def russian_notice(self):
        if self.Russian.isChecked:
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
        if self.Standard.isChecked():
            ExpressPatchingPage.demae_config = DemaeConfigs.Standard
            return True
        elif self.Dominos.isChecked():
            ExpressPatchingPage.demae_config = DemaeConfigs.Dominos
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

        self.Wii.toggled.connect(lambda: self.completeChanged.emit())
        self.vWii.toggled.connect(lambda: self.completeChanged.emit())
        self.Dolphin.toggled.connect(lambda: self.completeChanged.emit())

    def isComplete(self):
        if self.Wii.isChecked():
            ExpressPatchingPage.platform = Platforms.Wii
            return True
        elif self.vWii.isChecked():
            ExpressPatchingPage.platform = Platforms.vWii
            return True
        elif self.Dolphin.isChecked():
            ExpressPatchingPage.platform = Platforms.Dolphin
            return True
        return False


class ExpressPatchingPage(QWizardPage):
    platform: Platforms
    region: Regions
    regional_channels: bool
    wii_room_language = Languages.Japan
    demae_config: DemaeConfigs = DemaeConfigs.Standard
    translated: bool = False

    patching_complete = False
    percentage: int
    status: str

    def __init__(self, parent=None):
        super().__init__(parent)
    
        self.setTitle(self.tr("Patching in progress"))
        self.setSubTitle(self.tr("Please wait while the patcher works its magic!"))
    
        self.label = QLabel(self.tr("Downloading files..."))
        self.progress_bar = QProgressBar(self)
    
        self.news_box = NewsRenderer.createNewsBox(self)
    
        layout = QVBoxLayout()
        layout.addWidget(self.label)
        layout.addWidget(self.progress_bar)
        layout.addSpacing(10)
        layout.addWidget(self.news_box)
    
        self.setLayout(layout)
        
        QTimer.singleShot(0, lambda: NewsRenderer.getNews(self, self.news_box))


    def initializePage(self):
        QTimer.singleShot(0, self.disable_back_button)

        # Start thread to perform patching
        self.logic_thread = QThread()
        self.logic_worker = PatchingWorker()

        # Setup variables
        self.logic_worker.platform = self.platform
        self.logic_worker.region = self.region
        self.logic_worker.regional_channels = self.regional_channels
        self.logic_worker.setup_type = SetupTypes.Express

        match self.region:
            case Regions.USA:
                short_region = "us"
            case Regions.PAL:
                short_region = "eu"
            case Regions.Japan:
                short_region = "jp"
        
        match self.wii_room_language:
            case Languages.Japan:
                wiiroom_lang = "jp"
            case Languages.English:
                wiiroom_lang = "en"
            case Languages.Spanish:
                wiiroom_lang = "es"
            case Languages.French:
                wiiroom_lang = "fr"
            case Languages.German:
                wiiroom_lang = "de"
            case Languages.Italian:
                wiiroom_lang = "it"
            case Languages.Dutch:
                wiiroom_lang = "nl"
            case Languages.Portuguese:
                wiiroom_lang = "ptbr"
            case Languages.Russian:
                wiiroom_lang = "ru"
        
        if self.translated:
            regional_lang = "en"
        else:
            regional_lang = "jp"
        
        match self.demae_config:
            case DemaeConfigs.Standard:
                demae = f"food_{regional_lang}"
            case DemaeConfigs.Dominos:
                demae = "dominos"
        
        selected_channels = [
            "download",
            f"nc_{short_region}",
            f"forecast_{short_region}",
            f"news_{short_region}",
            f"evc_{short_region}",
            f"cmoc_{short_region}"
        ]

        if self.regional_channels:
            selected_channels.extend([
                f"wiiroom_{wiiroom_lang}",
                f"digicam_{regional_lang}",
                demae,
                "ktv"
            ])
        
        self.logic_worker.selected_channels = selected_channels

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