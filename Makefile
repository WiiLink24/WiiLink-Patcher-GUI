CC=python -m nuitka
ARCH_FLAGS?=

all:
	pyside6-project build
	$(CC) --show-progress --assume-yes-for-downloads WiiLinkPatcherGUI.py $(ARCH_FLAGS) -o WiiLinkPatcherGUI

clean:
	rm WiiLinkPatcherGUI
	rm -rd WiiLinkPatcherGUI.build/
	rm -rd WiiLinkPatcherGUI.dist/
	rm -rd WiiLinkPatcherGUI.onefile-build/