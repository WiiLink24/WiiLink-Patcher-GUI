# Using code with permission from "NUSGet.py" from NUSGet by NinjaCheetah
# https://github.com/NinjaCheetah/NUSGet

import pathlib
import tempfile
import sys
import os

patcher_url = "https://patcher.wiilink24.com"
patcher_version = "1.1.2 Nightly"

temp_dir = pathlib.Path().joinpath(tempfile.gettempdir(), "WiiLinkPatcher")
file_path = pathlib.Path(__file__).parents[1]

match sys.platform:
    case "winnt":
        import winreg

        sub_key = r"SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders"
        downloads_guid = "{374DE290-123F-4565-9164-39C4925E467B}"
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, sub_key) as key:
            output_path = pathlib.Path(winreg.QueryValueEx(key, downloads_guid)[0])
    case _:
        output_path = pathlib.Path(os.path.expanduser("~")).joinpath("Downloads")

wiilink_dir = output_path.joinpath("WiiLink")

wad_directory = wiilink_dir.joinpath("WAD")
apps_directory = wiilink_dir.joinpath("apps")
