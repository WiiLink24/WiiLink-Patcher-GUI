import pathlib
import tempfile

patcher_url = "https://patcher.wiilink24.com"
patcher_version = "1.1.2 Nightly"

temp_dir = pathlib.Path().joinpath(tempfile.gettempdir(), "WiiLinkPatcher")
file_path = pathlib.Path(__file__).parents[1]

if file_path.resolve().as_posix().endswith(".app/Contents/MacOS"):
    output_path = file_path.parents[2]
else:
    output_path = pathlib.Path()

wiilink_dir = output_path.joinpath("WiiLink")

wad_directory = wiilink_dir.joinpath("WAD")
