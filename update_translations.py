# "update_translations.py", licensed under the MPL 2.0 license
# Adapted with permission from "update_translations.py" in https://github.com/NinjaCheetah/NUSGet by NinjaCheetah
# This script exists to work around an issue in PySide6 where the "pyside6-project lupdate" command doesn't work as
# expected, as it struggles to parse the paths in the .pyproject file. This does what it's meant to do for it.

import pathlib
import tomllib
import subprocess

LUPDATE_CMD = "pyside6-lupdate"

pyproject_file = pathlib.Path("pyproject.toml")
pyproject = tomllib.load(open(pyproject_file, "rb"))

files = []
for key in pyproject["tool"]["pyside6-project"]["files"]:
    files.append(pathlib.Path(key))

source_files = []
ts_files = []
for file in files:
    if file.suffix == ".ts":
        ts_files.append(file)
    elif file.suffix == ".py" or file.suffix == ".ui":
        source_files.append(file)

for target in ts_files:
    cmd = [LUPDATE_CMD] + [s for s in source_files] + ["-ts"]
    cmd.append(target)
    subprocess.run(cmd, cwd=str(pyproject_file.parent))