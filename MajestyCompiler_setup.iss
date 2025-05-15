#define MyAppName "Majesty Compiler"
#define MyAppVersion "1.0"
#define MyAppPublisher "Ваше Величество"
#define MyAppURL "https://github.com/YourMajesty/MajestyCompiler"
#define MyAppExeName "MajestyCompiler.exe"
#define MyAppIconName "majesty_icon.ico"

[Setup]
; Уникальный идентификатор для этого приложения - не изменяйте его при обновлениях
AppId={{B4D2F7A8-924E-40A1-B89F-234F76D38A23}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
;AppVerName={#MyAppName} {#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}
DefaultDirName={autopf}\{#MyAppName}
DisableProgramGroupPage=yes
; Рекомендуется оставить следующую строку для более высокой безопасности
PrivilegesRequired=lowest
PrivilegesRequiredOverridesAllowed=dialog
OutputDir=installer
OutputBaseFilename=MajestyCompiler_Setup
SetupIconFile=majesty_icon.ico
Compression=lzma
SolidCompression=yes
WizardStyle=modern

[Languages]
Name: "russian"; MessagesFile: "compiler:Languages\Russian.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
Source: "dist\{#MyAppExeName}"; DestDir: "{app}"; Flags: ignoreversion
Source: "dist\{#MyAppIconName}"; DestDir: "{app}"; Flags: ignoreversion
; Здесь можно добавить дополнительные файлы, которые нужно включить в установщик

[Icons]
Name: "{autoprograms}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; IconFilename: "{app}\{#MyAppIconName}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; IconFilename: "{app}\{#MyAppIconName}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent

[Code]
// Дополнительный код для установщика (если потребуется) 