import os
import subprocess
import sys
import psutil
import shutil
import pathlib
import ctypes
import pyudev

from PySide6.QtWidgets import (
    QVBoxLayout,
    QLabel,
    QComboBox,
    QCheckBox,
    QPushButton,
    QHBoxLayout,
    QWizard,
    QWizardPage,
    QRadioButton,
    QMessageBox,
    QProgressBar,
)
from PySide6.QtCore import QTimer, QThread, QObject, Signal

from .newsRenderer import NewsRenderer

sd_path = ""
sd_wad_path = "WAD"


def get_devices(removable_only=True):
    devices = {}
    for part in psutil.disk_partitions():
        if removable_only and not check_removable(part):
            continue
        try:
            capacity = psutil.disk_usage(part.mountpoint).total
            capacity_gb = capacity / (1024**3)
            label = f"{part.mountpoint} - {capacity_gb:.2f} GB"
            devices.update({label: part.mountpoint})
        except PermissionError:
            continue
    return devices


def check_removable(device: psutil._common.sdiskpart):
    match sys.platform:
        case "win32":
            path = device.mountpoint
            device_type = ctypes.windll.kernel32.GetDriveTypeW(ctypes.c_wchar_p(path))
            return device_type == 2
        case "darwin":
            device_info = subprocess.check_output(
                ["diskutil", "info", device.device], text=True
            )
            return "Removable Media: Yes" in device_info
        case "linux":
            context = pyudev.Context()

            udev_partition = pyudev.Devices.from_device_file(context, device.device)

            if udev_partition.device_type != "disk":
                udev_device = udev_partition.find_parent("block", "disk")
            else:
                udev_device = udev_partition

            return udev_device.attributes.get("removable") == b"1"
        case _:
            return True


class AskSD(QWizardPage):
    def __init__(self):
        super().__init__()

        self.setTitle(self.tr("File copying"))
        self.setSubTitle(
            self.tr(
                "Decide if you'd like the patcher to copy its files to an external storage device."
            )
        )

        self.label = QLabel(
            self.tr(
                "Would you like the patcher to automatically copy its patched files to your SD card / USB drive?"
            )
        )
        self.label.setWordWrap(True)

        self.yes = QRadioButton(self.tr("Yes"))
        self.no = QRadioButton(self.tr("No"))

        self.yes.clicked.connect(self.completeChanged.emit)
        self.no.clicked.connect(self.completeChanged.emit)

        self.yes.setChecked(True)

        self.layout = QVBoxLayout()

        self.layout.addWidget(self.label)

        self.layout.addWidget(self.yes)
        self.layout.addWidget(self.no)

        self.setLayout(self.layout)

        QTimer.singleShot(0, self.disable_back_button)

    def isComplete(self):
        QTimer.singleShot(0, self.disable_back_button)
        if self.yes.isChecked() or self.no.isChecked():
            return True

        return False

    def nextId(self):
        if self.yes.isChecked():
            return 13
        elif self.no.isChecked():
            return 1000

        return 0

    def disable_back_button(self):
        self.wizard().button(QWizard.WizardButton.BackButton).setEnabled(False)


class SelectSD(QWizardPage):
    def __init__(self):
        super().__init__()
        self.setTitle(self.tr("Copying files: Step 1"))
        self.setSubTitle(self.tr("Select your storage device."))

        self.layout = QVBoxLayout()

        self.label = QLabel(self.tr(self.tr("<b>Select your SD card / USB drive:</b>")))
        self.layout.addWidget(self.label)

        self.layout.addSpacing(10)

        self.checkbox = QCheckBox("Show only removable devices?\n(Recommended)")
        self.checkbox.setChecked(True)
        self.checkbox.clicked.connect(self.refresh_devices)
        self.layout.addWidget(self.checkbox)

        self.selector = QHBoxLayout()

        self.combo = QComboBox()
        self.combo.currentIndexChanged.connect(lambda: self.completeChanged.emit())
        self.selector.addWidget(self.combo)

        self.refresh = QPushButton(self.tr("Refresh"))
        self.refresh.setFixedWidth(96)
        self.refresh.clicked.connect(self.refresh_devices)
        self.selector.addWidget(self.refresh)

        self.layout.addLayout(self.selector)

        self.setLayout(self.layout)

        self.devices = []
        self.refresh_devices()

    def refresh_devices(self):
        removable_only = self.checkbox.isChecked()
        new_devices = get_devices(removable_only=removable_only)

        if new_devices != self.devices:
            self.devices = new_devices
            self.combo.clear()
            for label, mountpoint in self.devices.items():
                self.combo.addItem(label, mountpoint)

    def isComplete(self):
        selected_device = self.combo.currentData()
        if selected_device:
            return True

        return False

    def nextId(self):
        global sd_wad_path
        selected_device = self.combo.currentData()

        # Find existing WAD folder, regardless of case
        for folder in os.listdir(selected_device):
            if (
                folder.upper() == "WAD"
                and pathlib.Path().joinpath(selected_device, folder).is_dir()
            ):
                sd_wad_path = folder
                return 14

        return 15

    def validatePage(self):
        global sd_path

        sd_path = self.combo.currentData()

        return True


class WADCleanup(QWizardPage):
    def __init__(self):
        super().__init__()
        self.setTitle(self.tr("Copying files: Step 1A"))
        self.setSubTitle(self.tr("Choose what to do with existing WAD folder."))

        self.layout = QVBoxLayout()
        self.layout.setSpacing(10)
        self.layout.setContentsMargins(20, 20, 20, 20)

        self.label = QLabel(
            self.tr(
                """The patcher has detected a directory called 'WAD' on your selected storage device.
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

    def validatePage(self):
        global sd_path
        global sd_wad_path

        sd_wad_directory = pathlib.Path().joinpath(sd_path, sd_wad_path)
        if self.options["rename"].isChecked():
            try:
                os.rename(sd_wad_directory, pathlib.Path().joinpath(sd_path, "WAD.bak"))
            except (OSError, FileExistsError):
                i = 1
                while True:
                    try:
                        os.rename(
                            sd_wad_directory,
                            pathlib.Path().joinpath(sd_path, f"WAD.bak ({i})"),
                        )
                    except (OSError, FileExistsError):
                        i += 1
                        continue
                    else:
                        break
            finally:
                sd_wad_path = "WAD"
        elif self.options["delete"].isChecked():
            shutil.rmtree(sd_wad_directory)
            sd_wad_path = "WAD"

        return True

    def isComplete(self):
        """Enable Next button only if a radio button is selected"""
        for button in self.options.values():
            if button.isChecked():
                return True

        return False


class FileCopying(QWizardPage):
    copying_complete: bool = False

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setTitle(self.tr("Copying in progress"))
        self.setSubTitle(self.tr("Please wait while the patcher copies its files..."))

        self.label = QLabel(self.tr("Copying files..."))
        self.progress_bar = QProgressBar(self)
        self.progress_bar.setRange(0, 0)

        self.news_box = NewsRenderer.createNewsBox(self)

        layout = QVBoxLayout()
        layout.addWidget(self.label)
        layout.addWidget(self.progress_bar)
        layout.addSpacing(10)
        layout.addWidget(self.news_box)

        self.setLayout(layout)

        QTimer.singleShot(0, lambda: NewsRenderer.getNews(self, self.news_box))

        # Start thread to perform patching
        self.copying_thread = QThread()
        self.copying_worker = CopyFiles()

    def initializePage(self):
        QTimer.singleShot(0, self.disable_back_button)

        self.copying_worker.moveToThread(self.copying_thread)
        self.copying_thread.started.connect(self.copying_worker.copy_files)

        self.copying_worker.error.connect(self.handle_error)

        self.copying_worker.finished.connect(self.logic_finished)
        self.copying_worker.finished.connect(self.copying_thread.quit)
        self.copying_worker.finished.connect(self.copying_thread.deleteLater)
        self.copying_worker.finished.connect(self.copying_thread.deleteLater)

        self.copying_thread.start()

    def isComplete(self):
        return self.copying_complete

    def disable_back_button(self):
        self.wizard().button(QWizard.WizardButton.BackButton).setEnabled(False)

    def logic_finished(self):
        self.copying_complete = True
        self.completeChanged.emit()
        QTimer.singleShot(0, self.wizard().next)

    def nextId(self):
        return 1000

    def handle_error(self, error: str):
        """Display errors thrown from the patching logic to the user"""
        QMessageBox.warning(
            self,
            "WiiLink Patcher - Warning",
            f"""An exception was encountered while copying files.

Exception:
{error}

Please report this issue in the WiiLink Discord Server (discord.gg/wiilink).""",
        )


class CopyFiles(QObject):
    error = Signal(str)
    finished = Signal(bool)

    def copy_files(self):
        global sd_path
        global sd_wad_path

        # Find existing apps folder, regardless of case
        sd_apps_path = "apps"
        for folder in os.listdir(sd_path):
            if (
                folder.lower() == "apps"
                and pathlib.Path().joinpath(sd_path, folder).is_dir()
            ):
                sd_apps_path = folder

        try:
            shutil.copytree(
                pathlib.Path().joinpath("WiiLink", "apps"),
                pathlib.Path().joinpath(sd_path, sd_apps_path),
                dirs_exist_ok=True,
            )
            shutil.copytree(
                pathlib.Path().joinpath("WiiLink", "WAD"),
                pathlib.Path().joinpath(sd_path, sd_wad_path),
                dirs_exist_ok=True,
            )
        except Exception as e:
            self.error.emit(f"{e}")

        self.finished.emit(True)
