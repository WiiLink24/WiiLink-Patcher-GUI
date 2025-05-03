from PySide6.QtCore import QTimer, QObject, Signal, QThread
from PySide6.QtWidgets import QWizardPage, QLabel, QVBoxLayout, QRadioButton, QButtonGroup, QProgressBar, QWizard, QCheckBox

from .download import download_osc_app, download_spd
from .patch import nc_patch, forecast_patch, news_patch, evc_patch, cmoc_patch, wiiroom_patch,digicam_patch, demae_patch, kirbytv_patch
from .enums import *

selected_wc24_channels = []
selected_regional_channels = []


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
        global selected_regional_channels

        self.local_selected_channels = [
            key for key, checkbox in self.checkboxes.items() if checkbox.isChecked()
        ]
        selected_regional_channels = []
        for item in self.local_selected_channels:
            selected_regional_channels.append(item)

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
            CustomPatchingPage.platform = Platforms.Wii
            return True
        elif self.vWii.isChecked():
            CustomPatchingPage.platform = Platforms.vWii
            return True
        elif self.Dolphin.isChecked():
            CustomPatchingPage.platform = Platforms.Dolphin
            return True
        return False


class CustomRegionConfiguration(QWizardPage):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle(self.tr("Step 4: Custom Setup"))
        self.setSubTitle(self.tr("Choose console region"))

        self.label = QLabel(self.tr("Which region is your console?"))

        self.USA = QRadioButton(self.tr("North America (NTSC-U)"))
        self.PAL = QRadioButton(self.tr("Europe (PAL)"))
        self.Japan = QRadioButton(self.tr("Japan (NTSC-J)"))

        self.buttonGroup = QButtonGroup(self)
        self.buttonGroup.addButton(self.USA)
        self.buttonGroup.addButton(self.PAL)
        self.buttonGroup.addButton(self.Japan)

        layout = QVBoxLayout()
        layout.addWidget(self.label)
        layout.addWidget(self.USA)
        layout.addWidget(self.PAL)
        layout.addWidget(self.Japan)

        self.setLayout(layout)

        self.USA.clicked.connect(self.completeChanged.emit)
        self.PAL.clicked.connect(self.completeChanged.emit)
        self.Japan.clicked.connect(self.completeChanged.emit)

    def isComplete(self):
        if self.USA.isChecked():
            CustomPatchingPage.region = Regions.USA
            return True
        elif self.PAL.isChecked():
            CustomPatchingPage.region = Regions.PAL
            return True
        elif self.Japan.isChecked():
            CustomPatchingPage.region = Regions.Japan
            return True
        return False


class CustomPatchingPage(QWizardPage):
    platform: Platforms
    region: Regions
    selected_channels: list
    regional_channels: bool = False

    patching_complete = False
    percentage: int
    status: str

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

        # Start thread to perform patching
        self.logic_thread = QThread()
        self.logic_worker = CustomPatchingLogic()

    def initializePage(self):
        QTimer.singleShot(0, self.disable_back_button)

        # Setup variables
        self.logic_worker.platform = self.platform
        self.logic_worker.region = self.region

        global selected_wc24_channels
        global selected_regional_channels

        if len(selected_regional_channels) > 0:
            self.logic_worker.regional_channels = True

        self.logic_worker.selected_channels = ["download"] + selected_wc24_channels + selected_regional_channels

        self.logic_worker.moveToThread(self.logic_thread)
        self.logic_thread.started.connect(self.logic_worker.patching_functions)

        self.logic_worker.broadcast_percentage.connect(self.set_percentage)
        self.logic_worker.broadcast_status.connect(self.set_status)

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


class CustomPatchingLogic(QObject):
    platform: Platforms
    region: Regions
    selected_channels: list
    regional_channels: bool = False
    is_patching_complete: bool
    finished = Signal(bool)
    broadcast_percentage = Signal(int)
    broadcast_status = Signal(str)

    def patching_functions(self):

        percentage_increment = 100 / len(self.selected_channels)

        percentage = 0

        patch_functions = {
            "download": lambda: self.download_supporting_apps(),
            "forecast_us": lambda: forecast_patch(Regions.USA, self.platform),
            "forecast_eu": lambda: forecast_patch(Regions.PAL, self.platform),
            "forecast_jp": lambda: forecast_patch(Regions.Japan, self.platform),
            "news_us": lambda: news_patch(Regions.USA),
            "news_eu": lambda: news_patch(Regions.PAL),
            "news_jp": lambda: news_patch(Regions.Japan),
            "nc_us": lambda: nc_patch(Regions.USA),
            "nc_eu": lambda: nc_patch(Regions.PAL),
            "nc_jp": lambda: nc_patch(Regions.Japan),
            "evc_us": lambda: evc_patch(Regions.USA),
            "evc_eu": lambda: evc_patch(Regions.PAL),
            "evc_jp": lambda: evc_patch(Regions.Japan),
            "cmoc_us": lambda: cmoc_patch(Regions.USA),
            "cmoc_eu": lambda: cmoc_patch(Regions.PAL),
            "cmoc_jp": lambda: cmoc_patch(Regions.Japan),
            "wiiroom_en": lambda: wiiroom_patch(Languages.English),
            "wiiroom_es": lambda: wiiroom_patch(Languages.Spanish),
            "wiiroom_fr": lambda: wiiroom_patch(Languages.French),
            "wiiroom_de": lambda: wiiroom_patch(Languages.German),
            "wiiroom_it": lambda: wiiroom_patch(Languages.Italian),
            "wiiroom_nl": lambda: wiiroom_patch(Languages.Dutch),
            "wiiroom_ptbr": lambda: wiiroom_patch(Languages.Portuguese),
            "wiiroom_ru": lambda: wiiroom_patch(Languages.Russian),
            "wiiroom_jp": lambda: wiiroom_patch(Languages.Japan),
            "digicam_en": lambda: digicam_patch(True),
            "digicam_jp": lambda: digicam_patch(False),
            "food_en": lambda: demae_patch(True, DemaeConfigs.Standard, self.region),
            "food_jp": lambda: demae_patch(False, DemaeConfigs.Standard, self.region),
            "dominos": lambda: demae_patch(True, DemaeConfigs.Dominos, self.region),
            "ktv": lambda: kirbytv_patch()
        }

        patch_status = {
            "download": self.tr("Downloading files..."),
            "forecast_us": self.tr("Patching Forecast Channel (USA)..."),
            "forecast_eu": self.tr("Patching Forecast Channel (PAL)..."),
            "forecast_jp": self.tr("Patching Forecast Channel (Japan)..."),
            "news_us": self.tr("Patching News Channel (USA)..."),
            "news_eu": self.tr("Patching News Channel (PAL)..."),
            "news_jp": self.tr("Patching News Channel (Japan)..."),
            "nc_us": self.tr("Patching Nintendo Channel (USA)..."),
            "nc_eu": self.tr("Patching Nintendo Channel (PAL)..."),
            "nc_jp": self.tr("Patching Nintendo Channel (Japan)..."),
            "evc_us": self.tr("Patching Everybody Votes Channel (USA)..."),
            "evc_eu": self.tr("Patching Everybody Votes Channel (PAL)..."),
            "evc_jp": self.tr("Patching Everybody Votes Channel (Japan)..."),
            "cmoc_us": self.tr("Patching Check Mii Out Channel (USA)..."),
            "cmoc_eu": self.tr("Patching Mii Contest Channel (PAL)..."),
            "cmoc_jp": self.tr("Patching Mii Contest Channel (Japan)..."),
            "wiiroom_en": self.tr("Patching Wii Room (English)..."),
            "wiiroom_es": self.tr("Patching Wii Room (Español)..."),
            "wiiroom_fr": self.tr("Patching Wii Room (Français)..."),
            "wiiroom_de": self.tr("Patching Wii Room (Deutsch)..."),
            "wiiroom_it": self.tr("Patching Wii Room (Italiano)..."),
            "wiiroom_nl": self.tr("Patching Wii Room (Nederlands)..."),
            "wiiroom_ptbr": self.tr("Patching Wii Room (Português (Brasil))..."),
            "wiiroom_ru": self.tr("Patching Wii Room (Русский)..."),
            "wiiroom_jp": self.tr("Patching Wii Room (Japanese)..."),
            "digicam_en": self.tr("Patching Photo Prints Channel (English)..."),
            "digicam_jp": self.tr("Patching Digicam Print Channel (Japanese)..."),
            "food_en": self.tr("Patching Food Channel (Standard) (English)..."),
            "food_jp": self.tr("Patching Demae Channel (Standard) (Japanese)..."),
            "dominos": self.tr("Patching Food Channel (Domino's) (English)..."),
            "ktv": self.tr("Patching Kirby TV Channel...")
        }

        for channel in self.selected_channels:
            self.broadcast_status.emit(patch_status[channel])
            patch_functions[channel]()
            percentage += percentage_increment
            self.broadcast_percentage.emit(round(percentage))


        self.finished.emit(True)

    def download_supporting_apps(self):
        if self.platform != Platforms.Dolphin:
            download_osc_app("yawmME")
            download_osc_app("sntp")

        if self.regional_channels:
            download_spd()

        download_osc_app("Mail-Patcher")