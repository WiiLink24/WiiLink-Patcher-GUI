#!/bin/bash
# Requires :
#  - curl
#  - python3 with venv

RUNTIME_VERSION=25.08 # This version will need to be updated accordingly to the updates of the runtime (https://flathub.org/en/apps/org.freedesktop.Platform)
APP_VERSION=v1.3.1 # The version needs to be adjusted accordingly to the releases of WiiLink
ARCH_DEPENDENT_MODULES="PySide6"  # List of modules listed in requirements.txt that flatpak-pip-generator is unable to generate
BINARY_MODULES="shiboken6==6.10.2 pyside6_essentials==6.10.2 pyside6_addons==6.10.2 pyside6==6.10.2"  # Full list of modules missing from failed modules listed above

echo "=== Flatpak Manifest Configurator ==="
echo "This tool sets up the required manifests in order to fully build the Flatpak package without relying on internet"
echo

# CDing into the script folder
cd -- "$(dirname -- "${BASH_SOURCE[0]}")"

echo "==> STEP 0 - PATCHING VERSIONS INSIDE THE MANIFEST..."
sed -i "s/{{RUNTIME_VERSION}}/$RUNTIME_VERSION/" ./ca.wiilink.Patcher.yml
sed -i "s/{{APP_VERSION}}/$APP_VERSION/" ./ca.wiilink.Patcher.yml

echo "==> STEP 0 - PATCHING REQUIREMENTS..."
for module in $ARCH_DEPENDENT_MODULES
do
    echo " -> Removing $module"
    sed -i "s/$module//" ../requirements.txt
done

echo "==> STEP 1 - FETCHING THE LATEST VERSION OF THE GENERATOR...."
curl -O https://raw.githubusercontent.com/flatpak/flatpak-builder-tools/refs/heads/master/pip/flatpak-pip-generator.py

echo "==> STEP 2 - CREATING A VENV FOR THE GENERATOR..."
python -m venv --system-site-packages .venv
source .venv/bin/activate

echo "==> STEP 3 - INSTALLING DEPENDENCIES..."
pip install requirements-parser req2flatpak

echo "==> STEP 4 - GENERATING MANIFESTS..."
python ./flatpak-pip-generator.py --runtime="org.freedesktop.Sdk//$RUNTIME_VERSION" --requirements-file='../requirements.txt' --output python-deps

echo "==> STEP 6 - DOWNLOADING MISSING DEPENDENCIES WITH REQ2FLATPAK..."
python -m req2flatpak --requirements $(echo $BINARY_MODULES) --target-platforms 39-x86_64 > ./python-missing-deps.json

echo "==> STEP 5 - DELETING RUNTIME FILES..."
deactivate
rm -r ./.venv
rm ./flatpak-pip-generator.py

echo "==========> YOU ARE NOW READY TO FIRE! <=========="
