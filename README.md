# WiiLink Patcher GUI
WiiLink Patcher GUI is a Python program built around the excellent [libWiiPy](https://github.com/NinjaCheetah/libWiiPy) to make WiiLink patching a simple process, with a streamlined graphical user interface.

## Downloading
You can download the latest release from the [Releases Page](https://github.com/WiiLink24/WiiLink-Patcher-GUI/releases).

### System Requirements
| Operating System | Minimum Version              |
|------------------|------------------------------|
| Windows          | Windows 10 1809             |
| macOS            | macOS Monterey           |
| Linux            | Ubuntu 22.04 (or equivalent) |

> [!TIP]
> Don't meet these system requirements? Check out our [CLI Patcher](https://github.com/WiiLink24/WiiLink24-Patcher) instead.

> **NOTE:** In **Windows**, your antivirus may flag the **patcher** as malware. This is a **false positive**, and you can safely ignore it. If you are still unsure, you can inspect the source code, and/or compile it yourself for extra verification. You can also temporarily disable your antivirus to download the patcher, or add an exception for it if you put it in a dedicated folder.

## Troubleshooting

### Linux
- ```qt.qpa.plugin: Could not load the Qt platform plugin "xcb" in "" even though it was found.```:
> - This is a common issue on Debian, Ubuntu and their derivatives (i.e. Linux Mint). To resolve this issue, install the `libxcb-cursor-dev` package on your system.

## Translating
To contribute translations, refer to [this](TRANSLATING.md).

## Contributing
We appreciate all contributions to this repository, big and small! If you're contributing to code, make sure to run black before submitting a pull request:
```
python -m black .
```

## Compiling
To compile the patcher, you will first need to install a few dependencies:
> - [Python 3.13](https://www.python.org/downloads/release/python-3139/) (the patcher has only been tested on Python 3.12+)
> - [Git](https://git-scm.com) (optional but highly recommended)

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

## Sponsors
<table>
  <tr>
    <td><img src="https://github.com/user-attachments/assets/bd599cbc-d860-41da-91a8-c1e70a57605d" alt="SignPath Logo"></img></td>
    <td>Free code signing on Windows provided by <a href="https://about.signpath.io">SignPath.io</a>, certificate by <a href="https://signpath.org">SignPath Foundation</a></td>
  </tr>
</table>

## Special thanks
Special thanks to [@NinjaCheetah](https://github.com/NinjaCheetah) for all his help with this project, and his work on libWiiPy and libTWLPy.
