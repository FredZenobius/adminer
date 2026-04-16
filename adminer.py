"""
pyinstaller --onefile --noconsole --icon=adminer.ico --exclude-module=numpy --exclude-module=PIL.ImageFilter --exclude-module=PIL.SpiderImagePlugin adminer.py
"""

import sys
import subprocess
import os
import socket
import argparse
import threading
import ctypes

# pystray / Pillow 로딩
try:
    import pystray
    from PIL import Image, ImageDraw
except ImportError:
    subprocess.run([sys.executable, "-m", "pip", "install", "pystray", "Pillow"])
    import pystray
    from PIL import Image, ImageDraw


def show_error(msg: str):
    ctypes.windll.user32.MessageBoxW(0, msg, "Adminer 오류", 0x10)


# ============================================================
#   경로 설정
# ============================================================

if getattr(sys, "frozen", False):
    APP_DIR = os.path.dirname(sys.executable)
    # dist 폴더처럼 PHP 파일이 없는 위치에서 실행 시 상위 폴더에서 탐색 (개발/테스트용)
    if not os.path.exists(os.path.join(APP_DIR, "adminer.php")):
        parent = os.path.dirname(APP_DIR)
        if os.path.exists(os.path.join(parent, "adminer.php")):
            APP_DIR = parent
else:
    APP_DIR = os.path.dirname(os.path.abspath(__file__))

# PHP 경로: php/php.exe (설치 버전) 또는 ../php.exe (개발 환경)
_php_sub = os.path.join(APP_DIR, "php", "php.exe")
_php_parent = os.path.join(APP_DIR, "..", "php.exe")
PHP_PATH = _php_sub if os.path.exists(_php_sub) else _php_parent
ADMINER_PATH = os.path.join(APP_DIR, "adminer.php")
ROUTER_PATH = os.path.join(APP_DIR, "router.php")
ICON_FILE = os.path.join(APP_DIR, "adminer.ico")

BIND_HOST = "0.0.0.0"
php_process = None
_job = None


# ============================================================
#   유틸
# ============================================================
def is_port_in_use(port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(("127.0.0.1", port)) == 0


def get_local_ip() -> str:
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect(("8.8.8.8", 80))
            return s.getsockname()[0]
    except Exception:
        return "127.0.0.1"


# ============================================================
#   Job Object (부모 종료 → 자식 자동 종료)
# ============================================================
def create_job_object():
    global _job
    try:
        from ctypes import wintypes
        kernel32 = ctypes.windll.kernel32

        _job = kernel32.CreateJobObjectW(None, None)
        if not _job:
            return

        class JOBOBJECT_BASIC_LIMIT_INFORMATION(ctypes.Structure):
            _fields_ = [
                ("PerProcessUserTimeLimit", ctypes.c_int64),
                ("PerJobUserTimeLimit", ctypes.c_int64),
                ("LimitFlags", ctypes.c_ulong),
                ("MinimumWorkingSetSize", ctypes.c_size_t),
                ("MaximumWorkingSetSize", ctypes.c_size_t),
                ("ActiveProcessLimit", ctypes.c_ulong),
                ("Affinity", ctypes.POINTER(ctypes.c_ulong)),
                ("PriorityClass", ctypes.c_ulong),
                ("SchedulingClass", ctypes.c_ulong),
            ]

        class IO_COUNTERS(ctypes.Structure):
            _fields_ = [(n, ctypes.c_uint64) for n in (
                "ReadOperationCount", "WriteOperationCount", "OtherOperationCount",
                "ReadTransferCount", "WriteTransferCount", "OtherTransferCount",
            )]

        class JOBOBJECT_EXTENDED_LIMIT_INFORMATION(ctypes.Structure):
            _fields_ = [
                ("BasicLimitInformation", JOBOBJECT_BASIC_LIMIT_INFORMATION),
                ("IoInfo", IO_COUNTERS),
                ("ProcessMemoryLimit", ctypes.c_size_t),
                ("JobMemoryLimit", ctypes.c_size_t),
                ("PeakProcessMemoryUsed", ctypes.c_size_t),
                ("PeakJobMemoryUsed", ctypes.c_size_t),
            ]

        info = JOBOBJECT_EXTENDED_LIMIT_INFORMATION()
        info.BasicLimitInformation.LimitFlags = 0x2000  # KILL_ON_JOB_CLOSE
        kernel32.SetInformationJobObject(_job, 9, ctypes.byref(info), ctypes.sizeof(info))
    except Exception:
        _job = None


# ============================================================
#   PHP 서버 관리
# ============================================================
def start_php(port: int) -> subprocess.Popen:
    proc = subprocess.Popen(
        [PHP_PATH, "-S", f"{BIND_HOST}:{port}", "router.php"],
        cwd=APP_DIR,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        shell=False,
        creationflags=subprocess.CREATE_NO_WINDOW,
    )
    if _job:
        try:
            h = ctypes.windll.kernel32.OpenProcess(0x1FFFFF, False, proc.pid)
            ctypes.windll.kernel32.AssignProcessToJobObject(_job, h)
            ctypes.windll.kernel32.CloseHandle(h)
        except Exception:
            pass
    return proc


def stop_php():
    global php_process
    if php_process:
        try:
            php_process.kill()
            php_process.wait(timeout=3)
        except Exception:
            pass
        php_process = None


# ============================================================
#   트레이 아이콘
# ============================================================
def load_icon():
    if os.path.exists(ICON_FILE):
        try:
            return Image.open(ICON_FILE)
        except Exception:
            pass
    img = Image.new("RGBA", (64, 64), (0, 0, 0, 0))
    ImageDraw.Draw(img).ellipse([4, 4, 60, 60], fill=(0, 120, 215))
    return img


def run_tray(port: int):
    local_ip = get_local_ip()
    url = f"http://{local_ip}:{port}/"

    def copy_url(icon, item):
        try:
            subprocess.run(["clip.exe"], input=url.encode("utf-8"),
                           creationflags=subprocess.CREATE_NO_WINDOW)
        except Exception:
            pass

    def open_browser(icon, item):
        import webbrowser
        webbrowser.open(url)

    def restart(icon, item):
        global php_process
        stop_php()
        php_process = start_php(port)

    def quit_app(icon, item):
        stop_php()
        icon.stop()

    menu = pystray.Menu(
        pystray.MenuItem(f"Adminer - {url}", None, enabled=False),
        pystray.Menu.SEPARATOR,
        pystray.MenuItem("브라우저로 열기", open_browser),
        pystray.MenuItem("URL 복사", copy_url),
        pystray.MenuItem("서버 재시작", restart),
        pystray.Menu.SEPARATOR,
        pystray.MenuItem("종료", quit_app),
    )
    pystray.Icon("adminer", load_icon(), f"Adminer - {url}", menu).run()


# ============================================================
#   메인
# ============================================================
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Adminer")
    parser.add_argument("--port", type=int, default=8080)
    port = parser.parse_args().port

    if is_port_in_use(port):
        show_error(f"포트 {port}이 이미 사용 중입니다.\n이미 실행 중인 인스턴스가 있을 수 있습니다.")
        sys.exit(1)
    if not os.path.exists(PHP_PATH):
        show_error(f"php.exe를 찾을 수 없습니다.\n경로: {PHP_PATH}")
        sys.exit(1)
    if not os.path.exists(ADMINER_PATH):
        show_error(f"adminer.php를 찾을 수 없습니다.\n경로: {ADMINER_PATH}")
        sys.exit(1)
    if not os.path.exists(ROUTER_PATH):
        show_error(f"router.php를 찾을 수 없습니다.\n경로: {ROUTER_PATH}")
        sys.exit(1)

    create_job_object()

    try:
        php_process = start_php(port)
    except Exception as e:
        show_error(f"PHP 서버 실행 실패:\n{e}")
        sys.exit(1)

    run_tray(port)
