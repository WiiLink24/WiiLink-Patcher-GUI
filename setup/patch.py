import pathlib
import sys

import libWiiPy
import bsdiff4

from PySide6.QtCore import QObject, Signal, QTimer, QThread, Qt
from PySide6.QtWidgets import (
    QMessageBox,
    QWizardPage,
    QLabel,
    QProgressBar,
    QVBoxLayout,
    QWizard,
    QTextEdit,
)

from PySide6.QtGui import QFont

from modules.widgets import ConsoleOutput
from .enums import *
from .download import (
    download_patch,
    download_file,
    download_agc,
    DownloadOSCApp,
    download_title_contents,
    download_spd,
)
from .newsRenderer import NewsRenderer
from modules.consts import wad_directory, patcher_url


def apply_bsdiff_patches(
    channel_name: str, patch_files: dict, title: libWiiPy.title.Title
):
    """Download and apply bsdiff patches to the app files specified

    Args:
        channel_name: The directory name of the channel's patches on the server
        patch_files: A dictionary containing the file names for the patches, and the index they are applied to
        title: The libWiiPy title which has the contents to be patched

    Returns:
        A libWiiPy title, containing the patched contents in place of the stock ones"""

    # Apply patches
    for patch in patch_files:
        index = patch["content_id"]
        patch_file = patch["patch_name"]

        print(f" - Patching content {index + 1}...")

        print("   - Downloading patch...")

        try:
            patch_binary = download_patch(channel_name.lower(), patch_file)
        except Exception as e:
            print("      - Failed!")
            raise ValueError(e)
        else:
            print("      - Done!")

        stock_content = title.get_content_by_index(index)

        print("   - Applying patch...")

        try:
            patched_content = bsdiff4.patch(stock_content, patch_binary)
        except Exception as e:
            print("      - Failed!")
            raise ValueError(e)
        else:
            print("      - Done!")

        title.set_content(patched_content, index)

    return title


def patch_channel(channel: dict, network: str = None):
    """Download a specified channel from NUS, and apply patches to the channel's app files

    Args:
        channel: A dictionary containing all info on the channel to patch
        network: An optional string of the network the channel uses to append to its file name

    Returns:
        None"""

    wad_directory.mkdir(exist_ok=True, parents=True)

    if channel["patches"]:
        print(f"Patching {channel["name"]}:")
        if network:
            output_wad = pathlib.Path().joinpath(
                wad_directory, f"{channel["name"]} ({network}).wad"
            )
        else:
            output_wad = pathlib.Path().joinpath(
                wad_directory, f"{channel["name"]}.wad"
            )
    else:
        print(f"Downloading {channel["name"]}:")
        output_wad = pathlib.Path().joinpath(wad_directory, f"{channel["name"]}.wad")

    if channel["patch_folder"]:
        file_url = f"{patcher_url}/{channel["patch_folder"].lower()}"

    title = libWiiPy.title.Title()

    print(" - Downloading and parsing TMD...")
    tmd = libWiiPy.title.download_tmd(channel["title_id"], channel["latest_version"])
    title.load_tmd(tmd)
    print("   - Done!")

    print(" - Downloading and parsing ticket...")
    if channel["additional_files"] and "ticket" in channel["additional_files"]:
        ticket = download_file(f"{file_url}/{channel["title_id"]}.tik")
    else:
        ticket = libWiiPy.title.download_ticket(
            channel["title_id"], channel["latest_version"]
        )

    title.load_ticket(ticket)
    print("   - Done!")

    print(" - Downloading certificate chain...")
    cert = libWiiPy.title.download_cert_chain()
    print("   - Done!")

    title.load_cert_chain(cert)

    title = download_title_contents(title)

    if channel["patches"]:
        title = apply_bsdiff_patches(channel["patch_folder"], channel["patches"], title)

    if channel["additional_files"] and "tmd" in channel["additional_files"]:
        print(" - Patching TMD...")
        tmd = download_file(f"{file_url}/{channel["patch_folder"]}.tmd")
        title.load_tmd(tmd)
        print("   - Done!")

    print(" - Packing WAD...")

    try:
        open(output_wad, "wb").write(title.dump_wad())
    except Exception as e:
        print("   - Failed!")
        raise ValueError(e)
    else:
        print("   - Done!")


class PatchingPage(QWizardPage):
    platform: Platforms
    region: Regions
    selected_channels: list
    regional_channels: bool = False
    setup_type: SetupTypes
    osc_enabled: bool = True

    patching_complete = False
    percentage: int
    status: str

    def __init__(self, patches_json: dict, parent=None):
        super().__init__(parent)

        self.setTitle(self.tr("Patching in progress"))
        self.setSubTitle(self.tr("Please wait while the patcher works its magic!"))

        self.label = QLabel(self.tr("Downloading files..."))
        self.label.setWordWrap(True)
        self.progress_bar = QProgressBar(self)

        self.news_box = NewsRenderer.createNewsBox(self)

        layout = QVBoxLayout()
        layout.addWidget(self.label)
        layout.addWidget(self.progress_bar)
        layout.addSpacing(10)
        layout.addWidget(self.news_box)

        self.console = QTextEdit()
        self.console.setReadOnly(True)
        self.console.setHidden(True)
        self.console.setObjectName("console")

        layout.addWidget(self.console)

        self.toggle_console_label = QLabel(self.tr("Show Details"))

        font = QFont()
        font.setUnderline(True)
        self.toggle_console_label.setFont(font)
        self.toggle_console_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.toggle_console_label.setStyleSheet("color: #606060;")
        self.toggle_console_label.setCursor(Qt.CursorShape.PointingHandCursor)

        self.toggle_console_label.mousePressEvent = self.toggle_console

        layout.addWidget(self.toggle_console_label)

        self.setLayout(layout)

        QTimer.singleShot(0, lambda: NewsRenderer.getNews(self, self.news_box))

        self.patches_json = patches_json

        # Start thread to perform patching
        self.logic_thread = QThread()
        self.logic_worker = PatchingWorker()

    def initializePage(self):
        QTimer.singleShot(0, self.disable_back_button)

        # Redirect outputs to the console
        sys.stdout = ConsoleOutput(self.console, sys.__stdout__)
        sys.stderr = ConsoleOutput(self.console, sys.__stderr__)

        # Setup variables
        self.logic_worker.setup_type = self.setup_type
        self.logic_worker.platform = self.platform
        self.logic_worker.region = self.region
        self.logic_worker.regional_channels = self.regional_channels
        self.logic_worker.selected_channels = self.selected_channels
        self.logic_worker.patches_json = self.patches_json

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

        # Remove output redirects
        sys.stdout = sys.__stdout__
        sys.stderr = sys.__stderr__

        self.completeChanged.emit()
        QTimer.singleShot(0, self.wizard().next)

    def nextId(self):
        if self.platform != Platforms.Dolphin:
            return 12

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

        QMessageBox.warning(
            self,
            "WiiLink Patcher - Warning",
            f"An exception was encountered while patching.<br><br>Exception:<br>{error}<br><br>Please report this issue in the WiiLink Discord Server (<a href='https://discord.gg/wiilink'>discord.gg/wiilink</a>).",
        )

    def toggle_console(self, event=None):
        is_visible = self.console.isVisible()
        self.console.setHidden(is_visible)
        self.news_box.setHidden(not is_visible)

        # Change the label text based on the current state
        if is_visible:
            self.toggle_console_label.setText(self.tr("Show Details"))
        else:
            self.toggle_console_label.setText(self.tr("Hide Details"))


class PatchingWorker(QObject):
    platform: Platforms
    region: Regions
    selected_channels: list
    regional_channels: bool
    setup_type: SetupTypes

    patches_json: dict

    is_patching_complete: bool
    finished = Signal(bool)
    broadcast_percentage = Signal(int)
    broadcast_status = Signal(str)
    error = Signal(str)

    def patching_functions(self):

        percentage_increment = 100 / (len(self.selected_channels) + 1)

        percentage = 0

        self.download_supporting_apps()
        percentage += percentage_increment
        self.broadcast_percentage.emit(round(percentage))

        for channel_key in self.selected_channels:
            channel_indexes = channel_key.split("_")
            try:
                category_index = int(channel_indexes[0])
                channel_index = int(channel_indexes[1])
                channel_category = self.find_category(category_index)
                channel_to_patch = self.find_channel(channel_category, channel_index)

                if channel_to_patch["patches"]:
                    self.broadcast_status.emit(
                        self.tr(f"Patching {channel_to_patch["name"]}...")
                    )
                else:
                    self.broadcast_status.emit(
                        self.tr(f"Downloading {channel_to_patch["name"]}...")
                    )

                if channel_category["network"] != "OSC":
                    patch_channel(channel_to_patch, channel_category["network"])

                if channel_to_patch["additional_apps"]:
                    for app in channel_to_patch["additional_apps"]:
                        if app != "agc":
                            DownloadOSCApp(app)
                        else:
                            download_agc(self.platform)

                if channel_to_patch["additional_channels"]:
                    for additional_channel in channel_to_patch["additional_channels"]:
                        additional_category_index = additional_channel["category"]
                        additional_channel_index = additional_channel["channel"]
                        additional_category = self.find_category(
                            additional_category_index
                        )
                        additional_channel_dict = self.find_channel(
                            additional_category, additional_channel_index
                        )

                        patch_channel(additional_channel_dict)
            except Exception as e:
                print(
                    f"""An exception occured!

Exception:
{e}"""
                )
                self.error.emit(f"{e}")
            finally:
                percentage += percentage_increment
                self.broadcast_percentage.emit(round(percentage))

        print("Patching complete!")
        self.finished.emit(True)

    def download_supporting_apps(self):
        match self.setup_type:
            case SetupTypes.Extras:
                if self.platform != Platforms.Dolphin:
                    DownloadOSCApp("yawmME")
            case _:
                if self.platform != Platforms.Dolphin:
                    DownloadOSCApp("yawmME")
                    DownloadOSCApp("sntp")

                if self.platform == Platforms.vWii:
                    eula_category = self.find_category(14)
                    eula_channel = self.find_channel(eula_category, self.region.value)

                    patch_channel(eula_channel)

                if self.regional_channels and self.region != Regions.Japan:
                    download_spd()

                DownloadOSCApp("Mail-Patcher")

    def find_category(self, category_id: int):
        for category in self.patches_json:
            if category["category_id"] == category_id:
                return category

        raise KeyError(f"Category {category_id} does not exist!")

    @staticmethod
    def find_channel(category: dict, channel_id: int):
        for channel in category["channels"]:
            if channel["item_id"] == channel_id:
                return channel

        raise KeyError(
            f"Channel {channel_id} does not exist in category {category["category_id"]}!"
        )
