# Nuitka options. These determine compilation settings based on the current OS.
# nuitka-project-if: {OS} == "Darwin":
#    nuitka-project: --standalone
#    nuitka-project: --macos-create-app-bundle
#    nuitka-project: --macos-app-icon={MAIN_DIRECTORY}/assets/logo.webp
#    nuitka-project: --macos-app-version=1.4.0
#    nuitka-project: --include-data-dir={MAIN_DIRECTORY}/assets=assets
#    nuitka-project: --include-data-dir={MAIN_DIRECTORY}/data=data
#    nuitka-project: --include-data-file={MAIN_DIRECTORY}/style.qss=style.qss
#    nuitka-project: --include-data-file={MAIN_DIRECTORY}/translations/*.qm=translations/
#    nuitka-project: --include-data-file={MAIN_DIRECTORY}/translations/languages.json=translations/languages.json
# nuitka-project-if: {OS} != "Darwin":
#    nuitka-project: --include-data-dir={MAIN_DIRECTORY}/assets=WiiLinkPatcherGUI/assets
#    nuitka-project: --include-data-dir={MAIN_DIRECTORY}/data=WiiLinkPatcherGUI/data
#    nuitka-project: --include-data-file={MAIN_DIRECTORY}/style.qss=WiiLinkPatcherGUI/style.qss
#    nuitka-project: --include-data-file={MAIN_DIRECTORY}/translations/*.qm=WiiLinkPatcherGUI/translations/
#    nuitka-project: --include-data-file={MAIN_DIRECTORY}/translations/languages.json=WiiLinkPatcherGUI/translations/languages.json
# nuitka-project-if: {OS} == "Windows":
#    nuitka-project: --windows-icon-from-ico={MAIN_DIRECTORY}/assets/logo.webp
#    nuitka-project: --windows-console-mode=disable
# nuitka-project-if: {OS} in ("Linux", "FreeBSD", "OpenBSD"):
#    nuitka-project: --onefile

# These are standard options that are needed on all platforms.
# nuitka-project: --product-version=1.4.0
# nuitka-project: --copyright="© 2020-2026 WiiLink Team. All rights reserved."
# nuitka-project: --plugin-enable=pyside6
# nuitka-project: --include-package-data=PySide6:*.qm

import os
import pathlib
import shutil
import sys
import traceback
import random
import json
import datetime

from PySide6.QtCore import (
    QTranslator,
    QLocale,
    QLibraryInfo,
    QTimer,
    Qt,
    QStandardPaths,
    QUrl,
)
from PySide6.QtGui import QIcon, QDesktopServices
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
    QComboBox,
    QDialog,
    QSizePolicy,
    QLineEdit,
    QHBoxLayout,
    QFileDialog,
)

from WiiLinkPatcherGUI.modules.errors import error_handler
from WiiLinkPatcherGUI.setup.custom import (
    CustomWiiConnect24Channels,
    CustomRegionalChannels,
    CustomPlatformConfiguration,
    CustomRegionConfiguration,
)
from WiiLinkPatcherGUI.setup.enums import SetupTypes
from WiiLinkPatcherGUI.setup.express import (
    ExpressRegion,
    ExpressPlatformConfiguration,
    ExpressLanguage,
    ExpressSecondaryLanguage,
    ExpressWiiConnect24Channels,
    ExpressRegionalChannels,
)
from WiiLinkPatcherGUI.setup.extras import (
    ExtrasChannelSelection,
    ExtrasPlatformConfiguration,
    ExtrasRegionConfiguration,
)
from WiiLinkPatcherGUI.setup.dokodemo import (
    DokodemoSelectLanguage,
    DokodemoPatchingPage,
)
from WiiLinkPatcherGUI.setup.download import (
    connection_test,
    get_latest_version,
    DownloadOSCApp,
)
from WiiLinkPatcherGUI.setup.patch import PatchingPage
from WiiLinkPatcherGUI.modules.widgets import ClickableLabel
from WiiLinkPatcherGUI.modules.consts import (
    temp_dir,
    file_path,
    patcher_version,
)


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
            "dokodemo": QRadioButton(
                self.tr(
                    "Wii Room Anywhere\nPatch Dokodemo Wii no Ma to work with Wii Room"
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
        elif self.options["dokodemo"].isChecked():
            PatchingPage.setup_type = SetupTypes.Dokodemo

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
        elif self.options["dokodemo"].isChecked():
            return 400
        return 0  # Stay on the same page if nothing is selected

    def show_about(self):
        self.about_window.show()


class About(QWidget):
    clicks = 0

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle(self.tr("WiiLink Patcher - About"))
        self.setFixedWidth(450)
        self.setFixedHeight(550)

        # Set background color to match main app
        stylesheet = open(pathlib.Path().joinpath(file_path, "style.qss"), "r").read()
        stylesheet = stylesheet.replace(
            "%AssetsDir%",
            pathlib.Path(file_path).joinpath("assets").resolve().as_posix(),
        )
        self.setStyleSheet(stylesheet)

        # Create main layout
        self.layout = QVBoxLayout()
        self.layout.setSpacing(4)
        self.layout.setContentsMargins(30, 20, 30, 20)

        # Logo
        logo_label = ClickableLabel()
        icon = QIcon(
            pathlib.Path()
            .joinpath(file_path, "assets", "logo.webp")
            .resolve()
            .as_posix()
        )
        self.setWindowIcon(icon)

        logo_pixmap = icon.pixmap(96, 96)
        logo_label.setPixmap(logo_pixmap)
        logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        logo_label.clicked.connect(self.pride)

        # Title
        title_label = QLabel(self.tr("WiiLink Patcher"))
        title_label.setProperty("class", "title")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Version
        version_label = QLabel(self.tr("GUI - Version {}").format(patcher_version))
        version_label.setProperty("class", "version")
        version_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Copyright
        copyright_label = QLabel(
            self.tr("© 2020-{} WiiLink Team. All rights reserved.").format(
                datetime.datetime.now().year
            )
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
            lambda: QDesktopServices.openUrl("https://wiilink.ca")
        )
        links_layout.addWidget(self.website_button)

        # GitHub button
        self.github_button = QPushButton(self.tr("View Project on GitHub"))
        self.github_button.clicked.connect(
            lambda: QDesktopServices.openUrl("https://github.com/WiiLink24")
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
            "harry": QLabel(
                self.tr(
                    "<a href=https://harrywalker.uk style='color: #4a86e8; text-decoration: none;'><b>Harry</b></a> - WiiLink Patcher GUI Developer"
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

        translator = self.tr(
            "<a href=https://example.com style='color: #4a86e8; text-decoration: none;'><b>YOUR NAME</b></a> - LANGUAGE Translator"
        )

        if (
            translator
            != "<a href=https://example.com style='color: #4a86e8; text-decoration: none;'><b>YOUR NAME</b></a> - LANGUAGE Translator"
        ):
            translator_credit = QLabel(translator)
            translator_credit.setOpenExternalLinks(True)
            translator_credit.setContentsMargins(15, 0, 0, 0)
            self.layout.addWidget(translator_credit)

        # Add spacer at the bottom
        self.layout.addStretch()

        self.setLayout(self.layout)

    def pride(self):
        global wizard

        self.clicks += 1

        if self.clicks == 3:
            pride_flags = (
                pathlib.Path(file_path).joinpath("assets", "pride_banners").iterdir()
            )
            flags_list = list(pride_flags)

            print("making it gay :3")
            self.clicks = 0

            flag_index = random.randint(0, len(flags_list) - 1)
            selected_flag = flags_list[flag_index]

            pride = QIcon(str(selected_flag))
            pride_pixmap = pride.pixmap(700, 120)
            wizard.setPixmap(QWizard.WizardPixmap.BannerPixmap, pride_pixmap)
            wizard.setWindowTitle(self.tr("GayLink Patcher"))


class SelectOutputLocation(QWizardPage):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setTitle(self.tr("Select output location"))
        self.setSubTitle(self.tr("Choose where to store the files from the patcher."))

        label = QLabel(
            self.tr(
                """Finally, before we begin, you need to choose where to store the files from the patcher.

If you are using the Dolphin Emulator, we recommend creating a new folder on your PC.
Otherwise, we recommend selecting your SD card or USB drive that you use in your console."""
            )
        )

        label.setWordWrap(True)

        self.path = QLineEdit()
        self.path.setPlaceholderText(self.tr("Select a location..."))

        self.select = QPushButton(self.tr("Browse"))
        self.select.pressed.connect(self.select_folder)

        sublayout = QHBoxLayout()
        sublayout.addWidget(self.path)
        sublayout.addWidget(self.select)

        layout = QVBoxLayout()
        layout.addWidget(label)
        layout.addLayout(sublayout)

        self.setLayout(layout)

        self.dialog = QFileDialog()

        self.dialog.setDirectory(
            QStandardPaths.standardLocations(
                QStandardPaths.StandardLocation.HomeLocation
            )[0]
        )

    def select_folder(self):
        directory = self.dialog.getExistingDirectory(
            self,
            self.tr("Select output location..."),
        )

        self.path.setText(directory)
        self.completeChanged.emit()

    def validatePage(self):
        if pathlib.Path(self.path.text()).is_dir():
            selected_path = pathlib.Path(self.path.text())
            self.wizard().setProperty("path", selected_path)
            return True

        QMessageBox.warning(
            self,
            self.tr("Invalid location!"),
            self.tr("The location you have selected is invalid."),
        )
        return False

    def isComplete(self):
        return len(self.path.text()) > 0

    def nextId(self):
        wad_path = pathlib.Path(self.path.text()).joinpath("WAD")
        match PatchingPage.setup_type:
            case SetupTypes.Dokodemo:
                return 401
            case _:
                if wad_path.is_dir():
                    return 11
                return 12


class WADCleanup(QWizardPage):
    def __init__(self):
        super().__init__()
        self.setTitle(self.tr("WAD folder detected"))
        self.setSubTitle(self.tr("Choose what to do with existing WAD folder."))

        self.layout = QVBoxLayout()
        self.layout.setSpacing(10)
        self.layout.setContentsMargins(20, 20, 20, 20)

        self.label = QLabel(
            self.tr(
                """The patcher has detected a directory called 'WAD' in your selected output location.
The 'WAD' directory is used to store channels you install on your Wii, therefore this directory causes a conflict.

What would you like to do?"""
            )
        )
        self.label.setWordWrap(True)

        self.options = {
            "rename": QRadioButton(
                self.tr(
                    "Rename the existing 'WAD' directory to 'WAD.bak'\n(Recommended)"
                )
            ),
            "delete": QRadioButton(self.tr("Delete the existing 'WAD' directory")),
            "leave": QRadioButton(
                self.tr("Leave the existing 'WAD' directory as-is\nNOT RECOMMENDED")
            ),
        }

        self.layout.addWidget(self.label)

        # Add radio buttons to layout
        for button in self.options.values():
            self.layout.addWidget(button)
            button.clicked.connect(self.completeChanged.emit)

        # Select the first option
        next(iter(self.options.values())).setChecked(True)

        self.setLayout(self.layout)

    def handle_error(self, error: str):
        """Display errors thrown in manipulating folder to the user"""
        QMessageBox.critical(
            self,
            "WiiLink Patcher - Error",
            f"An exception was encountered while performing the operation you requested.<br><pre>{error}</pre><br>If you need help, head over to the WiiLink Discord Server (<a href='https://discord.gg/wiilink'>discord.gg/wiilink</a>).",
        )

    def validatePage(self):
        output_path = self.wizard().property("path")
        wad_path = output_path.joinpath("WAD")

        try:
            if self.options["rename"].isChecked():
                if pathlib.Path(output_path).joinpath("WAD.bak").exists():
                    i = 1
                    while pathlib.Path(output_path).joinpath(f"WAD.bak ({i})").exists():
                        i += 1
                    os.rename(
                        wad_path,
                        pathlib.Path(output_path).joinpath(f"WAD.bak ({i})"),
                    )
                else:
                    os.rename(wad_path, pathlib.Path(output_path).joinpath("WAD.bak"))

            elif self.options["delete"].isChecked():
                shutil.rmtree(wad_path)
        except Exception as e:
            print(traceback.format_exc())
            self.handle_error(error_handler(e))
            return False

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
        self.container.setStyleSheet("""
            background-color: #2a2a2a;
            border-radius: 12px;
            padding: 15px;
        """)

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
        heading = QLabel(self.tr("<h1>Patching completed!</h1>"))
        heading.setStyleSheet("background-color: transparent; color: white; margin: 0;")
        heading.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Message with file path
        self.message = QLabel(
            self.tr(
                """<p>You can find the relevant files by clicking the button below.
Please open a support ticket on our <a href='https://discord.gg/wiilink' style='color: #4a86e8; text-decoration: none;'>Discord server</a> if you have any issues.</p>"""
            )
        )
        self.message.setStyleSheet(
            "background-color: transparent; color: white; margin: 0;"
        )
        self.message.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
        )
        self.message.setTextFormat(Qt.TextFormat.RichText)
        self.message.setWordWrap(True)
        self.message.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.message.setOpenExternalLinks(True)

        # Open folder button
        self.open_folder = QPushButton(self.tr("See the files!"))
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

        open_guide = QPushButton(
            self.tr("Open the WiiLink installation guide in your web browser")
        )
        self.layout.addWidget(open_guide)
        open_guide.clicked.connect(self.open_guide_link)

        self.setLayout(self.layout)

    def initializePage(self):
        QTimer.singleShot(0, self.disable_buttons)

    @staticmethod
    def open_guide_link():
        QDesktopServices.openUrl("https://wiilink.ca/guide/wads")

    def open_wiilink_folder(self):
        output_path = self.wizard().property("path")
        QDesktopServices.openUrl(QUrl.fromLocalFile(output_path.resolve().as_posix()))
        # match sys.platform:
        #    case "win32":

    #         os.startfile(output_path)
    #      case "darwin":
    #           subprocess.Popen(["open", output_path])
    #        case _:
    #             try:
    #                  subprocess.Popen(["xdg-open", output_path])
    #               except OSError:
    #                    print("Unable to launch file browser with xdg-open!")

    def disable_buttons(self):
        self.wizard().button(QWizard.WizardButton.BackButton).setEnabled(False)
        self.wizard().button(QWizard.WizardButton.CancelButton).setEnabled(False)


class WiiLinkPatcherGUI(QWizard):
    language = QLocale("en")

    def __init__(self, parent=None):
        super().__init__(parent)

        # Load in icon and banner images
        icon = QIcon(
            pathlib.Path()
            .joinpath(file_path, "assets", "logo.webp")
            .resolve()
            .as_posix()
        )

        match datetime.datetime.now().month:
            case 6:
                pride_flags = (
                    pathlib.Path(file_path)
                    .joinpath("assets", "pride_banners")
                    .iterdir()
                )
                flags_list = list(pride_flags)

                flag_index = random.randint(0, len(flags_list) - 1)
                selected_flag = flags_list[flag_index]

                background = QIcon(selected_flag.resolve().as_posix())
            case _:
                background = QIcon(
                    pathlib.Path()
                    .joinpath(file_path, "assets", "background.webp")
                    .resolve()
                    .as_posix()
                )

        logo = icon.pixmap(64, 64)
        banner = background.pixmap(700, 120)
        self.setPixmap(QWizard.WizardPixmap.LogoPixmap, logo)
        self.setPixmap(QWizard.WizardPixmap.BannerPixmap, banner)

        self.setWindowIcon(icon)

        # Apply global stylesheet for consistent styling across all pages
        stylesheet_path = pathlib.Path().joinpath(file_path, "style.qss")
        stylesheet = open(stylesheet_path, "r").read()
        stylesheet = stylesheet.replace(
            "%AssetsDir%",
            pathlib.Path(file_path).joinpath("assets").resolve().as_posix(),
        )
        self.setStyleSheet(stylesheet)

        # Check the internet connection, and perform internet-related tasks
        self.check_connection()
        if "Nightly" not in patcher_version and "RC" not in patcher_version:
            self.check_for_updates()

        self.language_selector = LanguageSelector()
        self.translation_setup()

        self.setWindowTitle(self.tr("WiiLink Patcher"))
        self.setWizardStyle(QWizard.WizardStyle.ModernStyle)
        self.setSubTitleFormat(Qt.TextFormat.RichText)

        self.setFixedWidth(550)
        self.setFixedHeight(625)

        # Override button text to remove chevrons
        self.setButtonText(QWizard.WizardButton.NextButton, self.tr("Next"))
        self.setButtonText(QWizard.WizardButton.BackButton, self.tr("Back"))

        patches_raw = open(
            pathlib.Path(file_path).joinpath("data", "patches.json"), "r"
        ).read()
        patches_json = json.loads(patches_raw)

        # Page setup
        self.setPage(0, MainMenu())

        self.setPage(10, SelectOutputLocation())
        self.setPage(11, WADCleanup())
        self.setPage(12, PatchingPage(patches_json))

        self.setPage(100, ExpressLanguage())
        self.setPage(101, ExpressSecondaryLanguage())
        self.setPage(102, ExpressRegion())
        self.setPage(103, ExpressWiiConnect24Channels(patches_json))
        self.setPage(104, ExpressRegionalChannels(patches_json))
        self.setPage(105, ExpressPlatformConfiguration())

        self.setPage(200, CustomWiiConnect24Channels(patches_json))
        self.setPage(201, CustomRegionalChannels(patches_json))
        self.setPage(202, CustomPlatformConfiguration())
        self.setPage(203, CustomRegionConfiguration())

        self.setPage(300, ExtrasChannelSelection(patches_json))
        self.setPage(301, ExtrasPlatformConfiguration())
        self.setPage(302, ExtrasRegionConfiguration())

        self.setPage(400, DokodemoSelectLanguage())
        self.setPage(401, DokodemoPatchingPage())

        self.setPage(1000, PatchingComplete())

        self.setStartId(0)

    def translation_setup(self):
        """Static method to load patcher translations for the user's language if they exist

        Returns:
            None"""

        self.language_selector.exec()

        path = QLibraryInfo.path(QLibraryInfo.LibraryPath.TranslationsPath)
        translator = QTranslator(QApplication.instance())
        if translator.load(self.language, "qtbase", "_", path):
            QApplication.instance().installTranslator(translator)

        translator = QTranslator(QApplication.instance())
        path = file_path.joinpath("translations").resolve().as_posix()
        if translator.load(self.language, "translation", "_", path):
            QApplication.instance().installTranslator(translator)

    def check_connection(self):
        """Static method to run a connection test and display the results to the user, terminating the patcher if the test is unsuccessful

        Returns:
            None"""
        try:
            connection = connection_test()
        except Exception as e:
            print(traceback.format_exc())
            connection = error_handler(e)

        if connection != "success":
            error_message = None
            osc_exception = False

            match connection:
                case "fail-nus":
                    error_message = (
                        "The patcher failed to connect to Nintendo's update servers."
                    )
                case "fail-patcher":
                    error_message = (
                        "The patcher failed to connect to WiiLink's servers."
                    )
                case "fail-osc":
                    # OSC is a special case here, as the patcher can run without it
                    osc_exception = True
                case _:
                    error_message = f"""The patcher failed to connect to the internet.<br><pre>{connection}</pre>"""

            if error_message:
                QMessageBox.critical(self, "WiiLink Patcher - Error", error_message)
                sys.exit()

            if osc_exception:
                continue_patcher = QMessageBox.warning(
                    self,
                    "WiiLink Patcher - Warning",
                    "The patcher failed to connect to OSC's servers, meaning it cannot automatically download homebrew apps. However, it can still function without OSC. Would you like to continue?",
                    buttons=QMessageBox.StandardButton.Yes
                    | QMessageBox.StandardButton.No,
                )
                if continue_patcher == QMessageBox.StandardButton.Yes:
                    DownloadOSCApp.osc_enabled = False
                else:
                    sys.exit()

    def check_for_updates(self):
        """Static method to compare the current patcher version to the latest, and inform the user if they aren't up to date

        Returns:
            None"""
        try:
            latest_version = get_latest_version()
        except Exception as e:
            QMessageBox.warning(
                self,
                "WiiLink Patcher - Warning",
                f"""Unable to check for updates!

Exception:
{e}""",
            )
        else:
            latest_version_split = latest_version.split(".")
            patcher_version_split = patcher_version.split(".")

            to_update = False

            if len(latest_version_split) == len(patcher_version_split):
                for place in range(len(latest_version_split)):
                    if latest_version_split[place] > patcher_version_split[place]:
                        to_update = True
                        break
                    elif latest_version_split[place] < patcher_version_split[place]:
                        break
            else:
                to_update = True

            if to_update:
                update = QMessageBox.question(
                    self,
                    "WiiLink Patcher - Update",
                    f"""An update has been detected for the patcher, would you like to download it?

Your version: {patcher_version}
Latest version: {latest_version}""",
                )
                if update == QMessageBox.StandardButton.Yes:
                    QDesktopServices.openUrl(
                        "https://github.com/WiiLink24/WiiLink-Patcher-GUI/releases/latest"
                    )
                    sys.exit()


class LanguageSelector(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("WiiLink Patcher - Select Language")
        self.setFixedWidth(450)
        self.setFixedHeight(150)

        # Set background color to match main app
        stylesheet = open(pathlib.Path().joinpath(file_path, "style.qss"), "r").read()
        stylesheet = stylesheet.replace(
            "%AssetsDir%",
            pathlib.Path(file_path).joinpath("assets").resolve().as_posix(),
        )
        self.setStyleSheet(stylesheet)
        self.layout = QVBoxLayout()

        icon = QIcon(
            pathlib.Path()
            .joinpath(file_path, "assets", "logo.webp")
            .resolve()
            .as_posix()
        )
        self.setWindowIcon(icon)

        label = QLabel(
            "Select the language you'd like to use the patcher in from the list below:"
        )
        label.setWordWrap(True)
        self.layout.addWidget(label)
        language_json = file_path.joinpath("translations", "languages.json").read_text(
            encoding="utf-8"
        )
        self.language_names = json.loads(language_json)

        self.language_dropdown = QComboBox()
        self.language_dropdown.addItems(self.language_names.keys())
        self.layout.addWidget(self.language_dropdown)

        done = QPushButton("Done")
        done.clicked.connect(self.set_language)
        self.layout.addWidget(done)

        self.setLayout(self.layout)

    def set_language(self):
        selected_name = self.language_dropdown.currentText()
        selected_language = self.language_names[selected_name]
        WiiLinkPatcherGUI.language = QLocale(selected_language)
        self.destroy()


def main():
    # Clear previous temporary directory to prevent potential conflicts
    if temp_dir.exists():
        shutil.rmtree(temp_dir)

    # Create instance of QApplication and the patcher's QWizard
    app = QApplication(sys.argv)
    wizard = WiiLinkPatcherGUI()

    # Start the wizard
    wizard.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
