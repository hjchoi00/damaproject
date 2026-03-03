"""
PyInstaller 빌드 스크립트
실행: python build.py
결과: dist/Damagochi.exe (단일 파일)
"""
import subprocess
import sys
import os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))


def build():
    print("🔨 다마고치 빌드 시작...")
    print("=" * 40)

    # PyInstaller 설치 확인
    try:
        import PyInstaller
        print(f"✅ PyInstaller {PyInstaller.__version__}")
    except ImportError:
        print("📦 PyInstaller 설치 중...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])

    # 빌드 명령
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--onefile",                     # 단일 exe
        "--windowed",                    # 콘솔 창 숨김
        "--name", "Damagochi",           # exe 이름
        "--clean",                       # 이전 빌드 정리
        "--add-data", f"data;data",      # data 폴더 포함
        "--add-data", f"gui;gui",
        "--add-data", f"pet;pet",
        "--add-data", f"minigames;minigames",
        "--add-data", f"network;network",
        "--hidden-import", "pygame",
        "--hidden-import", "bleak",
        "--hidden-import", "bless",
        "launcher.py",                   # 런처를 엔트리포인트로
    ]

    print(f"\n📋 실행 명령:")
    print(" ".join(cmd))
    print()

    result = subprocess.run(cmd, cwd=SCRIPT_DIR)

    if result.returncode == 0:
        exe_path = os.path.join(SCRIPT_DIR, "dist", "Damagochi.exe")
        if os.path.exists(exe_path):
            size_mb = os.path.getsize(exe_path) / (1024 * 1024)
            print(f"\n✅ 빌드 성공!")
            print(f"   📁 {exe_path}")
            print(f"   📏 {size_mb:.1f} MB")
        else:
            print("\n⚠️ 빌드 완료했지만 exe를 찾을 수 없습니다")
    else:
        print(f"\n❌ 빌드 실패 (코드: {result.returncode})")
        sys.exit(1)


if __name__ == "__main__":
    build()
