# 🐣 다마고치 (Damagochi)

Pygame 기반 가상 펫 게임. 픽셀아트 캐릭터를 키우고, 미니게임으로 놀고, 블루투스로 친구 펫과 만나보세요!

---

## 📥 다운로드 & 실행

### 방법 A: exe 파일 (가장 쉬움)
1. [Releases 페이지](../../releases) 에서 `Damagochi.exe` 다운로드
2. 더블 클릭으로 실행
3. 업데이트는 게임 시작 시 자동 확인

### 방법 B: 소스 코드
```bash
# 1. 클론
git clone https://github.com/hjchoi00/damaproject.git
cd damagochi

# 2. 의존성 설치
pip install -r requirements.txt

# 3. 실행 (자동 업데이트 포함)
python launcher.py

# 또는 직접 실행
python main.py
```

> **Python 3.10 이상** 필요

---

## 🎮 게임 기능

| 기능 | 설명 |
|------|------|
| 🥚 부화 | 알에서 시작, 30초 후 부화 |
| 📈 5단계 진화 | 알 → 아기 → 어린이 → 청소년 → 성인 |
| 🍚 밥 주기 | 기본 밥(무한) + 보상 음식(인벤토리) |
| 🎮 미니게임 5종 | 가위바위보, 숫자맞추기, 리듬, 퍼즐, 달리기 |
| 🏋️ 훈련 | 지능 상승 + 보상 음식 획득 |
| 📡 블루투스 | 친구 펫과 만나기 (BLE) |
| 💾 자동 저장 | 5분마다 + 종료 시 자동 저장 |

### 🎁 보상 시스템
- **미니게임 승리**: 간식 x1, 케이크 x1
- **미니게임 무승부**: 간식 x1
- **훈련**: 약초차 x1, 샐러드 x1

---

## 📡 블루투스 통신 방법

1. 두 PC 모두 블루투스 켜기
2. 각자 게임 실행
3. **📡 친구 만나기** → **🔵 블루투스 검색**
4. 발견된 기기 선택하여 연결

> Windows 10/11 + 블루투스 4.0 이상 필요

---

## 🔄 업데이트

### 소스 사용자
`python launcher.py` 실행 시 자동으로 `git pull` (또는 수동으로 `git pull`)

### exe 사용자
게임 시작 시 GitHub Releases에서 자동 확인 → 새 버전이 있으면 자동 다운로드

---

## 🛠️ 개발

### 프로젝트 구조
```
damagochi/
├── main.py          # 게임 엔트리포인트
├── launcher.py      # 자동 업데이트 런처
├── build.py         # exe 빌드 스크립트
├── data/            # 상수, 저장/불러오기  
├── pet/             # 펫 엔진, 액션, 진화
├── gui/             # UI, 스프라이트, 씬, 애니메이션
├── minigames/       # 미니게임 5종
└── network/         # BLE + WiFi 통신
```

### exe 빌드
```bash
pip install pyinstaller
python build.py
# → dist/Damagochi.exe 생성
```

### 버전 올리기
1. `data/constants.py`의 `VERSION` 수정
2. 커밋 & 푸시
3. GitHub에서 Release 생성 (태그: `v1.0.1` 등)
4. `python build.py`로 exe 빌드 후 Release에 첨부