"""
다마고치 런처 - 자동 업데이트 + 게임 실행
소스 모드: git pull로 업데이트
exe 모드: GitHub Releases에서 최신 버전 확인/다운로드
"""
import os
import sys
import subprocess
import json
import urllib.request
import urllib.error
import shutil
import time

# ─── 경로 설정 ───
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
os.chdir(SCRIPT_DIR)  # 작업 디렉토리를 스크립트 위치로 고정


def get_version():
    """현재 버전 읽기"""
    try:
        # constants.py에서 직접 파싱 (import 없이)
        const_path = os.path.join(SCRIPT_DIR, "data", "constants.py")
        with open(const_path, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip().startswith("VERSION"):
                    return line.split("=")[1].strip().strip('"').strip("'")
    except Exception:
        pass
    return "0.0.0"


def get_github_repo():
    """GitHub 레포 경로 읽기"""
    try:
        const_path = os.path.join(SCRIPT_DIR, "data", "constants.py")
        with open(const_path, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip().startswith("GITHUB_REPO"):
                    return line.split("=")[1].strip().strip('"').strip("'")
    except Exception:
        pass
    return None


def is_git_repo():
    """Git 저장소인지 확인"""
    return os.path.isdir(os.path.join(SCRIPT_DIR, ".git"))


def is_frozen():
    """PyInstaller exe로 실행 중인지 확인"""
    return getattr(sys, 'frozen', False)


# ═══════════════════════════════════════
# 소스 모드 업데이트 (git pull)
# ═══════════════════════════════════════

def update_source():
    """Git pull로 소스 업데이트"""
    if not is_git_repo():
        return False, "Git 저장소가 아닙니다"

    try:
        result = subprocess.run(
            ["git", "pull", "--rebase"],
            capture_output=True, text=True, timeout=30,
            cwd=SCRIPT_DIR
        )
        if result.returncode == 0:
            output = result.stdout.strip()
            if "Already up to date" in output or "이미" in output:
                return True, "최신 버전입니다"
            return True, f"업데이트 완료!\n{output}"
        else:
            return False, f"업데이트 실패: {result.stderr.strip()}"
    except FileNotFoundError:
        return False, "Git이 설치되어 있지 않습니다"
    except subprocess.TimeoutExpired:
        return False, "업데이트 시간 초과"
    except Exception as e:
        return False, f"오류: {e}"


# ═══════════════════════════════════════
# exe 모드 업데이트 (GitHub Releases)
# ═══════════════════════════════════════

def check_latest_release(repo):
    """GitHub Releases에서 최신 버전 확인"""
    url = f"https://api.github.com/repos/{repo}/releases/latest"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Damagochi-Launcher"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode())
            tag = data.get("tag_name", "").lstrip("v")
            assets = data.get("assets", [])
            exe_url = None
            for asset in assets:
                if asset["name"].lower().endswith(".exe"):
                    exe_url = asset["browser_download_url"]
                    break
            return tag, exe_url
    except Exception:
        return None, None


def version_tuple(v):
    """'1.2.3' → (1, 2, 3)"""
    try:
        return tuple(int(x) for x in v.split("."))
    except Exception:
        return (0, 0, 0)


def update_exe(repo):
    """exe 자동 업데이트"""
    current = get_version()
    latest, exe_url = check_latest_release(repo)

    if not latest:
        return False, "버전 확인 실패 (오프라인?)"

    if version_tuple(latest) <= version_tuple(current):
        return True, f"최신 버전입니다 (v{current})"

    if not exe_url:
        return False, f"새 버전 v{latest}이 있지만 exe가 없습니다"

    # 다운로드
    print(f"🔄 새 버전 v{latest} 다운로드 중...")
    try:
        exe_path = sys.executable
        temp_path = exe_path + ".new"
        urllib.request.urlretrieve(exe_url, temp_path)

        # 교체 배치 스크립트 생성 (현재 실행 중인 exe는 직접 교체 불가)
        bat_path = os.path.join(SCRIPT_DIR, "_update.bat")
        with open(bat_path, "w") as f:
            f.write(f"""@echo off
timeout /t 2 /nobreak >nul
move /y "{temp_path}" "{exe_path}"
del "%~f0"
start "" "{exe_path}"
""")
        subprocess.Popen(["cmd", "/c", bat_path], cwd=SCRIPT_DIR)
        return True, f"v{latest} 다운로드 완료! 재시작합니다..."
    except Exception as e:
        return False, f"다운로드 실패: {e}"


# ═══════════════════════════════════════
# 메인 런처
# ═══════════════════════════════════════

def show_update_screen(message):
    """Pygame 화면에 업데이트 상태 표시"""
    try:
        import pygame
        pygame.init()
        screen = pygame.display.set_mode((480, 300))
        pygame.display.set_caption("🐣 다마고치 업데이트")
        screen.fill((255, 250, 240))

        try:
            font = pygame.font.SysFont("malgungothic", 18)
        except Exception:
            font = pygame.font.Font(None, 22)

        lines = message.split("\n")
        for i, line in enumerate(lines):
            surf = font.render(line, True, (80, 80, 80))
            screen.blit(surf, (30, 40 + i * 30))

        pygame.display.flip()
        pygame.time.wait(1500)
        pygame.quit()
    except Exception:
        print(message)


def main():
    print(f"🐣 다마고치 런처 v{get_version()}")
    print("=" * 40)

    repo = get_github_repo()

    # 업데이트 시도
    if is_frozen():
        # exe 모드
        if repo:
            print("📦 exe 모드 — GitHub Releases 확인 중...")
            success, msg = update_exe(repo)
            print(f"  → {msg}")
            if "재시작" in msg:
                sys.exit(0)
    else:
        # 소스 모드
        if is_git_repo():
            print("📂 소스 모드 — git pull 확인 중...")
            success, msg = update_source()
            print(f"  → {msg}")
        else:
            print("📂 소스 모드 — Git 미설정 (업데이트 건너뜀)")

    # 게임 실행
    print("\n🎮 게임을 시작합니다...")
    print("=" * 40)

    # main.py를 직접 import하여 실행
    try:
        from main import main as run_game
        run_game()
    except KeyboardInterrupt:
        print("\n👋 종료합니다.")
    except Exception as e:
        print(f"\n❌ 오류 발생: {e}")
        import traceback
        traceback.print_exc()
        input("\n아무 키나 눌러 종료...")


if __name__ == "__main__":
    main()
