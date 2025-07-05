; Personal File Organizer Installer Script
; Created with Nullsoft Scriptable Install System

; Define application information
!define APPNAME "Personal File Organizer"
!define COMPANYNAME "JUST ELSON PRODUCTIVE.labs"
!define DESCRIPTION "A powerful tool for organizing your personal files"
!define VERSIONMAJOR 1
!define VERSIONMINOR 0
!define VERSIONBUILD 0
!define HELPURL "https://justelson.github.io/my-official-website/"
!define UPDATEURL "https://justelson.github.io/my-official-website/"
!define ABOUTURL "https://justelson.github.io/my-official-website/"

; Main install settings
Name "${APPNAME}"
InstallDir "$PROGRAMFILES64\${COMPANYNAME}\${APPNAME}"
InstallDirRegKey HKLM "Software\${COMPANYNAME}\${APPNAME}" "Install_Dir"
RequestExecutionLevel admin
OutFile "PersonalFileOrganizerSetup.exe"

; Include Modern UI
!include "MUI2.nsh"

; Modern UI Settings
!define MUI_ABORTWARNING
!define MUI_ICON "icon_personal.ico"
!define MUI_UNICON "icon_personal.ico"
!define MUI_WELCOMEFINISHPAGE_BITMAP "installer_welcome.bmp"
!define MUI_UNWELCOMEFINISHPAGE_BITMAP "installer_welcome.bmp"
!define MUI_HEADERIMAGE
!define MUI_HEADERIMAGE_BITMAP "installer_header.bmp"
!define MUI_HEADERIMAGE_RIGHT

; Pages
!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_LICENSE "license.txt"
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_PAGE_FINISH

!insertmacro MUI_UNPAGE_WELCOME
!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES
!insertmacro MUI_UNPAGE_FINISH

; Set UI language
!insertmacro MUI_LANGUAGE "English"

Section "Install"
    ; Set output path to the installation directory
    SetOutPath $INSTDIR
    
    ; Add files
    File "dist\PersonalFileOrganizer.exe"
    
    ; Create uninstaller
    WriteUninstaller "$INSTDIR\Uninstall.exe"
    
    ; Create shortcuts
    CreateDirectory "$SMPROGRAMS\${COMPANYNAME}"
    CreateShortcut "$SMPROGRAMS\${COMPANYNAME}\${APPNAME}.lnk" "$INSTDIR\PersonalFileOrganizer.exe"
    CreateShortcut "$DESKTOP\${APPNAME}.lnk" "$INSTDIR\PersonalFileOrganizer.exe"
    
    ; Create registry entries
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${COMPANYNAME}_${APPNAME}" "DisplayName" "${APPNAME}"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${COMPANYNAME}_${APPNAME}" "UninstallString" "$\"$INSTDIR\Uninstall.exe$\""
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${COMPANYNAME}_${APPNAME}" "QuietUninstallString" "$\"$INSTDIR\Uninstall.exe$\" /S"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${COMPANYNAME}_${APPNAME}" "InstallLocation" "$\"$INSTDIR$\""
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${COMPANYNAME}_${APPNAME}" "DisplayIcon" "$\"$INSTDIR\PersonalFileOrganizer.exe$\""
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${COMPANYNAME}_${APPNAME}" "Publisher" "${COMPANYNAME}"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${COMPANYNAME}_${APPNAME}" "HelpLink" "${HELPURL}"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${COMPANYNAME}_${APPNAME}" "URLUpdateInfo" "${UPDATEURL}"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${COMPANYNAME}_${APPNAME}" "URLInfoAbout" "${ABOUTURL}"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${COMPANYNAME}_${APPNAME}" "DisplayVersion" "${VERSIONMAJOR}.${VERSIONMINOR}.${VERSIONBUILD}"
    WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${COMPANYNAME}_${APPNAME}" "VersionMajor" ${VERSIONMAJOR}
    WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${COMPANYNAME}_${APPNAME}" "VersionMinor" ${VERSIONMINOR}
    
    ; Set registry for file associations if needed
    ; WriteRegStr HKCR ".myext" "" "MyAppFile"
    ; WriteRegStr HKCR "MyAppFile" "" "My Application File"
    ; WriteRegStr HKCR "MyAppFile\DefaultIcon" "" "$INSTDIR\PersonalFileOrganizer.exe,0"
    ; WriteRegStr HKCR "MyAppFile\shell\open\command" "" '"$INSTDIR\PersonalFileOrganizer.exe" "%1"'
SectionEnd

Section "Uninstall"
    ; Remove application files
    Delete "$INSTDIR\PersonalFileOrganizer.exe"
    Delete "$INSTDIR\Uninstall.exe"
    RMDir "$INSTDIR"
    
    ; Remove shortcuts
    Delete "$SMPROGRAMS\${COMPANYNAME}\${APPNAME}.lnk"
    RMDir "$SMPROGRAMS\${COMPANYNAME}"
    Delete "$DESKTOP\${APPNAME}.lnk"
    
    ; Remove registry keys
    DeleteRegKey HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${COMPANYNAME}_${APPNAME}"
    DeleteRegKey HKLM "Software\${COMPANYNAME}\${APPNAME}"
    
    ; Remove file associations if you added them
    ; DeleteRegKey HKCR ".myext"
    ; DeleteRegKey HKCR "MyAppFile"
SectionEnd