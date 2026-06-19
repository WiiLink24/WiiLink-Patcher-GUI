#!/bin/bash

wget https://raw.githubusercontent.com/flatpak/flatpak-builder-tools/master/pip/flatpak-pip-generator.py -O flatpak-pip-generator.py
python flatpak-pip-generator.py -r requirements.txt -o python3-requirements.json
flatpak-builder --force-clean flatpak-build-dir --install-deps-from flathub ca.wiilink.Patcher.json