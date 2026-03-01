# Using code with permission from "NUSGet.py" from NUSGet by NinjaCheetah
# https://github.com/NinjaCheetah/NUSGet

import pathlib
import tempfile

patcher_url = "https://patcher.wiilink24.com"
patcher_version = "1.3.2 Nightly"

temp_dir = pathlib.Path().joinpath(tempfile.gettempdir(), "WiiLinkPatcher")
file_path = pathlib.Path(__file__).parents[1]
print(file_path)
