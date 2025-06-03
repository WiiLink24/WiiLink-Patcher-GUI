# Default option is to run build, like a Makefile
param(
    [string]$Task = "build",
    [string]$additional_args = "--standalone"
)

$buildProject = {
    Write-Host "Building WiiLink Patcher GUI..."
    pyside6-project build pyproject.toml

    $argsArray = $additional_args -split " "


    python -m nuitka --show-progress --assume-yes-for-downloads @argsArray WiiLinkPatcherGUI.py
}

$cleanBuild = {
    Write-Host "Cleaning..."
    Remove-Item -Recurse -Force WiiLinkPatcherGUI.exe, ./WiiLinkPatcherGUI.build/, ./WiiLinkPatcherGUI.dist/, ./WiiLinkPatcherGUI.onefile-build/
}

switch ($Task.ToLower()) {
    "build" {
        & $buildProject
        break
    }
    "clean" {
        & $cleanBuild
        break
    }
    default {
        Write-Host "Unknown task: $Task" -ForegroundColor Red
        Write-Host "Available tasks: build, clean"
        break
    }
}