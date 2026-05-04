; DL Mongoose - Inno Setup Script
; Download Inno Setup: https://jrsoftware.org/isinfo.php
; Compile this file with Inno Setup Compiler

#define MyAppName "DL Mongoose"
#define MyAppVersion "1.0.0"
#define MyAppPublisher "DL Mongoose"
#define MyAppURL "https://github.com/yourusername/dl-mongoose"
#define MyAppExeName "DLMongoose.exe"

[Setup]
AppId={{YOUR-UNIQUE-GUID-HERE}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppVerName={#MyAppName} {#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
AllowNoIcons=yes
LicenseFile=LICENSE.txt
OutputDir=installer_output
OutputBaseFilename=DLMongoose_Setup_v{#MyAppVersion}
SetupIconFile=assets\mongoose.ico
Compression=lzma
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=lowest
ArchitecturesAllowed=x64
ArchitecturesInstallIn64BitMode=x64

; Visual styling
WizardImageFile=assets\installer_banner.bmp
WizardSmallImageFile=assets\installer_icon.bmp

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon";    Description: "{cm:CreateDesktopIcon}";    GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked
Name: "startupicon";    Description: "Launch DL Mongoose at Windows startup"; GroupDescription: "Startup:"; Flags: unchecked
Name: "systemtray";     Description: "Minimize to system tray when closed";   GroupDescription: "Behaviour:"; Flags: checkedonce

[Files]
; Main app files from PyInstaller dist folder
Source: "dist\DLMongoose\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\{#MyAppName}";         Filename: "{app}\{#MyAppExeName}"
Name: "{group}\Uninstall {#MyAppName}"; Filename: "{uninstallexe}"
Name: "{userdesktop}\{#MyAppName}";   Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon
Name: "{userstartup}\{#MyAppName}";   Filename: "{app}\{#MyAppExeName}"; Tasks: startupicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent

[UninstallDelete]
Type: filesandordirs; Name: "{app}"

[Code]
// Check if FFmpeg needs to be downloaded
procedure InitializeWizard;
begin
  // Custom init logic can go here
end;
