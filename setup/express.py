import pathlib

from PySide6.QtWidgets import (
    QWizardPage,
    QLabel,
    QVBoxLayout,
    QRadioButton,
    QMessageBox,
    QCheckBox,
)

from .patch import PatchingPage
from .enums import *
from modules.consts import wiilink_dir


class ExpressLanguage(QWizardPage):
    languages = {
        Languages.English: "English",
        Languages.Spanish: "español",
        Languages.French: "français",
        Languages.German: "Deutsch",
        Languages.Italian: "italiano",
        Languages.Dutch: "Nederlands",
        Languages.Portuguese: "português brasileiro",
        Languages.Russian: "русский",
        Languages.Japanese: "日本語",
    }

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle(self.tr("Step 1: Express Setup"))
        self.setSubTitle(self.tr("Choose the language for your installation."))

        self.label = QLabel(
            self.tr("What language would you like to use the channels in?")
        )
        self.label.setWordWrap(True)

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

        self.buttons[Languages.Russian].clicked.connect(self.russian_notice)

    def russian_notice(self):
        QMessageBox.warning(
            self,
            self.tr("Russian notice for Wii Room"),
            self.tr(
                """You have selected the Russian translation for Wii Room<br>
Proper functionality is not guaranteed for systems without the Russian Wii Menu.<br>
Follow the installation guide at <a href='https://wii.zazios.ru/rus_menu'>https://wii.zazios.ru/rus_menu</a> if you have not already done so.<br>
(The guide is only available in Russian for now)"""
            ),
        )

    def nextId(self):
        match self.wizard().property("language"):
            case Languages.English | Languages.Japanese:
                return 102
            case _:
                return 101

    def validatePage(self):
        for key, button in self.buttons.items():
            if button.isChecked():
                self.wizard().setProperty("language", key)

                match key:
                    case Languages.Portuguese | Languages.Russian:
                        self.wizard().setProperty("custom_language", True)
                    case Languages.English | Languages.Japanese:
                        self.wizard().setProperty("custom_language", False)
                        self.wizard().setProperty("secondary_language", key)
                    case _:
                        self.wizard().setProperty("custom_language", False)

                return True

        return False


class ExpressSecondaryLanguage(QWizardPage):
    languages = {
        Languages.English: "English",
        Languages.Japanese: "日本語",
    }

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle(self.tr("Step 1A: Express Setup"))
        self.setSubTitle(self.tr("Choose a secondary language for your installation."))

        self.label = QLabel(
            self.tr(
                "Not all channels are available in the language you selected. For these channels, what language would you like to use?"
            )
        )
        self.label.setWordWrap(True)

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

    def validatePage(self):
        for key, button in self.buttons.items():
            if button.isChecked():
                self.wizard().setProperty("secondary_language", key)
                return True

        return False


class ExpressRegion(QWizardPage):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle(self.tr("Step 2: Express Setup"))
        self.setSubTitle(self.tr("Choose your region for WiiConnect24 services."))

        self.label = QLabel(
            self.tr(
                "For the WiiConnect24 services, which region would you like to install?"
            )
        )
        self.label.setWordWrap(True)

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


class ExpressWiiConnect24Channels(QWizardPage):
    checkboxes = {}

    def __init__(self, patches_json: dict, parent=None):
        self.patches_json = patches_json

        wc24_channels = []
        for channel in patches_json:
            if channel["type"] == "wc24":
                wc24_channels.append(channel)

        super().__init__(parent)
        self.setTitle(self.tr("Step 3: Express Setup"))
        self.setSubTitle(
            self.tr("Select the WiiConnect24 channels you want to install")
        )

        layout = QVBoxLayout()

        self.label = QLabel(
            self.tr(
                "Select the WiiConnect24 channels you'd like to install from the list below:"
            )
        )
        self.label.setWordWrap(True)
        layout.addWidget(self.label)

        for channel in wc24_channels:
            checkbox = QCheckBox(channel["name"])
            checkbox.setChecked(True)
            self.checkboxes[channel["category_id"]] = checkbox
            layout.addWidget(checkbox)

        self.setLayout(layout)

    def validatePage(self):
        selected_wc24_channels = []

        for channel, checkbox in self.checkboxes.items():
            if checkbox.isChecked():
                if self.wizard().property(
                    "custom_language"
                ) and self.find_custom_translation_id(channel):
                    selected_wc24_channels.append(
                        f"{channel}_{self.find_custom_translation_id(channel)}"
                    )
                else:
                    selected_wc24_channels.append(
                        f"{channel}_{self.find_region_id(channel)}"
                    )

        self.wizard().setProperty("wc24_channels", selected_wc24_channels)
        return True

    def find_region_id(self, channel: int):
        for category in self.patches_json:
            if category["category_id"] == channel:
                for variant in category["channels"]:
                    if variant["region"] == PatchingPage.region.name:
                        return variant["item_id"]

        raise KeyError(
            f"Channel {channel} has no variant for {PatchingPage.region.name}!"
        )

    def find_custom_translation_id(self, channel: int):
        for category in self.patches_json:
            if category["category_id"] == channel:
                for variant in category["channels"]:
                    if variant["language"] == self.wizard().property("language").name:
                        return variant["item_id"]

        return False


class ExpressRegionalChannels(QWizardPage):
    checkboxes = {}

    def __init__(self, patches_json: dict, parent=None):
        self.patches_json = patches_json

        regional_channels = []
        for channel in patches_json:
            if channel["type"] == "regional":
                regional_channels.append(channel)

        super().__init__(parent)
        self.setTitle(self.tr("Step 4: Express Setup"))
        self.setSubTitle(self.tr("Select the regional channels you want to install"))

        layout = QVBoxLayout()

        self.label = QLabel(
            self.tr(
                "Select the regional channels you'd like to install from the list below:"
            )
        )
        self.label.setWordWrap(True)
        layout.addWidget(self.label)

        for channel in regional_channels:
            checkbox = QCheckBox(channel["name"])
            checkbox.clicked.connect(self.completeChanged.emit)
            self.checkboxes[channel["category_id"]] = checkbox
            layout.addWidget(checkbox)

        self.setLayout(layout)

    def isComplete(self):
        if len(self.wizard().property("wc24_channels")) > 0:
            return True

        for checkbox in self.checkboxes.values():
            if checkbox.isChecked():
                return True

        return False

    def validatePage(self):
        selected_regional_channels = []
        PatchingPage.regional_channels = False

        for channel, checkbox in self.checkboxes.items():
            if checkbox.isChecked():
                if len(self.find_category(channel)["channels"]) == 1:
                    selected_regional_channels.append(f"{channel}_1")
                elif self.find_translation_id(channel):
                    selected_regional_channels.append(
                        f"{channel}_{self.find_translation_id(channel)}"
                    )
                else:
                    selected_regional_channels.append(
                        f"{channel}_{self.find_translation_id(channel, self.wizard().property("secondary_language"))}"
                    )

        if len(selected_regional_channels) > 0:
            PatchingPage.regional_channels = True

        PatchingPage.selected_channels = (
            self.wizard().property("wc24_channels") + selected_regional_channels
        )

        return True

    def find_category(self, category_id: int):
        for category in self.patches_json:
            if category["category_id"] == category_id:
                return category

        raise KeyError(f"Category {category_id} does not exist!")

    def find_translation_id(self, channel: int, language: Languages = None):
        if language is None:
            language = self.wizard().property("language")

        for category in self.patches_json:
            if category["category_id"] == channel:
                for variant in category["channels"]:
                    if variant["language"] == language.name:
                        return variant["item_id"]

        return False


class ExpressPlatformConfiguration(QWizardPage):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle(self.tr("Step 5: Express Setup"))
        self.setSubTitle(self.tr("Choose console platform."))

        self.label = QLabel(
            self.tr("Which platform will you be installing WiiLink onto?")
        )
        self.label.setWordWrap(True)

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

    def validatePage(self):
        for key, button in self.buttons.items():
            if button.isChecked():
                PatchingPage.platform = key
                return True

        return False

    def nextId(self):
        if wiilink_dir.exists():
            return 10

        return 11
