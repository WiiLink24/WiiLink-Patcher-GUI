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
# nuitka-project: --include-package="certifi"
# nuitka-project: --include-data-dir={MAIN_DIRECTORY}/assets=assets

import os
import pathlib
import shutil
import subprocess
import sys
import tempfile
import webbrowser

from PySide6.QtCore import QTranslator, QLocale, QLibraryInfo, QTimer
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QWizard, QApplication, QWizardPage, QVBoxLayout, QRadioButton, QLabel, \
    QPushButton, QMessageBox, QWidget

from setup.custom import CustomWiiConnect24Channels, CustomRegionalChannels, CustomPlatformConfiguration, \
    CustomRegionConfiguration, CustomPatchingPage
from setup.enums import Platforms, SetupTypes
from setup.express import ExpressRegion, ExpressRegionalChannels, ExpressRegionalChannelTranslation, \
    ExpressRegionalChannelLanguage, ExpressDemaeConfiguration, ExpressPlatformConfiguration, ExpressPatchingPage
from setup.extras import ExtrasSystemChannelRestorer, MinimalExtraChannels, FullExtraChannels, \
    ExtrasPlatformConfiguration, ExtraPatchingPage
from setup.download import connection_test, download_translation_dict, download_translation

patcher_url = "https://patcher.wiilink24.com"
temp_dir = pathlib.Path(tempfile.gettempdir()).joinpath("WiiLinkPatcher")
wiilink_dir = pathlib.Path().joinpath("WiiLink")
setup_type = SetupTypes.Express


class IntroPage(QWizardPage):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle(self.tr("Welcome to the WiiLink Patcher!"))
        self.setSubTitle(self.tr("This tool will walk you through downloading the necessary files to install WiiLink."))

        self.label = QLabel(self.tr("""Welcome to the WiiLink Patcher!
                            
With this tool, you'll be able to get patched files to install WiiLink in no time!

Press 'Next' to get started!"""))
        self.label.setWordWrap(True)

        self.layout = QVBoxLayout()

        self.layout.addWidget(self.label)

        self.setLayout(self.layout)


class MainMenu(QWizardPage):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle(self.tr("Choose what you'd like to do!"))
        self.setSubTitle(self.tr("We recommend choosing 'Express Setup' for first-time users."))

        self.options = {
            "express_setup": QRadioButton(self.tr("Express Setup (Recommended)")),
            "custom_setup": QRadioButton(self.tr("Custom Setup (Advanced)")),
            "extra_channels": QRadioButton(self.tr("Extra Channels (Optional)")),
            "credits": QPushButton(self.tr("Credits"))
        }

        self.layout = QVBoxLayout()

        # Add checkboxes to layout
        for button in self.options.values():
            self.layout.addWidget(button)
            button.clicked.connect(self.completeChanged)
            button.clicked.connect(self.set_setup_type)
        
        self.options["credits"].clicked.connect(self.show_credits)

        self.setLayout(self.layout)

    def set_setup_type(self):
        global setup_type
        if self.options["express_setup"].isChecked():
            setup_type = SetupTypes.Express
        elif self.options["custom_setup"].isChecked():
            setup_type = SetupTypes.Custom
        elif self.options["extra_channels"].isChecked():
            setup_type = SetupTypes.Extras

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
    
    def show_credits(self):
        self.credits = Credits()
        self.credits.show()


class Credits(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle(self.tr("WiiLink Patcher - Credits"))

        self.people = {
            "sketch": QLabel(self.tr("<a href=https://noahpistilli.ca><b>Sketch</b></a> - WiiLink Project Lead")),
            "isla": QLabel(self.tr("<a href=https://islawalker.uk><b>Isla</b></a> - WiiLink Patcher GUI Developer")),
            "pablo": QLabel(self.tr("<a href=https://github.com/pabloscorner><b>PablosCorner</b></a> - WiiLink Patcher CLI Developer")),
            "alex": QLabel(self.tr("<a href=https://github.com/humanoidear><b>Alex</b></a> - WiiLink Design Lead")),
            "ninjacheetah": QLabel(self.tr("<a href=https://ninjacheetah.dev><b>NinjaCheetah</b></a> - libWiiPy Developer"))
        }

        self.layout = QVBoxLayout()

        for credit in self.people.values():
            self.layout.addWidget(credit)
            credit.setOpenExternalLinks(True)

        self.setLayout(self.layout)


class PatchingComplete(QWizardPage):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setFinalPage(True)

        self.completeChanged.emit()

        self.setTitle(self.tr("Patching complete!"))
        self.setSubTitle(self.tr("Patching has been completed"))

        self.label = QLabel(self.tr("Patching is complete! You can find the relevant files at the following location:\n"
                                    f"{pathlib.Path(wiilink_dir).resolve()}\n\n"
                                    "What would you like to do now?"))

        self.label.setWordWrap(True)

        self.open_folder = QPushButton(self.tr("Open the 'WiiLink' folder"))

        self.layout = QVBoxLayout()
        self.layout.addWidget(self.label)

        self.layout.addWidget(self.open_folder)

        self.setLayout(self.layout)

        self.open_folder.clicked.connect(self.open_wiilink_folder)

    def initializePage(self):
        global setup_type

        match setup_type:
            case SetupTypes.Extras:
                if ExtraPatchingPage.platform != Platforms.Dolphin:
                    open_guide = QPushButton(self.tr("Open the WAD installation guide in your web browser"))
                    self.layout.addWidget(open_guide)
                    open_guide.clicked.connect(self.open_guide_link)
            case _:
                open_guide = QPushButton(self.tr("Open the WiiLink installation guide in your web browser"))
                self.layout.addWidget(open_guide)
                open_guide.clicked.connect(self.open_guide_link)

        self.setLayout(self.layout)

        QTimer.singleShot(0, self.disable_buttons)

    @staticmethod
    def open_guide_link():

        guide_url = "https://wiilink.ca/guide"
        match setup_type:
            case SetupTypes.Express:
                match ExpressPatchingPage.platform:
                    case Platforms.Wii:
                        guide_url = f"{guide_url}/wii/#section-ii---installing-wads-and-patching-wii-mail"
                    case Platforms.vWii:
                        guide_url = f"{guide_url}/vwii/#section-iii---installing-wads-and-patching-wii-mail"
                    case Platforms.Dolphin:
                        guide_url = f"{guide_url}/dolphin/#section-ii---installing-wads"
            case SetupTypes.Custom:
                match CustomPatchingPage.platform:
                    case Platforms.Wii:
                        guide_url = f"{guide_url}/wii/#section-ii---installing-wads-and-patching-wii-mail"
                    case Platforms.vWii:
                        guide_url = f"{guide_url}/vwii/#section-iii---installing-wads-and-patching-wii-mail"
                    case Platforms.Dolphin:
                        guide_url = f"{guide_url}/dolphin/#section-ii---installing-wads"
            case SetupTypes.Extras:
                guide_url = "https://wii.hacks.guide/yawmme"

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

    connection = connection_test()

    app = QApplication(sys.argv)

    wizard = QWizard()
    wizard.setWindowTitle(app.tr("WiiLink Patcher"))
    wizard.setWizardStyle(QWizard.WizardStyle.ModernStyle)

    icon = QIcon(os.path.join(os.path.dirname(__file__), "assets", "logo.webp"))
    logo = icon.pixmap(64, 64)
    wizard.setPixmap(QWizard.WizardPixmap.LogoPixmap, logo)
    app.setWindowIcon(icon)

    if not connection:
        QMessageBox.critical(QWidget(),
                             "WiiLink Patcher - Error",
                             "The patcher failed to connect to the internet, and thus cannot continue.")
        sys.exit()
    
    language = QLocale.languageToCode(QLocale.system().language())
    supported_languages = download_translation_dict()

    if supported_languages is False:
        QMessageBox.warning(QWidget(),
                             "WiiLink Patcher - Warning",
                             "The patcher failed to download the list of languages. Therefore, it will run in English.")
    else:
        if language in supported_languages:
            if download_translation(language) is False:
                QMessageBox.warning(QWidget(),
                                    "WiiLink Patcher - Warning",
                                    "The patcher failed to download translations for your language. Therefore, it will run in English")

    path = QLibraryInfo.path(QLibraryInfo.LibraryPath.TranslationsPath)
    translator = QTranslator(app)
    if translator.load(QLocale.system(), 'qtbase', '_', path):
        app.installTranslator(translator)
    translator = QTranslator(app)
    path = os.path.join(os.path.dirname(__file__), "translations")
    if translator.load(QLocale.system(), 'translation', '_', path):
        app.installTranslator(translator)

    wizard.setPage(0, IntroPage())
    wizard.setPage(1, MainMenu())

    wizard.setPage(100, ExpressRegion())
    wizard.setPage(101, ExpressRegionalChannels())
    wizard.setPage(102, ExpressRegionalChannelTranslation())
    wizard.setPage(103, ExpressRegionalChannelLanguage())
    wizard.setPage(104, ExpressDemaeConfiguration())
    wizard.setPage(105, ExpressPlatformConfiguration())
    wizard.setPage(106, ExpressPatchingPage())

    wizard.setPage(200, CustomWiiConnect24Channels())
    wizard.setPage(201, CustomRegionalChannels())
    wizard.setPage(202, CustomPlatformConfiguration())
    wizard.setPage(203, CustomRegionConfiguration())
    wizard.setPage(204, CustomPatchingPage())

    wizard.setPage(300, ExtrasSystemChannelRestorer())
    wizard.setPage(301, MinimalExtraChannels())
    wizard.setPage(302, FullExtraChannels())
    wizard.setPage(303, ExtrasPlatformConfiguration())
    wizard.setPage(304, ExtraPatchingPage())

    wizard.setPage(1000, PatchingComplete())

    wizard.setStartId(0)

    wizard.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
