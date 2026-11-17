@echo off
rem Launch the pyTIARA desktop app using the project environment (created by install.bat)
if not exist "%~dp0env\pythonw.exe" (
  echo pyTIARA is not installed yet - run install.bat in this folder first.
  pause
  exit /b 1
)
start "" "%~dp0env\pythonw.exe" -m pytiara.gui.launcher
