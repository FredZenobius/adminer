; Adminer InnoSetup Script
; InnoSetup 6.x

#define MyAppName "Adminer"
#define MyAppVersion "1.01"
#define MyAppExeName "adminer.exe"
#define PhpDir "..\\"

[Setup]
AppId={{A1D2E3F4-5678-9ABC-DEF0-123456789ABC}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
AppComments=v1.01: 트레이 메뉴에 '브라우저로 열기' 기능 추가
OutputDir=output
OutputBaseFilename=AdminerSetup
Compression=lzma2/ultra64
SolidCompression=yes
SetupIconFile=adminer.ico
UninstallDisplayIcon={app}\adminer.ico
PrivilegesRequired=lowest
ArchitecturesInstallIn64BitMode=x64compatible

[Languages]
Name: "korean"; MessagesFile: "compiler:Languages\Korean.isl"

[Files]
; Adminer
Source: "dist\adminer.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "adminer.php"; DestDir: "{app}"; Flags: ignoreversion
Source: "adminer.css"; DestDir: "{app}"; Flags: ignoreversion
Source: "router.php"; DestDir: "{app}"; Flags: ignoreversion
Source: "adminer.ico"; DestDir: "{app}"; Flags: ignoreversion

; PHP 최소 구성 (코어)
Source: "{#PhpDir}php.exe"; DestDir: "{app}\php"; Flags: ignoreversion
Source: "{#PhpDir}php.ini"; DestDir: "{app}\php"; Flags: ignoreversion
Source: "{#PhpDir}php8.dll"; DestDir: "{app}\php"; Flags: ignoreversion

; PHP 필수 DLL (런타임 의존성)
Source: "{#PhpDir}libcrypto-3-x64.dll"; DestDir: "{app}\php"; Flags: ignoreversion
Source: "{#PhpDir}libssl-3-x64.dll"; DestDir: "{app}\php"; Flags: ignoreversion
Source: "{#PhpDir}libsqlite3.dll"; DestDir: "{app}\php"; Flags: ignoreversion
Source: "{#PhpDir}libpq.dll"; DestDir: "{app}\php"; Flags: ignoreversion
Source: "{#PhpDir}libsasl.dll"; DestDir: "{app}\php"; Flags: ignoreversion
Source: "{#PhpDir}libssh2.dll"; DestDir: "{app}\php"; Flags: ignoreversion
Source: "{#PhpDir}nghttp2.dll"; DestDir: "{app}\php"; Flags: ignoreversion

; PHP 확장 (Adminer에서 사용하는 것만)
Source: "{#PhpDir}ext\php_mbstring.dll"; DestDir: "{app}\php\ext"; Flags: ignoreversion
Source: "{#PhpDir}ext\php_openssl.dll"; DestDir: "{app}\php\ext"; Flags: ignoreversion
Source: "{#PhpDir}ext\php_mysqli.dll"; DestDir: "{app}\php\ext"; Flags: ignoreversion
Source: "{#PhpDir}ext\php_pdo_mysql.dll"; DestDir: "{app}\php\ext"; Flags: ignoreversion
Source: "{#PhpDir}ext\php_pgsql.dll"; DestDir: "{app}\php\ext"; Flags: ignoreversion
Source: "{#PhpDir}ext\php_pdo_pgsql.dll"; DestDir: "{app}\php\ext"; Flags: ignoreversion
Source: "{#PhpDir}ext\php_sqlite3.dll"; DestDir: "{app}\php\ext"; Flags: ignoreversion
Source: "{#PhpDir}ext\php_pdo_sqlite.dll"; DestDir: "{app}\php\ext"; Flags: ignoreversion
Source: "{#PhpDir}ext\php_curl.dll"; DestDir: "{app}\php\ext"; Flags: ignoreversion

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; IconFilename: "{app}\adminer.ico"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; IconFilename: "{app}\adminer.ico"; Tasks: desktopicon
Name: "{autostartup}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; IconFilename: "{app}\adminer.ico"; Tasks: startupicon

[Tasks]
Name: "desktopicon"; Description: "바탕화면에 바로가기 만들기"; GroupDescription: "추가 아이콘:"
Name: "startupicon"; Description: "Windows 시작 시 자동 실행"; GroupDescription: "자동 실행:"

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "Adminer 실행"; Flags: nowait postinstall skipifsilent

[UninstallRun]
Filename: "taskkill"; Parameters: "/F /IM adminer.exe"; Flags: runhidden; RunOnceId: "KillAdminer"
Filename: "taskkill"; Parameters: "/F /IM php.exe"; Flags: runhidden; RunOnceId: "KillPhp"
