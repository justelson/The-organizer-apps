@echo off
echo Building Unified File Organizer...

echo Step 1: Creating executable with PyInstaller...
pyinstaller --clean --noconfirm unified_organizer.spec

echo Step 2: Preparing installer resources...
copy app_icons\the_all_in_one.ico unified_installer.ico
copy media_installer_welcome.bmp unified_installer_welcome.bmp
copy media_installer_header.bmp unified_installer_header.bmp

echo Step 3: Building installer with NSIS...
"C:\Program Files (x86)\NSIS\makensis.exe" installer.nsi

echo Build complete! The installer is: UnifiedFileOrganizerSetup.exe
pause