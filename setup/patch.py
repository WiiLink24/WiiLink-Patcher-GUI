import pathlib
import libWiiPy
import tempfile
import shutil
import bsdiff4

from PySide6.QtCore import QObject, Signal, QTimer, QThread
from PySide6.QtWidgets import (
    QMessageBox,
    QWizardPage,
    QLabel,
    QProgressBar,
    QVBoxLayout,
    QWizard,
)

from .enums import *
from .download import (
    download_patch,
    download_file,
    download_agc,
    download_osc_app,
    download_title_contents,
    download_channel,
    download_spd,
    download_today_tomorrow,
    download_eula,
)
from .newsRenderer import NewsRenderer

patcher_url = "https://patcher.wiilink24.com"
temp_dir = pathlib.Path().joinpath(tempfile.gettempdir(), "WiiLinkPatcher")
wad_directory = pathlib.Path().joinpath("WiiLink", "WAD")

title_directory = pathlib.Path().joinpath(temp_dir, "Unpack")


def apply_bsdiff_patches(
    channel_name: str, patch_files: dict[str, int], title: libWiiPy.title.Title
):
    """Download and apply bsdiff patches to the app files specified

    Args:
        channel_name: The directory name of the channel's patches on the server
        patch_files: A dictionary containing the file names for the patches, and the index they are applied to
        title: The libWiiPy title which has the contents to be patched

    Returns:
        A libWiiPy title, containing the patched contents in place of the stock ones"""

    # Apply patches
    for patch, index in patch_files.items():
        print(f" - Patching content {index + 1}...")

        print("   - Downloading patch...")

        try:
            patch_binary = download_patch(channel_name.lower(), patch)
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


def patch_channel(
    channel_name: str,
    channel_title: str,
    title_id: str,
    patch_files: dict[str, int],
    channel_type: ChannelTypes,
    version: int = None,
    region: Regions = None,
    language: Languages = None,
    additional_files: dict[str, pathlib.Path] = None,
    wfc_network: WFCNetworks = None,
):
    """Download a specified channel from NUS, and apply patches to the channel's app files

    Args:
        channel_name: The directory name of the channel's files on the server
        channel_title: The title of the WAD file that will be outputted
        title_id: The ID of the title to download from NUS
        patch_files: A dictionary containing the file names for the patches, and the index they are applied to
        channel_type: The type of the channel to be patched
        version: Optionally, specify the version of the channel to download from NUS
        region: Optionally, specify the region of the channel to be appended to the file name
        language: Optionally, specify the language of the channel to be appended to the file name
        wfc_network: Optionally, specify the WFC Network of the channel to be appended to the file name
        additional_files: Optionally, specify additional files that need to be downloaded for the title

    Returns:
        None"""
    print(f"Patching {channel_title}:")
    file_url = f"{patcher_url}/{channel_name.lower()}/{title_id}"

    wad_directory.mkdir(exist_ok=True)

    match channel_type:
        case ChannelTypes.WiiConnect24:
            name_data = [region]
        case ChannelTypes.Regional:
            name_data = [language]
        case ChannelTypes.WFC:
            name_data = [region, wfc_network]
        case _:
            name_data = None

    if name_data:
        wad_name = f"{channel_title}"
        for index in range(len(name_data)):
            if name_data[index] is not None:
                if index % 2 == 0:
                    wad_name = f"{wad_name} [{name_data[index].name}]"
                else:
                    wad_name = f"{wad_name} ({name_data[index].name}"

        output_wad = pathlib.Path().joinpath(wad_directory, f"{wad_name}.wad")
    else:
        output_wad = pathlib.Path().joinpath(wad_directory, f"{channel_title}.wad")

    if additional_files is not None:
        title_directory.mkdir(parents=True)
        for file, destination in additional_files.items():
            url = f"{file_url}{file}"
            download_file(url, destination)

    title = libWiiPy.title.Title()

    if not pathlib.Path().joinpath(title_directory, f"tmd.{version}").exists():
        tmd = libWiiPy.title.download_tmd(title_id, version)
    else:
        tmd = open(
            pathlib.Path().joinpath(title_directory, f"tmd.{version}"), "rb"
        ).read()

    title.load_tmd(tmd)

    if not pathlib.Path().joinpath(title_directory, "tik").exists():
        ticket = libWiiPy.title.download_ticket(title_id)
    else:
        ticket = open(pathlib.Path().joinpath(title_directory, "tik"), "rb").read()

    title.load_ticket(ticket)

    cert = libWiiPy.title.download_cert_chain()

    title.load_cert_chain(cert)

    title = download_title_contents(title, title_id)

    title = apply_bsdiff_patches(channel_name, patch_files, title)

    print(" - Packing WAD...")

    try:
        open(output_wad, "wb").write(title.dump_wad())
    except Exception as e:
        print("   - Failed!")
        raise ValueError(e)
    else:
        print("   - Done!")

    # Delete temporary directory, ready for next channel to be patched
    if title_directory.exists() and title_directory.is_dir():
        shutil.rmtree(title_directory)


def nc_patch(region: Regions):
    """Patch the Nintendo Channel for the specified region

    Args:
        region: The region of Nintendo Channel to download and patch

    Returns:
        None"""
    region_data = {
        Regions.USA: ["0001000148415445", "Nintendo Channel"],
        Regions.PAL: ["0001000148415450", "Nintendo Channel"],
        Regions.Japan: ["000100014841544a", "Minna no Nintendo Channel"],
    }

    channel_id = region_data[region][0]
    channel_title = region_data[region][1]

    patches = {f"NC_1_{region.name}.bsdiff": 1}

    additional_files = {".tik": pathlib.Path().joinpath(title_directory, "tik")}

    patch_channel(
        "nc",
        channel_title,
        channel_id,
        patches,
        ChannelTypes.WiiConnect24,
        1792,
        region,
        None,
        additional_files,
    )


def forecast_patch(region: Regions, platform: Platforms):
    """Patch the Forecast Channel for the specified region

    Args:
        region: The region of Forecast Channel to download and patch
        platform: The platform which the channel will be downloaded to (used to determine which AnyGlobe Changer version to download)

    Returns:
        None"""
    title_ids = {
        Regions.USA: "0001000248414645",
        Regions.PAL: "0001000248414650",
        Regions.Japan: "000100024841464a",
    }

    channel_id = title_ids[region]

    patches = {
        "Forecast_1.bsdiff": 1,
        "Forecast_5.bsdiff": 5,
    }

    # Download AnyGlobe Changer to allow setting custom regions
    download_agc(platform)

    patch_channel(
        "forecast",
        "Forecast Channel",
        channel_id,
        patches,
        ChannelTypes.WiiConnect24,
        7,
        region,
    )


def news_patch(region: Regions):
    """Patch the News Channel for the specified region

    Args:
        region: The region of News Channel to download and patch

    Returns:
        None"""
    title_ids = {
        Regions.USA: "0001000248414745",
        Regions.PAL: "0001000248414750",
        Regions.Japan: "000100024841474a",
    }

    channel_id = title_ids[region]

    patches = {"News_1.bsdiff": 1}

    patch_channel(
        "news",
        "News Channel",
        channel_id,
        patches,
        ChannelTypes.WiiConnect24,
        7,
        region,
    )


def evc_patch(region: Regions):
    """Patch the Everybody Votes Channel for the specified region

    Args:
        region: The region of the Everybody Votes Channel to download and patch

    Returns:
        None"""
    title_ids = {
        Regions.USA: "0001000148414a45",
        Regions.PAL: "0001000148414a50",
        Regions.Japan: "0001000148414a4a",
    }

    channel_id = title_ids[region]

    patches = {f"EVC_1_{region.name}.bsdiff": 1}

    additional_files = {".tik": pathlib.Path().joinpath(title_directory, "tik")}

    patch_channel(
        "evc",
        "Everybody Votes Channel",
        channel_id,
        patches,
        ChannelTypes.WiiConnect24,
        512,
        region,
        None,
        additional_files,
    )

    region_select_patch(region)


def region_select_patch(region: Regions):
    """Patch Region Select for the specified region

    Args:
        region: The region of Region Select to download and patch

    Returns:
        None"""
    title_ids = {
        Regions.USA: "0001000848414c45",
        Regions.PAL: "0001000848414c50",
        Regions.Japan: "0001000848414c4a",
    }

    channel_id = title_ids[region]

    patches = {"RegSel_1.bsdiff": 1}

    patch_channel(
        "regsel",
        "Region Select",
        channel_id,
        patches,
        ChannelTypes.WiiConnect24,
        2,
        region,
    )


def check_mii_out_channel_patch(region: Regions):
    """Patch the Check Mii Out Channel for the specified region

    Args:
        region: The region of Check Mii Out Channel to download and patch

    Returns:
        None"""
    region_data = {
        Regions.USA: ["0001000148415045", "Check Mii Out Channel"],
        Regions.PAL: ["0001000148415050", "Mii Contest Channel"],
        Regions.Japan: ["000100014841504a", "Mii Contest Channel"],
    }

    channel_id = region_data[region][0]
    channel_title = region_data[region][1]

    patches = {f"CMOC_1_{region.name}.bsdiff": 1}

    additional_files = {".tik": pathlib.Path().joinpath(title_directory, "tik")}

    patch_channel(
        "cmoc",
        channel_title,
        channel_id,
        patches,
        ChannelTypes.WiiConnect24,
        512,
        region,
        additional_files=additional_files,
    )


def wii_room_patch(language: Languages):
    """Patch Wii Room for the specified language

    Args:
        language: The language to patch Wii Room into

    Returns:
        None"""
    patches = {f"WiinoMa_2_{language.name}.bsdiff": 2}

    if language == Languages.Russian:
        patches.update(
            {
                "WiinoMa_1_Russian.bsdiff": 1,
                "WiinoMa_3_Russian.bsdiff": 3,
                "WiinoMa_4_Russian.bsdiff": 4,
                "WiinoMa_9_Russian.bsdiff": 9,
                "WiinoMa_C_Russian.bsdiff": 12,
                "WiinoMa_D_Russian.bsdiff": 13,
                "WiinoMa_E_Russian.bsdiff": 14,
            }
        )
    elif language == Languages.Portuguese:
        patches.update(
            {
                "WiinoMa_1_Portuguese.bsdiff": 1,
                "WiinoMa_3_Portuguese.bsdiff": 3,
                "WiinoMa_4_Portuguese.bsdiff": 4,
                "WiinoMa_D_Portuguese.bsdiff": 13,
            }
        )
    else:
        patches.update({"WiinoMa_1_Universal.bsdiff": 1})

    if language == Languages.Japan:
        channel_title = "Wii no Ma"
    else:
        channel_title = "Wii Room"
        patches.update({"WiinoMa_0_Universal.bsdiff": 0})

    patch_channel(
        "WiinoMa",
        channel_title,
        "000100014843494a",
        patches,
        ChannelTypes.Regional,
        language=language,
    )


def digicam_patch(translated: bool):
    """Patch the Digicam Prints Channel for English or Japanese

    Args:
        translated: Whether to patch Digicam to English, or leave it in Japanese

    Returns:
        None"""
    if translated:
        language = Languages.English
        channel_title = "Photo Prints Channel"
        patches = {
            "Digicam_0_English.bsdiff": 0,
            "Digicam_1_English.bsdiff": 1,
            "Digicam_2_English.bsdiff": 2,
        }
    else:
        language = Languages.Japan
        channel_title = "Digicam Print Channel"
        patches = {"Digicam_1_Japan.bsdiff": 1}

    patch_channel(
        "Digicam",
        channel_title,
        "000100014843444a",
        patches,
        ChannelTypes.Regional,
        language=language,
    )


def demae_patch(translated: bool, demae_version: DemaeConfigs, region: Regions):
    """Patch the Demae Channel for Fake Ordering or Domino's, in English or Japanese

    Args:
        translated: Whether to patch Demae to English, or leave it in Japanese
        demae_version: The version of Demae to patch (i.e. standard "fake" ordering or Domino's)
        region: The region of the console Demae will be installed to, to determine the region of Internet Channel to download for Demae Domino's order tracking

    Returns:
        None"""
    patches = {}
    channel_name = ""

    match demae_version:
        case DemaeConfigs.Standard:
            if translated:
                patches = {
                    "Demae_0_English.bsdiff": 0,
                    "Demae_1_English.bsdiff": 1,
                    "Demae_2_English.bsdiff": 2,
                }
            else:
                patches = {"Demae_1_Japan.bsdiff": 1}

            channel_name = "Demae"

        case DemaeConfigs.Dominos:
            patches = {
                "Dominos_0.bsdiff": 0,
                "Dominos_1.bsdiff": 1,
                "Dominos_2.bsdiff": 2,
            }

            ic_ids = {
                Regions.USA: "0001000148414445",
                Regions.PAL: "0001000148414450",
                Regions.Japan: "000100014841444a",
            }

            ic_id = ic_ids[region]

            channel_name = "Dominos"

            # Download WiiLink Account Linker, as this is needed for Demae Dominos
            download_osc_app("wiilink-account-linker")

            # Download Internet Channel to allow on-console order tracking
            download_channel("Internet Channel", ic_id, 1024, region)

    if translated:
        channel_title = "Food Channel"
        language = Languages.English
    else:
        channel_title = "Demae Channel"
        language = Languages.Japan

    patch_channel(
        channel_name,
        f"{channel_title} ({demae_version.name})",
        "000100014843484a",
        patches,
        ChannelTypes.Regional,
        language=language,
    )


def kirby_tv_patch():
    """Patch the Kirby TV Channel

    Returns:
        None"""
    patches = {"ktv_2.bsdiff": 2}

    additional_files = {
        ".tmd": pathlib.Path().joinpath(title_directory, f"tmd.257"),
        ".tik": pathlib.Path().joinpath(title_directory, "tik"),
    }

    patch_channel(
        "ktv",
        "Kirby TV Channel",
        "0001000148434d50",
        patches,
        ChannelTypes.Regional,
        additional_files=additional_files,
    )


def wiispeak_patch(region: Regions, network: WFCNetworks):
    """Patch the Wii Speak Channel for the specified region and WFC network

    Args:
        region: The region of Wii Speak Channel to download and patch
        network: The WFC network to patch Wii Speak to use

    Returns:
        None"""
    patches = {f"WiiSpeak_1_{region.name}.bsdiff": 1}

    title_ids = {
        Regions.USA: "0001000148434645",
        Regions.PAL: "0001000148434650",
        Regions.Japan: "000100014843464a",
    }

    channel_id = title_ids[region]

    patch_channel(
        "ws",
        "Wii Speak Channel",
        channel_id,
        patches,
        ChannelTypes.WFC,
        region=region,
        wfc_network=network,
    )


class PatchingPage(QWizardPage):
    platform: Platforms
    region: Regions
    selected_channels: list
    regional_channels: bool = False
    setup_type: SetupTypes

    patching_complete = False
    percentage: int
    status: str
    error = ""

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setTitle(self.tr("Patching in progress"))
        self.setSubTitle(self.tr("Please wait while the patcher works its magic!"))

        self.label = QLabel(self.tr("Downloading files..."))
        self.progress_bar = QProgressBar(self)

        self.news_box = NewsRenderer.createNewsBox(self)

        layout = QVBoxLayout()
        layout.addWidget(self.label)
        layout.addWidget(self.progress_bar)
        layout.addSpacing(10)
        layout.addWidget(self.news_box)

        self.setLayout(layout)

        QTimer.singleShot(0, lambda: NewsRenderer.getNews(self, self.news_box))

        # Start thread to perform patching
        self.logic_thread = QThread()
        self.logic_worker = PatchingWorker()

    def initializePage(self):
        QTimer.singleShot(0, self.disable_back_button)

        # Setup variables
        self.logic_worker.setup_type = self.setup_type
        self.logic_worker.platform = self.platform
        self.logic_worker.region = self.region
        self.logic_worker.regional_channels = self.regional_channels
        self.logic_worker.selected_channels = ["download"] + self.selected_channels

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
        self.error = error

        QMessageBox.warning(
            self,
            "WiiLink Patcher - Warning",
            f"""An exception was encountered while patching.

Exception:
{error}

Please report this issue in the WiiLink Discord Server (discord.gg/wiilink).""",
        )


class PatchingWorker(QObject):
    platform: Platforms
    region: Regions
    selected_channels: list
    regional_channels: bool = False
    setup_type: SetupTypes

    is_patching_complete: bool
    finished = Signal(bool)
    broadcast_percentage = Signal(int)
    broadcast_status = Signal(str)
    error = Signal(str)

    def patching_functions(self):

        percentage_increment = 100 / len(self.selected_channels)

        percentage = 0

        patch_functions = {
            "download": lambda: self.download_supporting_apps(),
            "scr": lambda: download_osc_app("system-channel-restorer"),
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
            "cmoc_us": lambda: check_mii_out_channel_patch(Regions.USA),
            "cmoc_eu": lambda: check_mii_out_channel_patch(Regions.PAL),
            "cmoc_jp": lambda: check_mii_out_channel_patch(Regions.Japan),
            "wiiroom_en": lambda: wii_room_patch(Languages.English),
            "wiiroom_es": lambda: wii_room_patch(Languages.Spanish),
            "wiiroom_fr": lambda: wii_room_patch(Languages.French),
            "wiiroom_de": lambda: wii_room_patch(Languages.German),
            "wiiroom_it": lambda: wii_room_patch(Languages.Italian),
            "wiiroom_nl": lambda: wii_room_patch(Languages.Dutch),
            "wiiroom_ptbr": lambda: wii_room_patch(Languages.Portuguese),
            "wiiroom_ru": lambda: wii_room_patch(Languages.Russian),
            "wiiroom_jp": lambda: wii_room_patch(Languages.Japan),
            "digicam_en": lambda: digicam_patch(True),
            "digicam_jp": lambda: digicam_patch(False),
            "food_en": lambda: demae_patch(True, DemaeConfigs.Standard, self.region),
            "food_jp": lambda: demae_patch(False, DemaeConfigs.Standard, self.region),
            "dominos": lambda: demae_patch(True, DemaeConfigs.Dominos, self.region),
            "ktv": lambda: kirby_tv_patch(),
            "ws_us": lambda: wiispeak_patch(Regions.USA, WFCNetworks.Wiimmfi),
            "ws_eu": lambda: wiispeak_patch(Regions.PAL, WFCNetworks.Wiimmfi),
            "ws_jp": lambda: wiispeak_patch(Regions.Japan, WFCNetworks.Wiimmfi),
            "tatc_eu": lambda: download_today_tomorrow(Regions.PAL),
            "tatc_jp": lambda: download_today_tomorrow(Regions.Japan),
            "ic_us": lambda: download_channel(
                "Internet Channel", "0001000148414445", 1024, Regions.USA
            ),
            "ic_eu": lambda: download_channel(
                "Internet Channel", "0001000148414450", 1024, Regions.PAL
            ),
            "ic_jp": lambda: download_channel(
                "Internet Channel", "000100014841444a", 1024, Regions.Japan
            ),
        }

        patch_status = {
            "download": self.tr("Downloading files..."),
            "scr": self.tr("Downloading System Channel Restorer..."),
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
            "ktv": self.tr("Patching Kirby TV Channel..."),
            "ws_us": self.tr("Patching Wii Speak Channel (USA)..."),
            "ws_eu": self.tr("Patching Wii Speak Channel (PAL)..."),
            "ws_jp": self.tr("Patching Wii Speak Channel (Japan)..."),
            "tatc_eu": self.tr("Downloading Today and Tomorrow Channel (PAL)..."),
            "tatc_jp": self.tr("Downloading Today and Tomorrow Channel (Japan)..."),
            "ic_us": self.tr("Downloading Internet Channel (USA)..."),
            "ic_eu": self.tr("Downloading Internet Channel (PAL)..."),
            "ic_jp": self.tr("Downloading Internet Channel (Japan)..."),
        }

        for channel in self.selected_channels:
            try:
                self.broadcast_status.emit(patch_status[channel])
                patch_functions[channel]()
            except KeyError:
                print(f"Invalid key: {channel}")
                self.error.emit(f"Invalid key: {channel}")
            except Exception as e:
                self.error.emit(f"{e}")
            finally:
                percentage += percentage_increment
                self.broadcast_percentage.emit(round(percentage))

        self.finished.emit(True)

    def download_supporting_apps(self):
        match self.setup_type:
            case SetupTypes.Extras:
                if self.platform != Platforms.Dolphin:
                    download_osc_app("yawmME")
            case _:
                if self.platform != Platforms.Dolphin:
                    download_osc_app("yawmME")
                    download_osc_app("sntp")

                if self.platform == Platforms.vWii:
                    download_eula(self.region)

                if self.regional_channels and self.region != Regions.Japan:
                    download_spd()

                download_osc_app("Mail-Patcher")
