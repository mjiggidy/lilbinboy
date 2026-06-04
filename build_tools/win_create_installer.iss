; Lil' Bin Boy Install v0.1
; October 14, 2025

#define MyAppName "Lil' Bin Boy"
#define MyAppPublisher "GlowingPixel"
#define MyAppURL "https://github.com/mjiggidy/lilbinboy/"
#define MyAppExeName "lilbinboy.exe"
#define AppGUID "d114e8d0-975b-4f0f-8661-3fade5acc82f"


[Setup]
AppId={#AppGUID}
AppName={#MyAppName}
;App version comes in from the command line in the github workflow
AppVersion={#MyAppVersion}
;AppVerName={#MyAppName} {#MyAppVersion}

AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}
DefaultDirName={autopf}\{#MyAppName}
; "ArchitecturesAllowed=x64compatible" specifies that Setup cannot run
; on anything but x64 and Windows 11 on Arm.
ArchitecturesAllowed=x64compatible
; "ArchitecturesInstallIn64BitMode=x64compatible" requests that the
; install be done in "64-bit mode" on x64 or Windows 11 on Arm,
; meaning it should use the native 64-bit Program Files directory and
; the 64-bit view of the registry.
ArchitecturesInstallIn64BitMode=x64compatible
DisableProgramGroupPage=yes
LicenseFile=..\DISCLAIMER.md
; lowest means "user level" btw
PrivilegesRequired=lowest
PrivilegesRequiredOverridesAllowed=dialog

OutputDir=..\installer
OutputBaseFilename=lilbinboy_windows_v{#MyAppVersion}_x86-64
Compression=lzma
SolidCompression=yes
WizardStyle=classic
;WizardSmallImageFile=lbb_logo_58.bmp,lbb_logo_71.bmp

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
Source: "..\build\main.dist\{#MyAppExeName}"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\build\main.dist\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{autoprograms}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent
