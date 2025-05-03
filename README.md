# WiiLink Patcher GUI
WiiLink Patcher GUI is a Python program built around the excellent [libWiiPy](https://github.com/NinjaCheetah/libWiiPy) to make WiiLink patching a simple process, with a streamlined graphical user interface.

## Downloading
You can download the latest release from the [Releases Page](https://github.com/WiiLink24/WiiLink-Patcher-GUI/releases).

> **NOTE:** In **Windows**, your antivirus may flag the **patcher** as malware. This is a **false positive**, and you can safely ignore it. If you are still unsure, you can inspect the source code, and/or compile it yourself for extra verification. You can also temporarily disable your antivirus to download the patcher, or add an exception for it if you put it in a dedicated folder.

## Translating
To contribute translations, refer to [this](TRANSLATING.md).

## Compiling
- Clone the repository to your computer
```
git clone https://github.com/WiiLink24/WiiLink-Patcher-GUI
```
- Enter the repository
```
cd WiiLink-Patcher-GUI/
```
- Create a venv
```
python -m venv .venv
```
- Activate the venv
```
# Windows
.venv\Scripts\activate

# macOS, Linux and other OSes
source .venv/bin/activate
```
- Install build dependencies
```
pip install --upgrade -r requirements.txt
```
- Build the project
```
# Windows
.\build.ps1

# macOS, Linux and other OSes
make all
```

## Special thanks
Special thanks to @NinjaCheetah for all his help with this project, and his work on libWiiPy.