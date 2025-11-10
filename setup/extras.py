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

from .enums import *
from .patch import PatchingPage
from modules.widgets import CollapsibleBox
from modules.consts import wiilink_dir


class ExtrasChannelSelection(QWizardPage):
    checkboxes = {}

    def __init__(self, patches_json: dict, parent=None):
        self.categories = []
        for category in patches_json:
            if category["type"] == "extra":
                self.categories.append(category)

        super().__init__(parent)
        self.setTitle(self.tr("Step 1: Extras Setup"))
        self.setSubTitle(self.tr("Select the extra channels you want to install"))

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

        container_layout.addStretch()
        scroll_area.setWidget(container)

        layout = QVBoxLayout()

        layout.addWidget(self.label)
        layout.addWidget(scroll_area)

        self.setLayout(layout)

    def validatePage(self):
        selected_extra_channels = []

        for channel, checkbox in self.checkboxes.items():
            if checkbox.isChecked():
                selected_extra_channels.append(channel)

        PatchingPage.selected_channels = selected_extra_channels

        return True

    def isComplete(self):
        for checkbox in self.checkboxes.values():
            if checkbox.isChecked():
                return True

        return False


class ExtrasPlatformConfiguration(QWizardPage):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle(self.tr("Step 2: Extras Setup"))
        self.setSubTitle(self.tr("Choose console platform."))

        self.label = QLabel(
            self.tr("Which platform will you be installing the channels onto?")
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


class ExtrasRegionConfiguration(QWizardPage):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle(self.tr("Step 3: Extras Setup"))
        self.setSubTitle(self.tr("Choose console region."))

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
