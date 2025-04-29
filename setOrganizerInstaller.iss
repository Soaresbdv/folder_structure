[Setup]
AppName=OrganizeUP
AppVersion=1.0
DefaultDirName={autopf}\OrganizeUP
DefaultGroupName=OrganizeUP
OutputDir=.\Output
OutputBaseFilename=OrganizeUP_Installer
Compression=lzma
SolidCompression=yes
DisableProgramGroupPage=yes
SetupIconFile="favicon.ico"

[Files]
Source: "dist\OrganizeUP.exe"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{autoprograms}\OrganizeUP"; Filename: "{app}\OrganizeUP.exe"; IconFilename: "{app}\OrganizeUP.exe"

[Run]
Filename: "{app}\OrganizeUP.exe"; Description: "Lançar OrganizeUP"; Flags: nowait postinstall skipifsilent

[UninstallDelete]
Type: dirifempty; Name: "{app}"
