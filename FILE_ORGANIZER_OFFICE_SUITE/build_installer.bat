@echo off
echo Building Office File Organizer...

echo Step 1: Creating executable with PyInstaller...
pyinstaller --clean --noconfirm OFFICE_organizer.spec

echo Step 2: Creating installer images...
REM This is a placeholder for creating installer images
REM You would need actual image creation tools or pre-made images

echo Step 3: Building installer with NSIS...
REM Update this path to where you installed NSIS
"C:\Program Files (x86)\NSIS\makensis.exe" installer.nsi

echo Build complete! The installer is: OfficeFileOrganizerSetup.exe
pause