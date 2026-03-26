#define MyAppName "Empty Pockets"
#define MyAppVersion "1.0"
#define MyAppExeName "Empty_Pockets.exe"

[Setup]
AppId={{DD26CD03-FAF1-4117-AD2E-94930DE782E4}}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
DefaultDirName={autopf}\{#MyAppName}
UninstallDisplayIcon={app}\{#MyAppExeName}
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
DisableProgramGroupPage=yes
OutputBaseFilename=EmptyPocketsInstaller
SolidCompression=yes
WizardStyle=modern

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "Create a desktop shortcut"; GroupDescription: "Additional Icons"; Flags: unchecked

[Files]
Source: "C:\Users\Ehan\Desktop\Empty-Pockets-main\dist\Empty_Pockets.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "C:\Users\Ehan\Desktop\Empty-Pockets-main\dist\images\*"; DestDir: "{app}\images"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "C:\Users\Ehan\Desktop\Empty-Pockets-main\dist\savegame.json"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{autoprograms}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "Launch Empty Pockets"; Flags: nowait postinstall skipifsilent

