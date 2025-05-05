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

import os
import pathlib
import shutil
import subprocess
import sys
import tempfile
import webbrowser

from PySide6.QtCore import QTranslator, QLocale, QLibraryInfo, QTimer, Qt
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QWizard, QApplication, QWizardPage, QVBoxLayout, QRadioButton, QLabel, \
    QPushButton, QMessageBox, QWidget

from setup.custom import CustomWiiConnect24Channels, CustomRegionalChannels, CustomPlatformConfiguration, \
    CustomRegionConfiguration
from setup.enums import Platforms, SetupTypes
from setup.express import ExpressRegion, ExpressRegionalChannels, ExpressRegionalChannelTranslation, \
    ExpressRegionalChannelLanguage, ExpressDemaeConfiguration, ExpressPlatformConfiguration
from setup.extras import ExtrasSystemChannelRestorer, MinimalExtraChannels, FullExtraChannels, \
    ExtrasPlatformConfiguration, ExtrasRegionConfiguration
from setup.download import connection_test, download_translation_dict, download_translation
from setup.patch import PatchingPage

patcher_url = "https://patcher.wiilink24.com"
temp_dir = pathlib.Path(tempfile.gettempdir()).joinpath("WiiLinkPatcher")
wiilink_dir = pathlib.Path().joinpath("WiiLink")


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
            "credits": QPushButton(self.tr("About WiiLink Patcher")),
        }

        self.layout = QVBoxLayout()

        # Add checkboxes to layout
        for button in self.options.values():
            self.layout.addWidget(button)
            button.clicked.connect(self.completeChanged)

        # Select the first option        
        next(iter(self.options.values())).setChecked(True)
        
        self.options["credits"].clicked.connect(self.show_credits)

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
    
    def show_credits(self):
        self.credits = Credits()
        self.credits.show()


class Credits(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle(self.tr("WiiLink Patcher - About"))
        self.setFixedWidth(450)
        self.setFixedHeight(500)
        
        # Set background color to match main app
        self.setStyleSheet("""
            Credits {
                background-color: #222222;
                color: #ffffff;
            }
            QLabel {
                color: #ffffff;
            }
            QLabel[class="title"] {
                font-size: 20px;
                font-weight: bold;
                color: #ffffff;
            }
            QLabel[class="version"] {
                font-size: 13px;
                color: #aaaaaa;
            }
            QLabel[class="copyright"] {
                font-size: 12px;
                color: #888888;
            }
            QLabel[class="header"] {
                font-size: 14px;
                font-weight: bold;
                border-bottom: 1px solid #444444;
                padding-bottom: 4px;
                margin-top: 8px;
            }
            QPushButton {
                background-color: transparent;
                border: 1px solid rgba(70, 70, 70, 1);
                border-radius: 8px;
                padding: 8px 12px;
                margin: 4px 0px;
                font-size: 13px;
                font-weight: 500;
                color: #ffffff;
                text-align: center;
            }
            QPushButton:hover {
                background-color: rgba(60, 60, 60, 1);
                border-color: #4a86e8;
            }
            QPushButton:pressed {
                background-color: rgba(26, 115, 232, 0.15);
                border: 1px solid #1a73e8;
            }
        """)
        
        # Create main layout
        self.layout = QVBoxLayout()
        self.layout.setSpacing(4)
        self.layout.setContentsMargins(30, 20, 30, 20)
        
        # Logo
        logo_label = QLabel()
        icon = QIcon(os.path.join(os.path.dirname(__file__), "assets", "logo.webp"))
        logo_pixmap = icon.pixmap(96, 96)
        logo_label.setPixmap(logo_pixmap)
        logo_label.setAlignment(Qt.AlignCenter)
        
        # Title
        title_label = QLabel(self.tr("WiiLink Patcher"))
        title_label.setProperty("class", "title")
        title_label.setAlignment(Qt.AlignCenter)
        
        # Version
        version_label = QLabel(self.tr("GUI - Version 2.0"))
        version_label.setProperty("class", "version")
        version_label.setAlignment(Qt.AlignCenter)
        
        # Copyright
        copyright_label = QLabel(self.tr("© 2020-2025 WiiLink Team. All rights reserved."))
        copyright_label.setProperty("class", "copyright")
        copyright_label.setAlignment(Qt.AlignCenter)
        
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
        self.website_button.clicked.connect(lambda: webbrowser.open("https://wiilink.ca"))
        links_layout.addWidget(self.website_button)
        
        # GitHub button
        self.github_button = QPushButton(self.tr("View Project on GitHub"))
        self.github_button.clicked.connect(lambda: webbrowser.open("https://github.com/WiiLink24"))
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
            "sketch": QLabel(self.tr("<a href=https://noahpistilli.ca style='color: #4a86e8; text-decoration: none;'><b>Sketch</b></a> - WiiLink Project Lead")),
            "isla": QLabel(self.tr("<a href=https://islawalker.uk style='color: #4a86e8; text-decoration: none;'><b>Isla</b></a> - WiiLink Patcher GUI Developer")),
            "pablo": QLabel(self.tr("<a href=https://github.com/pabloscorner style='color: #4a86e8; text-decoration: none;'><b>PablosCorner</b></a> - WiiLink Patcher CLI Developer")),
            "alex": QLabel(self.tr("<a href=https://github.com/humanoidear style='color: #4a86e8; text-decoration: none;'><b>Alex</b></a> - WiiLink Design Lead")),
            "ninjacheetah": QLabel(self.tr("<a href=https://ninjacheetah.dev style='color: #4a86e8; text-decoration: none;'><b>NinjaCheetah</b></a> - libWiiPy Developer"))
        }

        # Add team members to layout
        for credit in self.people.values():
            credit.setOpenExternalLinks(True)
            credit.setContentsMargins(15, 0, 0, 0)
            self.layout.addWidget(credit)
        
        # Add spacer at the bottom
        self.layout.addStretch()
        
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
        match PatchingPage.setup_type:
            case SetupTypes.Extras:
                if PatchingPage.platform != Platforms.Dolphin:
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

    connection = connection_test()

    app = QApplication(sys.argv)

    wizard = QWizard()
    wizard.setWindowTitle(app.tr("WiiLink Patcher"))
    wizard.setWizardStyle(QWizard.WizardStyle.ModernStyle)
    wizard.setSubTitleFormat(Qt.RichText)
    
    icon = QIcon(os.path.join(os.path.dirname(__file__), "assets", "logo.webp"))
    background = QIcon(os.path.join(os.path.dirname(__file__), "assets", "background.webp"))
    logo = icon.pixmap(64, 64)
    banner = background.pixmap(700, 120)
    wizard.setPixmap(QWizard.WizardPixmap.LogoPixmap, logo)
    wizard.setPixmap(QWizard.WizardPixmap.BannerPixmap, banner)
    
    app.setWindowIcon(icon)
    
    # Apply global stylesheet for consistent styling across all pages
    wizard.setStyleSheet("""
        QWizard {
        background-color: #222222;
    }
    
    QWizard QLabel {
        color: #ffffff;
    }
    
    QLabel[class="QWizardPageTitle"] {
        background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #1a73e8, stop:1 #135cb6);
        color: white;
        font-size: 18px;
        font-weight: bold;
        padding: 8px 10px;
        border-top-left-radius: 4px;
        border-top-right-radius: 4px;
    }
    
    QLabel[class="QWizardPageSubTitle"] {
        background-color: #f0f6ff;
        color: #1a73e8;
        font-size: 13px;
        padding: 6px 10px;
        border-bottom: 1px solid #c2d7ff;
    }
    
        QRadioButton {
            background-color: transparent;
            border: 1px solid rgba(70, 70, 70, 1);
            border-radius: 8px;
            padding: 8px 10px;
            font-size: 13px;
            font-weight: 500;
            color: #ffffff;
        }
        
        QRadioButton:hover {
            background-color: rgba(60, 60, 60, 1);
            border-color: #4a86e8;
        }
        
        QRadioButton:checked {
            background-color: rgba(26, 115, 232, 0.08);
            border: 1px solid #1a73e8;
            color: #1a73e8;
        }
        
        QRadioButton::indicator {
            width: 18px;
            height: 18px;
            border-radius: 5px;
            border: 1px solid #5f6368;
            margin-right: 8px;
            subcontrol-position: left center;
        }
        
        QRadioButton::indicator:checked {
            background-color: #1a73e8;
            border: 1px solid #1a73e8;
            image: url(assets/rounded_square.svg);
        }
        
        QRadioButton::indicator:hover {
            border-color: #1a73e8;
        }
        
        QPushButton {
            background-color: transparent;
            border: 1px solid rgba(70, 70, 70, 1);
            border-radius: 8px;
            padding: 6px 10px;
            margin: 4px 0px;
            font-size: 13px;
            font-weight: 500;
            color: #ffffff;
        }
        
        QPushButton:hover {
            background-color: rgba(60, 60, 60, 1);
            border-color: #4a86e8;
        }
        
        QPushButton:pressed {
            background-color: rgba(26, 115, 232, 0.15);
            border: 1px solid #1a73e8;
        }
        
        QPushButton:disabled {
            background-color: rgba(70, 70, 70, 0.5);
            border: 1px solid rgba(100, 100, 100, 0.3);
            color: rgba(255, 255, 255, 0.3);
        }
        
        /* Style for the wizard's next and back buttons with chevrons */
        QWizard QToolButton {
            background-color: rgba(50, 50, 50, 1);
            border: 1px solid rgba(70, 70, 70, 1);
            border-radius: 4px;
            padding: 2px;
            color: #ffffff;
        }
        
        QWizard QToolButton:hover {
            background-color: rgba(60, 60, 60, 1);
            border-color: #4a86e8;
        }
        
        QWizard QToolButton:disabled {
            background-color: rgba(70, 70, 70, 0.5);
            border: 1px solid rgba(100, 100, 100, 0.3);
            color: rgba(255, 255, 255, 0.3);
        }
        
        QCheckBox {
            background-color: transparent;
            border: 1px solid rgba(70, 70, 70, 1);
            border-radius: 8px;
            padding: 8px 10px;
            font-size: 13px;
            font-weight: 500;
            color: #ffffff;
        }
        
        QCheckBox:hover {
            background-color: rgba(60, 60, 60, 1);
            border-color: #4a86e8;
        }
        
        QCheckBox:checked {
            background-color: rgba(26, 115, 232, 0.08);
            border: 1px solid #1a73e8;
            color: #1a73e8;
        }
        
        QCheckBox::indicator {
            width: 18px;
            height: 18px;
            border-radius: 4px;
            border: 1px solid #5f6368;
            margin-right: 8px;
            subcontrol-position: left center;
        }
        
        QCheckBox::indicator:checked {
            background-color: #1a73e8;
            border: 1px solid #1a73e8;
            image: url(assets/check.svg);
        }
        
        QCheckBox::indicator:hover {
            border-color: #1a73e8;
        }
        
        QCheckBox:disabled {
            background-color: rgba(70, 70, 70, 0.5);
            border: 1px solid rgba(100, 100, 100, 0.3);
            color: rgba(255, 255, 255, 0.3);
        }
        
        QCheckBox::indicator:disabled {
            background-color: rgba(70, 70, 70, 0.5);
            border: 1px solid rgba(100, 100, 100, 0.3);
        }
    """)
    
    wizard.setButtonText(QWizard.NextButton, "Next")
    wizard.setButtonText(QWizard.BackButton, "Back")

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

    wizard.setPage(10, PatchingPage())

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
