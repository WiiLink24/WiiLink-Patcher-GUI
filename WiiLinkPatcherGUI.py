# Nuitka options. These determine compilation settings based on the current OS.
# nuitka-project-if: {OS} == "Darwin":
#    nuitka-project: --standalone
#    nuitka-project: --macos-create-app-bundle
#    nuitka-project: --macos-app-icon={MAIN_DIRECTORY}/assets/logo.webp
# nuitka-project-if: {OS} == "Windows":
#    nuitka-project: --onefile
#    nuitka-project: --windows-icon-from-ico={MAIN_DIRECTORY}/assets/logo.webp
#    nuitka-project: --windows-console-mode=disable
# nuitka-project-if: {OS} in ("Linux", "FreeBSD", "OpenBSD"):
#    nuitka-project: --onefile

# These are standard options that are needed on all platforms.
# nuitka-project: --plugin-enable=pyside6
# nuitka-project: --include-data-dir={MAIN_DIRECTORY}/assets=assets
# nuitka-project: --include-data-file={MAIN_DIRECTORY}/style.qss=style.qss

import os
import pathlib
import shutil
import subprocess
import sys
import tempfile
import webbrowser

from PySide6.QtCore import QTranslator, QLocale, QLibraryInfo, QTimer, Qt
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (
    QWizard,
    QApplication,
    QWizardPage,
    QVBoxLayout,
    QRadioButton,
    QLabel,
    QPushButton,
    QMessageBox,
    QWidget,
)

from setup.custom import (
    CustomWiiConnect24Channels,
    CustomRegionalChannels,
    CustomPlatformConfiguration,
    CustomRegionConfiguration,
)
from setup.enums import Platforms, SetupTypes
from setup.express import (
    ExpressRegion,
    ExpressRegionalChannels,
    ExpressRegionalChannelTranslation,
    ExpressRegionalChannelLanguage,
    ExpressDemaeConfiguration,
    ExpressPlatformConfiguration,
)
from setup.extras import (
    ExtrasSystemChannelRestorer,
    MinimalExtraChannels,
    FullExtraChannels,
    ExtrasPlatformConfiguration,
    ExtrasRegionConfiguration,
)
from setup.download import (
    connection_test,
    download_translation_dict,
    download_translation,
    get_latest_version,
)
from setup.patch import PatchingPage
from setup.sd import AskSD, SelectSD, WADCleanup, FileCopying

patcher_url = "https://patcher.wiilink24.com"
temp_dir = pathlib.Path(tempfile.gettempdir()).joinpath("WiiLinkPatcher")
wiilink_dir = pathlib.Path().joinpath("WiiLink")
patcher_version = "1.0"


class IntroPage(QWizardPage):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle(self.tr("Welcome to the WiiLink Patcher!"))
        self.setSubTitle(
            self.tr(
                "This tool will walk you through downloading the necessary files to install WiiLink."
            )
        )

        self.label = QLabel(
            self.tr(
                """Welcome to the WiiLink Patcher!
                            
With this tool, you'll be able to get patched files to install WiiLink in no time!

Press 'Next' to get started!"""
            )
        )
        self.label.setWordWrap(True)

        self.layout = QVBoxLayout()

        self.layout.addWidget(self.label)

        self.setLayout(self.layout)


class MainMenu(QWizardPage):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.about_window = About()

        self.setTitle(self.tr("Choose what you'd like to do!"))
        self.setSubTitle(
            self.tr("We recommend choosing 'Express Setup' for first-time users.")
        )

        self.options = {
            "express_setup": QRadioButton(
                self.tr(
                    "Express Setup (Recommended)\nThe fastest way to get started with WiiLink"
                )
            ),
            "custom_setup": QRadioButton(
                self.tr("Custom Setup (Advanced)\nCustomize your WiiLink installation")
            ),
            "extra_channels": QRadioButton(
                self.tr(
                    "Extra Channels (Optional)\nAdd additional channels to your Wii"
                )
            ),
            "about": QPushButton(self.tr("About WiiLink Patcher")),
        }

        self.layout = QVBoxLayout()
        self.layout.setSpacing(10)
        self.layout.setContentsMargins(20, 20, 20, 20)

        # Add checkboxes to layout
        for button in self.options.values():
            self.layout.addWidget(button)
            button.clicked.connect(self.completeChanged.emit)

        # Select the first option
        next(iter(self.options.values())).setChecked(True)

        self.options["about"].clicked.connect(self.show_about)

        self.setLayout(self.layout)

    def validatePage(self):
        if self.options["express_setup"].isChecked():
            PatchingPage.setup_type = SetupTypes.Express
        elif self.options["custom_setup"].isChecked():
            PatchingPage.setup_type = SetupTypes.Custom
        elif self.options["extra_channels"].isChecked():
            PatchingPage.setup_type = SetupTypes.Extras

        return True

    def isComplete(self):
        """Enable Next button only if a radio button is selected"""
        for button in self.options.values():
            if button.isChecked():
                return True

        return False

    def nextId(self):
        """Determine which page to navigate to based on radio button selection"""
        if self.options["express_setup"].isChecked():
            return 100  # Start Express Setup
        elif self.options["custom_setup"].isChecked():
            return 200
        elif self.options["extra_channels"].isChecked():
            return 300
        return 0  # Stay on the same page if nothing is selected

    def show_about(self):
        self.about_window.show()


class About(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle(self.tr("WiiLink Patcher - About"))
        self.setFixedWidth(450)
        self.setFixedHeight(500)

        # Set background color to match main app
        stylesheet = open(
            os.path.join(os.path.dirname(__file__), "style.qss"), "r"
        ).read()
        self.setStyleSheet(stylesheet)

        # Create main layout
        self.layout = QVBoxLayout()
        self.layout.setSpacing(4)
        self.layout.setContentsMargins(30, 20, 30, 20)

        # Logo
        logo_label = QLabel()
        icon = QIcon(os.path.join(os.path.dirname(__file__), "assets", "logo.webp"))
        logo_pixmap = icon.pixmap(96, 96)
        logo_label.setPixmap(logo_pixmap)
        logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Title
        title_label = QLabel(self.tr("WiiLink Patcher"))
        title_label.setProperty("class", "title")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Version
        global patcher_version

        version_label = QLabel(self.tr(f"GUI - Version {patcher_version}"))
        version_label.setProperty("class", "version")
        version_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Copyright
        copyright_label = QLabel(
            self.tr("© 2020-2025 WiiLink Team. All rights reserved.")
        )
        copyright_label.setProperty("class", "copyright")
        copyright_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Add header section
        self.layout.addWidget(logo_label)
        self.layout.addWidget(title_label)
        self.layout.addWidget(version_label)
        self.layout.addWidget(copyright_label)
        self.layout.addSpacing(15)

        # External links layout
        links_layout = QVBoxLayout()

        # Website button
        self.website_button = QPushButton(self.tr("Visit WiiLink Website"))
        self.website_button.clicked.connect(
            lambda: webbrowser.open("https://wiilink.ca")
        )
        links_layout.addWidget(self.website_button)

        # GitHub button
        self.github_button = QPushButton(self.tr("View Project on GitHub"))
        self.github_button.clicked.connect(
            lambda: webbrowser.open("https://github.com/WiiLink24")
        )
        links_layout.addWidget(self.github_button)

        # Add the links layout to main layout
        self.layout.addLayout(links_layout)
        self.layout.addSpacing(15)

        # Add a horizontal line
        line = QLabel()
        line.setStyleSheet("background-color: #444444; height: 1px;")
        line.setFixedHeight(1)
        self.layout.addWidget(line)
        self.layout.addSpacing(10)

        # Team members header
        team_header = QLabel(self.tr("WiiLink Team"))
        team_header.setProperty("class", "header")
        self.layout.addWidget(team_header)
        self.layout.addSpacing(5)

        # Team members with roles
        self.people = {
            "sketch": QLabel(
                self.tr(
                    "<a href=https://noahpistilli.ca style='color: #4a86e8; text-decoration: none;'><b>Sketch</b></a> - WiiLink Project Lead"
                )
            ),
            "isla": QLabel(
                self.tr(
                    "<a href=https://islawalker.uk style='color: #4a86e8; text-decoration: none;'><b>Isla</b></a> - WiiLink Patcher GUI Developer"
                )
            ),
            "pablo": QLabel(
                self.tr(
                    "<a href=https://github.com/pabloscorner style='color: #4a86e8; text-decoration: none;'><b>PablosCorner</b></a> - WiiLink Patcher CLI Developer"
                )
            ),
            "alex": QLabel(
                self.tr(
                    "<a href=https://github.com/humanoidear style='color: #4a86e8; text-decoration: none;'><b>Alex</b></a> - WiiLink Design Lead"
                )
            ),
            "ninjacheetah": QLabel(
                self.tr(
                    "<a href=https://ninjacheetah.dev style='color: #4a86e8; text-decoration: none;'><b>NinjaCheetah</b></a> - libWiiPy Developer"
                )
            ),
        }

        # Add team members to layout
        for credit in self.people.values():
            credit.setOpenExternalLinks(True)
            credit.setContentsMargins(15, 0, 0, 0)
            self.layout.addWidget(credit)

        # Add spacer at the bottom
        self.layout.addStretch()

        self.setLayout(self.layout)


class WiiLinkFolderDetected(QWizardPage):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setTitle(self.tr("WiiLink folder detected!"))
        self.setSubTitle(
            self.tr(
                "A directory called 'WiiLink' has been found in the current directory."
            )
        )

        self.label = QLabel(
            self.tr(
                """The patcher has detected a directory called 'WiiLink' in your current directory.
The patcher uses the 'WiiLink' directory to store its files, therefore this
directory causes a conflict.

What would you like to do?"""
            )
        )

        self.options = {
            "rename": QRadioButton(
                self.tr(
                    "Rename the existing 'WiiLink' directory to 'WiiLink.bak'\n(Recommended)"
                )
            ),
            "delete": QRadioButton(self.tr("Delete the existing 'WiiLink' directory")),
            "leave": QRadioButton(
                self.tr("Leave the existing 'WiiLink' directory as-is\nNOT RECOMMENDED")
            ),
        }

        self.layout = QVBoxLayout()
        self.layout.setSpacing(10)
        self.layout.setContentsMargins(20, 20, 20, 20)

        self.layout.addWidget(self.label)

        # Add radio buttons to layout
        for button in self.options.values():
            self.layout.addWidget(button)
            button.clicked.connect(self.completeChanged.emit)

        # Select the first option
        next(iter(self.options.values())).setChecked(True)

        self.setLayout(self.layout)

    def validatePage(self):
        if self.options["rename"].isChecked():
            try:
                os.rename("WiiLink", "WiiLink.bak")
            except (OSError, FileExistsError):
                i = 1
                while True:
                    try:
                        os.rename("WiiLink", f"WiiLink.bak ({i})")
                    except (OSError, FileExistsError):
                        i += 1
                        continue
                    else:
                        break
        elif self.options["delete"].isChecked():
            shutil.rmtree("WiiLink")
        return True

    def isComplete(self):
        """Enable Next button only if a radio button is selected"""
        for button in self.options.values():
            if button.isChecked():
                return True

        return False


class PatchingComplete(QWizardPage):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setFinalPage(True)
        self.completeChanged.emit()

        self.setTitle(self.tr("Success!"))
        self.setSubTitle(self.tr("Everything has been patched successfully"))

        # Create a container with rounded corners and slightly lighter background
        self.container = QWidget()
        self.container.setFixedHeight(400)
        self.container.setStyleSheet(
            """
            background-color: #2a2a2a;
            border-radius: 12px;
            padding: 15px;
        """
        )

        # Container layout
        container_layout = QVBoxLayout(self.container)
        container_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        container_layout.setContentsMargins(15, 15, 15, 15)
        container_layout.setSpacing(5)  # Reduced spacing between elements

        # Party popper emoji
        emoji_label = QLabel("🎉")
        emoji_label.setStyleSheet("font-size: 64px; background-color: transparent;")
        emoji_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Heading
        heading = QLabel("<h1>Patching completed!</h1>")
        heading.setStyleSheet("background-color: transparent; color: white; margin: 0;")
        heading.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Message with file path
        self.message = QLabel(
            self.tr(
                f"<p>You can find the relevant files by clicking the button below. Please open a support ticket on our <a href='https://discord.gg/wiilink' style='color: #4a86e8; text-decoration: none;'>Discord server</a> if you have any issues.</p>"
            )
        )
        self.message.setStyleSheet(
            "background-color: transparent; color: white; margin: 0;"
        )
        self.message.setTextFormat(Qt.TextFormat.RichText)
        self.message.setWordWrap(True)
        self.message.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.message.setOpenExternalLinks(True)

        # Open folder button
        self.open_folder = QPushButton(self.tr("Open the 'WiiLink' folder"))
        self.open_folder.clicked.connect(self.open_wiilink_folder)

        # Add widgets to container
        container_layout.addWidget(emoji_label)
        container_layout.addWidget(heading)
        container_layout.addWidget(self.message)
        container_layout.addSpacing(5)  # Reduced spacing
        container_layout.addWidget(self.open_folder)

        # Main layout
        self.layout = QVBoxLayout()
        self.layout.addWidget(self.container)
        self.setLayout(self.layout)

    def initializePage(self):
        match PatchingPage.setup_type:
            case SetupTypes.Extras:
                if PatchingPage.platform != Platforms.Dolphin:
                    open_guide = QPushButton(
                        self.tr("Open the WAD installation guide in your web browser")
                    )
                    self.layout.addWidget(open_guide)
                    open_guide.clicked.connect(self.open_guide_link)
            case _:
                open_guide = QPushButton(
                    self.tr("Open the WiiLink installation guide in your web browser")
                )
                self.layout.addWidget(open_guide)
                open_guide.clicked.connect(self.open_guide_link)

        self.setLayout(self.layout)

        QTimer.singleShot(0, self.disable_buttons)

    @staticmethod
    def open_guide_link():

        guide_url = "https://wiilink.ca/guide"
        match PatchingPage.setup_type:
            case SetupTypes.Extras:
                guide_url = "https://wii.hacks.guide/yawmme"
            case _:
                match PatchingPage.platform:
                    case Platforms.Wii:
                        guide_url = f"{guide_url}/wii/#section-ii---installing-wads-and-patching-wii-mail"
                    case Platforms.vWii:
                        guide_url = f"{guide_url}/vwii/#section-iii---installing-wads-and-patching-wii-mail"
                    case Platforms.Dolphin:
                        guide_url = f"{guide_url}/dolphin/#section-ii---installing-wads"

        webbrowser.open(guide_url)

    @staticmethod
    def open_wiilink_folder():
        if sys.platform == "win32":
            os.startfile(wiilink_dir)
        elif sys.platform == "darwin":
            subprocess.Popen(["open", wiilink_dir])
        else:
            try:
                subprocess.Popen(["xdg-open", wiilink_dir])
            except OSError:
                print("Unable to launch file browser with xdg-open!")

    def disable_buttons(self):
        self.wizard().button(QWizard.WizardButton.BackButton).setEnabled(False)
        self.wizard().button(QWizard.WizardButton.CancelButton).setEnabled(False)


def main():
    if temp_dir.exists():
        shutil.rmtree(temp_dir)

    app = QApplication(sys.argv)

    wizard = QWizard()
    wizard.setWindowTitle(app.tr("WiiLink Patcher"))
    wizard.setWizardStyle(QWizard.WizardStyle.ModernStyle)
    wizard.setSubTitleFormat(Qt.TextFormat.RichText)

    icon = QIcon(os.path.join(os.path.dirname(__file__), "assets", "logo.webp"))
    background = QIcon(
        os.path.join(os.path.dirname(__file__), "assets", "background.webp")
    )
    logo = icon.pixmap(64, 64)
    banner = background.pixmap(700, 120)
    wizard.setPixmap(QWizard.WizardPixmap.LogoPixmap, logo)
    wizard.setPixmap(QWizard.WizardPixmap.BannerPixmap, banner)

    app.setWindowIcon(icon)

    # Apply global stylesheet for consistent styling across all pages
    stylesheet = open(os.path.join(os.path.dirname(__file__), "style.qss"), "r").read()
    stylesheet = stylesheet.replace(
        "assets", os.path.join(os.path.dirname(__file__), "assets")
    )
    wizard.setStyleSheet(stylesheet)

    wizard.setButtonText(QWizard.WizardButton.NextButton, "Next")
    wizard.setButtonText(QWizard.WizardButton.BackButton, "Back")

    try:
        connection = connection_test()
    except Exception as e:
        connection = e

    if connection != "success":
        match connection:
            case "fail-nus":
                error_message = (
                    "The patcher failed to connect to Nintendo's update servers."
                )
            case "fail-patcher":
                error_message = "The patcher failed to connect to WiiLink's servers."
            case _:
                error_message = f"""The patcher failed to connect to the internet.

Exception:
{connection}"""

        QMessageBox.critical(QWidget(), "WiiLink Patcher - Error", error_message)
        sys.exit()

    try:
        latest_version = get_latest_version()
    except Exception as e:
        QMessageBox.warning(
            QWidget(),
            "WiiLink Patcher - Warning",
            f"""Unable to check for updates!
Exception:
{e}""",
        )
    else:
        if latest_version != patcher_version:
            update = QMessageBox.question(
                QWidget(),
                "WiiLink Patcher - Update",
                f"""An update has been detected for the patcher, would you like to download it?

Your version: {patcher_version}
Latest version: {latest_version}""",
            )
            if update == QMessageBox.StandardButton.Yes:
                webbrowser.open(
                    "https://github.com/WiiLink24/WiiLink-Patcher-GUI/releases/latest"
                )
                sys.exit()

    language = QLocale.languageToCode(QLocale.system().language())
    supported_languages = download_translation_dict()

    if supported_languages is False:
        QMessageBox.warning(
            QWidget(),
            "WiiLink Patcher - Warning",
            "The patcher failed to download the list of languages. Therefore, it will run in English.",
        )
    else:
        if language in supported_languages:
            if download_translation(language) is False:
                QMessageBox.warning(
                    QWidget(),
                    "WiiLink Patcher - Warning",
                    "The patcher failed to download translations for your language. Therefore, it will run in English",
                )

    path = QLibraryInfo.path(QLibraryInfo.LibraryPath.TranslationsPath)
    translator = QTranslator(app)
    if translator.load(QLocale.system(), "qtbase", "_", path):
        app.installTranslator(translator)
    translator = QTranslator(app)
    path = os.path.join(os.path.dirname(__file__), "translations")
    if translator.load(QLocale.system(), "translation", "_", path):
        app.installTranslator(translator)

    wizard.setPage(0, IntroPage())
    wizard.setPage(1, MainMenu())

    wizard.setPage(10, WiiLinkFolderDetected())
    wizard.setPage(11, PatchingPage())
    wizard.setPage(12, AskSD())
    wizard.setPage(13, SelectSD())
    wizard.setPage(14, WADCleanup())
    wizard.setPage(15, FileCopying())

    wizard.setPage(100, ExpressRegion())
    wizard.setPage(101, ExpressRegionalChannels())
    wizard.setPage(102, ExpressRegionalChannelTranslation())
    wizard.setPage(103, ExpressRegionalChannelLanguage())
    wizard.setPage(104, ExpressDemaeConfiguration())
    wizard.setPage(105, ExpressPlatformConfiguration())

    wizard.setPage(200, CustomWiiConnect24Channels())
    wizard.setPage(201, CustomRegionalChannels())
    wizard.setPage(202, CustomPlatformConfiguration())
    wizard.setPage(203, CustomRegionConfiguration())

    wizard.setPage(300, ExtrasSystemChannelRestorer())
    wizard.setPage(301, MinimalExtraChannels())
    wizard.setPage(302, FullExtraChannels())
    wizard.setPage(303, ExtrasPlatformConfiguration())
    wizard.setPage(304, ExtrasRegionConfiguration())

    wizard.setPage(1000, PatchingComplete())

    wizard.setStartId(0)

    wizard.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
