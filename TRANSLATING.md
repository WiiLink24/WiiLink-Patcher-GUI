# Translating WiiLink Patcher

To translate the patcher, you'll need some things installed on your PC first:
- [Git](https://git-scm.org)
- [Python 3.13](https://www.python.org/downloads/release/python-3139/)

### Step 1: Forking and cloning the repository
First, you'll want to fork, clone and enter this repository.

Follow [this link](https://github.com/WiiLink24/WiiLink-Patcher-GUI/fork) to fork the repo to your GitHub account, then run the following commands to clone and enter your fork:
```
# If you named your fork something other than WiiLink-Patcher-GUI, make sure to swap out the repository name in these commands.

git clone https://github.com/<your username>/WiiLink-Patcher-GUI
cd WiiLink-Patcher-GUI/
```
After this, create a venv and activate it:
```
python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS, Linux and other OSes
source .venv/bin/activate
```
Now, you can install the dependencies for the patcher:
```
pip install --upgrade -r requirements.txt
```

### Step 2: Adding your language
If your language does not already exist in the patcher, open `pyproject.toml` in a text editor, and copy and paste the sample language line into the `files` list, remembering to swap `XX` for your language's two-letter code.

### Step 3: Updating translation files
Run the following command to update all translation files, ensuring all the latest strings are present for you to translate:
```
python update_translations.py
```

### Step 4: Translating
Qt Linguist is included as part of the `PySide6` package you installed during Step 1. To launch Qt Linguist, use the appropriate command for your platform, replacing `<ver>` with the version of Python you installed (for example, `3.12`).

```
# Windows
.venv\lib\python<ver>\site-packages\PySide6\linguist.exe

# macOS
open .venv/lib/python<ver>/site-packages/PySide6/Linguist.app

# Linux and other Unix-likes
./.venv/lib/python<ver>/site-packages/PySide6/linguist
```
If you have Qt Linguist installed system-wide already, you can use that instead. These steps are included primarily for those who don't, since installing the Qt Platform Tools on Windows or macOS requires having a Qt account.

Once you've launched Qt Linguist, you can open the `.ts` file for your language in it.

We have a localisation sheet available [here](https://docs.google.com/spreadsheets/d/1uNqUGsfe1Y-CuVvV-UaVUPdde-OhkweanIRUk5XBhj8) with channel names in it. Please use the channel names from this spreadsheet to help keep these strings consistent with what we use elsewhere!

### Step 5: Pushing
Finally, commit and push your changes to your fork. Then, open a pull request in this repository to add your language!