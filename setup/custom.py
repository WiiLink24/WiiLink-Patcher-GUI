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
    QMessageBox,
)

from .patch import PatchingPage
from .enums import *
from modules.widgets import CollapsibleBox
from modules.consts import wiilink_dir

selected_wc24_channels = []


class CustomWiiConnect24Channels(QWizardPage):
    checkboxes = {}

    def __init__(self, patches_json: dict, parent=None):
        self.categories = []
        for category in patches_json:
            if category["type"] == "wc24":
                self.categories.append(category)

        super().__init__(parent)
        self.setTitle(self.tr("Step 1: Custom Setup"))
        self.setSubTitle(
            self.tr("Select the WiiConnect24 channels you want to install")
        )

        self.label = QLabel(
            self.tr("Select the channels you'd like to install from the list below:")
        )
        self.label.setWordWrap(True)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFixedHeight(400)

        container = QWidget()
        container_layout = QVBoxLayout(container)
        container_layout.setContentsMargins(0, 0, 0, 0)
        container_layout.setSpacing(0)

        for category in self.categories:
            box = CollapsibleBox(title=category["name"])
            box.toggle_button.setSizePolicy(
                QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed
            )
            box.toggle_button.setMinimumWidth(0)
            for channel in category["channels"]:
                checkbox = QCheckBox(channel["name"])
                box.content_layout.addWidget(checkbox)
                self.checkboxes[f"{category["category_id"]}_{channel["item_id"]}"] = (
                    checkbox
                )
            container_layout.addWidget(box)

        container_layout.addStretch()
        scroll_area.setWidget(container)

        layout = QVBoxLayout()

        layout.addWidget(self.label)
        layout.addWidget(scroll_area)

        self.setLayout(layout)

    def validatePage(self):
        global selected_wc24_channels

        selected_wc24_channels = []

        for channel, checkbox in self.checkboxes.items():
            if checkbox.isChecked():
                selected_wc24_channels.append(channel)

        return True


class CustomRegionalChannels(QWizardPage):
    checkboxes = {}

    def __init__(self, patches_json: dict, parent=None):
        self.categories = []
        for category in patches_json:
            if category["type"] == "regional":
                self.categories.append(category)

        super().__init__(parent)
        self.setTitle(self.tr("Step 2: Custom Setup"))
        self.setSubTitle(self.tr("Select the regional channels you want to install"))

        self.label = QLabel(
            self.tr("Select the channels you'd like to install from the list below:")
        )
        self.label.setWordWrap(True)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFixedHeight(400)

        container = QWidget()
        container_layout = QVBoxLayout(container)
        container_layout.setContentsMargins(0, 0, 0, 0)
        container_layout.setSpacing(0)

        for category in self.categories:
            box = CollapsibleBox(title=category["name"])
            box.toggle_button.setSizePolicy(
                QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed
            )
            box.toggle_button.setMinimumWidth(0)
            for channel in category["channels"]:
                checkbox = QCheckBox(channel["name"])
                box.content_layout.addWidget(checkbox)
                self.checkboxes[f"{category["category_id"]}_{channel["item_id"]}"] = (
                    checkbox
                )
                checkbox.clicked.connect(self.completeChanged.emit)
            container_layout.addWidget(box)

        self.checkboxes["7_9"].clicked.connect(self.russian_notice)

        container_layout.addStretch()
        scroll_area.setWidget(container)

        layout = QVBoxLayout()

        layout.addWidget(self.label)
        layout.addWidget(scroll_area)

        self.setLayout(layout)

    def russian_notice(self):
        if self.checkboxes["7_9"].isChecked():
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

    def validatePage(self):
        global selected_wc24_channels

        selected_regional_channels = []

        for channel, checkbox in self.checkboxes.items():
            if checkbox.isChecked():
                selected_regional_channels.append(channel)

        if len(selected_regional_channels) > 0:
            PatchingPage.regional_channels = True

        PatchingPage.selected_channels = (
            selected_wc24_channels + selected_regional_channels
        )

        return True

    def isComplete(self):
        for checkbox in CustomWiiConnect24Channels.checkboxes.values():
            if checkbox.isChecked():
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

    def nextId(self):
        if wiilink_dir.exists():
            return 10

        return 11
