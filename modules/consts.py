import pathlib
import tempfile

patcher_url = "https://patcher.wiilink24.com"
patcher_version = "1.0"

temp_dir = pathlib.Path().joinpath(tempfile.gettempdir(), "WiiLinkPatcher")
file_path = pathlib.Path(__file__).parents[1]

wiilink_dir = pathlib.Path().joinpath("WiiLink")

wad_directory = wiilink_dir.joinpath("WiiLink", "WAD")
