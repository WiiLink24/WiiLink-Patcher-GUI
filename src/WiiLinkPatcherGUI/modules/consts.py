# Using code with permission from "NUSGet.py" from NUSGet by NinjaCheetah
# https://github.com/NinjaCheetah/NUSGet

import pathlib
import tempfile
import platform

patcher_url = "https://patcher.wiilink24.com"
patcher_version = "1.3.2 Nightly"

temp_dir = pathlib.Path().joinpath(tempfile.gettempdir(), "WiiLinkPatcher")
file_path = pathlib.Path(__file__).parents[1]
if platform.system() == "Darwin":
    file_path = file_path.parent
