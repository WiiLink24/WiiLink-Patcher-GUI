import pathlib
import tempfile
import os

patcher_url = "https://patcher.wiilink24.com"
patcher_version = "1.1.2 Nightly"

temp_dir = pathlib.Path().joinpath(tempfile.gettempdir(), "WiiLinkPatcher")
file_path = pathlib.Path(__file__).parents[1]

output_path = pathlib.Path(os.getcwd())

wiilink_dir = output_path.joinpath("WiiLink")

wad_directory = wiilink_dir.joinpath("WAD")
