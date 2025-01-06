[Setup]
PrivilegesRequired=lowest
AppName=Lil' Bin Boy
AppVersion=1.0
DefaultDirName={autoappdata}\Lil Bin Boy
OutputDir=..\dist
OutputBaseFilename=lilbinboy_win
Compression=lzma
SolidCompression=yes
SourceDir=..\build
LicenseFile=..\EULA

[Files]
Source: "lilbinboy.exe"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{autoprograms}\Lil' Bin Boy"; Filename: "{app}\lilbinboy.exe"