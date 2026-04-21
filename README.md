# Adminer Portable

[Adminer](https://www.adminer.org/) 데이터베이스 관리 도구를 Windows 시스템 트레이 애플리케이션으로 실행합니다.  
PHP를 내장하여 별도 설치 없이 독립 실행됩니다.

## 기능

- **시스템 트레이 실행** — GUI 없이 백그라운드로 동작
- **네트워크 접속** — 같은 네트워크의 다른 PC에서 접속 가능 (`0.0.0.0` 바인딩)
- **중복 실행 방지** — 이미 실행 중이면 에러 팝업 후 종료
- **트레이 메뉴**
  - 현재 PC의 접속 URL 확인 및 클립보드 복사
  - 서버 재시작
  - 종료
- **포트 커스텀** — `--port` 인자로 변경 가능 (기본: 8080)
- **자동 프로세스 정리** — Windows Job Object로 부모 종료 시 PHP도 함께 종료

## 파일 구조

### 개발 환경 (PHP 폴더 안에 adminer가 있는 구조)

```
php/
├── php.exe
├── php.ini
├── php8.dll
├── *.dll
├── ext/
│   └── ...
└── adminer/           ← 이 저장소
    ├── adminer.py
    ├── adminer.php
    ├── adminer.css
    ├── adminer.ico
    └── setup.iss
```

### InnoSetup 설치 후

```
Adminer/
├── adminer.exe
├── adminer.php
├── adminer.css
├── adminer.ico
└── php/
    ├── php.exe
    ├── php.ini
    ├── php8.dll
    ├── *.dll
    └── ext/
        └── ...
```

> PHP 경로는 자동 감지됩니다: `php/php.exe`를 먼저 찾고, 없으면 `../php.exe`를 사용합니다.

## 빌드 방법

### 사전 준비

1. [PHP for Windows](https://windows.php.net/download/) 다운로드 후 압축 해제 (예: `c:\php\`)
2. **이 저장소를 PHP 폴더 안에 clone**

```bash
cd c:\php
git clone <repo-url> adminer
```

> **중요**: `setup.iss`가 부모 폴더(`..\\`)에서 PHP 파일을 가져오므로, 반드시 PHP 폴더 바로 아래에 `adminer/` 폴더가 있어야 합니다.

```
c:\php\                  ← PHP 폴더
├── php.exe
├── php.ini
├── php8.dll
├── *.dll
├── ext\
└── adminer\             ← 이 저장소
    ├── adminer.py
    ├── adminer.php
    ├── adminer.css
    ├── adminer.ico
    └── setup.iss
```

### PyInstaller 빌드

```bash
cd c:\php\adminer
pip install pystray Pillow pyinstaller
pyinstaller --onefile --noconsole --icon=adminer.ico --exclude-module=numpy --exclude-module=PIL.ImageFilter --exclude-module=PIL.SpiderImagePlugin adminer.py
```

빌드 결과: `dist/adminer.exe`

### InnoSetup 설치 프로그램 빌드

1. [InnoSetup 6](https://jrsoftware.org/isinfo.php) 설치
2. `setup.iss`를 InnoSetup Compiler로 열고 컴파일
3. `output/AdminerSetup.exe` 생성됨

## 지원 DB

Adminer에서 지원하는 모든 DB를 사용할 수 있습니다:

- MySQL / MariaDB
- PostgreSQL
- SQLite
- MS SQL
- Oracle

## 시스템 요구사항

**Microsoft Visual C++ 재배포 가능 패키지 2015-2022 (x64)** 가 필요합니다.  
Windows 10/11에는 대부분 기본 설치되어 있으나, 없을 경우 아래에서 설치하세요.

- 다운로드: https://aka.ms/vs/17/release/vc_redist.x64.exe

## 라이선스

- Adminer: [Apache License 2.0 / GPL 2](https://www.adminer.org/)
- 본 래퍼: MIT
