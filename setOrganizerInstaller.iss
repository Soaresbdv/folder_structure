[Setup]
AppName=SetOrganizer
AppVersion=1.0
DefaultDirName={autopf}\SetOrganizer
DefaultGroupName=SetOrganizer
OutputDir=C:\Users\bruno.lima\Desktop\Output
OutputBaseFilename=Organizer
Compression=lzma
SolidCompression=yes
DisableProgramGroupPage=yes
SetupIconFile="C:\Users\bruno.lima\Downloads\favicon.ico"


[Files]
Source: "dist\\setOrganizer.exe"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{autoprograms}\\SetOrganizer"; Filename: "{app}\\setOrganizer.exe"; IconFilename: "{app}\\setOrganizer.exe"

[Run]
Filename: "{app}\\setOrganizer.exe"; Description: "Lançar SetOrganizer"; Flags: nowait postinstall skipifsilent

[UninstallDelete]
Type: dirifempty; Name: "{app}"
