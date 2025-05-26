import os
import requests
import tempfile
import zipfile
import libWiiPy
import shutil
import json
import pathlib

from .enums import *

patcher_url = "https://patcher.wiilink24.com"
temp_dir = pathlib.Path().joinpath(tempfile.gettempdir(), "WiiLinkPatcher")
wad_directory = pathlib.Path().joinpath("WiiLink", "WAD")

osc_enabled = True


# Using code from "commands/title/nus.py" from WiiPy by NinjaCheetah
# https://github.com/NinjaCheetah/WiiPy


def connection_test():
    """Function to ensure the patcher is able to connect to the patcher server and NUS

    Returns:
        "success" - Both connection tests succeeded

        "fail-patcher" - The patcher failed to connect to patcher.wiilink24.com

        "fail-nus" - The patcher failed to connect to NUS"""
    print("Testing internet connection:")
    patcher_test = f"{patcher_url}/connectiontest.txt"
    patcher_expected = b"If the patcher can read this, the connection test succeeds.\n"

    print(" - Checking connection to patcher server...")
    patcher_response = requests.get(url=patcher_test, timeout=10)

    if patcher_response.status_code != 200:
        print(
            f"""Connection test failed!
Got HTTP code {patcher_response.status_code}.
URL: {patcher_test}"""
        )
        return "fail-patcher"

    patcher_content = patcher_response.content

    if patcher_content != patcher_expected:
        print(
            f"""Unexpected response!
Expected: {patcher_expected}
Received: {patcher_response}"""
        )
        return "fail-patcher"

    print("   - Success!")

    nus_test = "http://nus.cdn.shop.wii.com/ccs/download/000100014841564a/tmd"

    print(" - Checking connection to NUS...")
    nus_request = requests.get(
        url=nus_test, headers={"User-Agent": "wii libnup/1.0"}, timeout=10
    )
    if nus_request.status_code != 200:
        print(
            f"""Connection test failed!
Got HTTP code {nus_request.status_code}.
URL: {nus_test}"""
        )
        return "fail-nus"

    print("   - Success!")

    osc_test = "https://hbb1.oscwii.org/api/v4/information"

    print(" - Checking connection to OSC...")
    try:
        osc_request = requests.get(osc_test, timeout=10)
    except Exception as e:
        print(
            f"""An exception occurred while connecting to OSC!

Exception:
{e}"""
        )
        return "fail-osc"

    if osc_request.status_code != 200:
        print(
            f"""Connection test failed!
Got HTTP code {osc_request.status_code}.
URL: {osc_test}"""
        )
        return "fail-osc"

    print("   - Success!")

    return "success"


def get_latest_version() -> str:
    """Gets the tag of the latest stable release from the GitHub API

    Returns:
        The latest tag from the GitHub API"""
    api_url = (
        "https://api.github.com/repos/WiiLink24/WiiLink-Patcher-GUI/releases/latest"
    )

    api_response_raw = download_file(api_url)
    api_response = json.loads(api_response_raw)

    latest_version = api_response["tag_name"].replace("v", "")

    return latest_version


def download_translation(language: str):
    """Downloads a specified translation file from the server, ready to be loaded into the app

    Args:
        language: The two-character code of the language of the translation to download

    Returns:
        None"""
    translation_url = f"{patcher_url}/qt-lang/translation_{language}.qm"

    translation_dir = pathlib.Path().joinpath(__file__, "translations")
    os.makedirs(translation_dir, exist_ok=True)

    download_file(translation_url, translation_dir)


def download_translation_dict():
    """Downloads and returns a dictionary of available languages from the server

    Returns:
        The dictionary of available translations"""
    url = f"{patcher_url}/qt-lang/languages.json"

    raw_json = download_file(url)

    translation_dict = json.loads(raw_json)

    return translation_dict


def download_file(url: str, destination: str | pathlib.Path = None):
    """Simple function to download files from a specified URL

    Args:
        url: The URL to download the file from
        destination: Optionally, the specified location to write the file to

    Returns:
        The binary contents of the URL, or None if the destination is specified"""
    response = requests.get(url=url)
    if response.status_code != 200:
        print(
            f"""Received HTTP status code {response.status_code}!
File URL: {url}"""
        )
        raise ValueError(
            f"""Received HTTP status code {response.status_code}!
File URL: {url}"""
        )
    else:
        file = response.content
        if destination is not None:
            open(destination, "wb").write(file)
            return None
        else:
            return file


class DownloadOSCApp:
    osc_enabled: bool = True

    def __init__(self, app_name: str):
        """Downloads an app from the OSC to 'WiiLink/apps'

        Args:
            app_name: The name of the app on OSC to download

        Returns:
            None"""

        if not self.osc_enabled:
            print(f"Downloading {app_name} skipped - OSC downloading is disabled!")
            return

        app_path = pathlib.Path().joinpath("WiiLink", "apps", app_name)

        os.makedirs(app_path, exist_ok=True)

        print(f"Downloading {app_name} from OSC:")

        print(" - Downloading boot.dol...")
        download_file(
            f"https://hbb1.oscwii.org/unzipped_apps/{app_name}/apps/{app_name}/boot.dol",
            pathlib.Path().joinpath(app_path, "boot.dol"),
        )
        print("   - Done!")
        print(" - Downloading meta.xml...")
        download_file(
            f"https://hbb1.oscwii.org/unzipped_apps/{app_name}/apps/{app_name}/meta.xml",
            pathlib.Path().joinpath(app_path, "meta.xml"),
        )
        print("   - Done!")
        print(" - Downloading icon.png...")
        download_file(
            f"https://hbb1.oscwii.org/api/v3/contents/{app_name}/icon.png",
            pathlib.Path().joinpath(app_path, "icon.png"),
        )
        print("   - Done!")


def download_agc(platform: Platforms):
    """Downloads AnyGlobe Changer, either from OSC or GitHub, depending on the user's platform

    Args:
        platform: The platform the app will be used on, to determine which source to download from

    Returns:
        None"""
    if platform != Platforms.Dolphin:
        DownloadOSCApp("AnyGlobe_Changer")
    else:
        # Dolphin users need v1.0 of AnyGlobe Changer, as the latest OSC release doesn't work with Dolphin, for some reason.
        app_path = pathlib.Path().joinpath(temp_dir, "AGC")
        agc_dest = pathlib.Path().joinpath(app_path, "AGC.zip")

        os.makedirs(app_path)

        print("Downloading AnyGlobe Changer from GitHub:")
        print(" - Downloading release...")
        download_file(
            "https://github.com/fishguy6564/AnyGlobe-Changer/releases/download/1.0/AnyGlobe.Changer.zip",
            agc_dest,
        )
        print("   - Done!")
        print(" - Extracting release...")
        with zipfile.ZipFile(agc_dest, "r") as agc_zip:
            agc_zip.extractall(pathlib.Path().joinpath("WiiLink"))
        print("   - Done!")

        shutil.rmtree(app_path)


def download_spd():
    """Downloads the SPD WAD from the WiiLink Patcher server

    Returns:
        None"""
    spd_url = f"{patcher_url}/spd/WiiLink_SPD.wad"

    os.makedirs(wad_directory, exist_ok=True)

    print("Downloading WiiLink Address Settings:")
    download_file(
        spd_url,
        pathlib.Path().joinpath(
            wad_directory, "INSTALL ME - WiiLink Address Settings.wad"
        ),
    )
    print(" - Done!")


def download_patch(folder: str, patch_name: str):
    """Downloads a patch from the WiiLink Patcher server

    Args:
        folder: The folder on the server which the patch resides within
        patch_name: The filename of the patch on the server

    Returns:
        The binary contents of the patch"""
    patch_url = f"{patcher_url}/bsdiff/{folder}/{patch_name}.bsdiff"

    patch = download_file(patch_url)

    return patch


def download_title_contents(title: libWiiPy.title.Title):
    """Download the contents for a title from NUS

    Args:
        title: The libWiiPy title to download the contents for

    Returns:
        A libWiiPy title, containing the downloaded contents"""

    # Load the content records from the TMD, and begin iterating over the records.
    title.load_content_records()
    content_list = []

    for content in range(len(title.tmd.content_records)):
        # Generate the content file name by converting the Content ID to hex and then removing the 0x.
        content_file_name = hex(title.tmd.content_records[content].content_id)[2:]
        while len(content_file_name) < 8:
            content_file_name = "0" + content_file_name
        print(
            f" - Downloading content {content + 1} of {len(title.tmd.content_records)} "
            f"(Content ID: {title.tmd.content_records[content].content_id}, "
            f"Size: {title.tmd.content_records[content].content_size} bytes)..."
        )
        content_list.append(
            libWiiPy.title.download_content(
                title.tmd.title_id, title.tmd.content_records[content].content_id
            )
        )
        print("   - Done!")

    title.content.content_list = content_list

    return title
