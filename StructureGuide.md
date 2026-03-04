## 프로젝트 전체 구조 설명

---

### 앱 시작 흐름
```
launcher.py → main.py → SceneManager → TitleScene → NamingScene/MainScene → ...
```

---

### 엔트리포인트 & 빌드

| 파일 | 역할 |
|------|------|
| launcher.py | **진짜 시작점.** exe 모드면 GitHub Releases에서 최신 버전 확인→자동 업데이트, 소스 모드면 `git pull`. 그 후 `main.main()` 호출 |
| main.py | **Pygame 메인 루프.** 화면 생성, 9개 씬 등록, 매 프레임 이벤트→업데이트→드로우 반복. 종료 시 펫 저장 |
| build.py | **PyInstaller 빌드 스크립트.** `python build.py` → `dist/Damagochi.exe` 생성 |
| .github/workflows/build.yml | **CI/CD.** `v*` 태그 push 시 GitHub Actions가 자동으로 exe 빌드 → Release에 첨부 |

---

### `data/` — 상수 & 저장

| 파일 | 역할 |
|------|------|
| data/constants.py | **모든 숫자가 여기.** `VERSION`, 화면 크기, 색상 26종, 스탯 변화율, 레벨/경험치 테이블, 진화 단계·타입 정의, 음식 목록, 보상 테이블, BLE/WiFi 설정값. **게임 밸런스 수정은 이 파일만 건드리면 됨** |
| data/save.py | **세이브 파일 관리.** `~/.damagochi/save.json`에 JSON으로 저장/불러오기. 불러올 때 오프라인 경과 시간만큼 스탯 자연감소 적용 |

---

### `pet/` — 펫 로직

| 파일 | 역할 |
|------|------|
| pet/pet.py | **`Pet` 클래스 (핵심).** 15개 스탯 관리, 매 프레임 `update(dt)`로 배고픔↑/행복↓/청결↓ 자연변화, 레벨업·진화 처리, 랜덤 이벤트(병/보물), 사망 판정. `to_dict()`/`from_dict()`로 직렬화 |
| pet/actions.py | **펫에게 하는 행동들.** `feed()` 밥주기, `play()` 놀기 결과 반영, `clean()` 목욕, `sleep()` 재우기/깨우기, `give_medicine()` 치료, `train()` 훈련 |
| pet/evolution.py | **진화 설명 텍스트.** 단계(알→아기→어린이→청소년→성인) × 타입(활발/지능/먹보/균형)별 설명문. 다음 진화 레벨 계산 |

---

### `gui/` — 화면 & UI

| 파일 | 역할 |
|------|------|
| gui/scenes.py | **씬 시스템 (가장 큰 파일, 868줄).** `TitleScene`: 타이틀 화면. `NamingScene`: 이름 입력. `MainScene`: 메인 게임 화면(스탯바, 펫, 6개 버튼, 음식/놀기 팝업, 자동저장). `NetworkScene`: BLE/WiFi 연결 UI. **화면 흐름 수정은 여기** |
| gui/ui_elements.py | **UI 위젯 모음.** `Button`, `StatBar`(게이지), `TextInput`(한글IME지원), `Toast`(알림), `Dialog`(팝업), `Particle`(이펙트), `ExpBar`(경험치바) |
| gui/sprites.py | **코드로 그리는 픽셀아트 (744줄).** 외부 이미지 없이 도트 단위로 그림. 5단계×7표정×4타입 악세서리 조합. `get_sprite_for_pet(pet)` 호출하면 알아서 맞는 스프라이트 반환 |
| gui/animations.py | **애니메이션 효과.** 바운스(idle), 흔들림(아플때), 맥동(진화), 떠오르는 텍스트(+25 EXP), ZZZ(수면) |

---

### `minigames/` — 미니게임 5종

| 파일 | 역할 |
|------|------|
| minigames/base.py | **미니게임 기본 클래스.** ready→playing→result 상태머신. `finish_game()`에서 승/패/무 판정 + 보상 지급. **새 미니게임 추가 시 이걸 상속** |
| minigames/rps.py | **가위바위보** — 3판 2선승 |
| minigames/number_guess.py | **숫자 맞추기** — 1~100, 7회 이내 |
| minigames/rhythm.py | **리듬 게임** — 4레인 낙하 노트, 30초, 정확도 70%↑ 승리 |
| minigames/puzzle.py | **슬라이드 퍼즐** — 3×3, 30회 이내 |
| minigames/runner.py | **횡스크롤 달리기** — 장애물 피하기, 3000m 도달 시 승리 |

---

### `network/` — 네트워크 대전

| 파일 | 역할 |
|------|------|
| network/manager.py | **통합 매니저.** BLE와 WiFi를 하나의 인터페이스로 묶음. `send()` 하면 알아서 연결된 방식으로 전송 |
| network/protocol.py | **메시지 규약.** JSON 기반. hello/pet_info/battle_request/gift/bye 등 메시지 팩토리 |
| network/ble_central.py | **BLE 클라이언트** (bleak 라이브러리) — 스캔+연결 |
| network/ble_peripheral.py | **BLE 서버** (bless 라이브러리) — GATT 서버 광고 |
| network/wifi_socket.py | **WiFi TCP/UDP** — TCP 서버·클라이언트 + UDP 브로드캐스트 검색 |

---

### 수정 시 참고

| 하고 싶은 것 | 수정할 파일 |
|-------------|-----------|
| 게임 밸런스 (스탯 변화 속도, 보상량) | data/constants.py |
| 펫 외형 변경 | gui/sprites.py |
| 새 미니게임 추가 | minigames/base.py 상속 → main.py에 씬 등록 → gui/scenes.py 놀기 팝업에 버튼 추가 |
| UI 위젯 수정 | gui/ui_elements.py |
| 화면 흐름 변경 | gui/scenes.py |
| 새 음식 추가 | data/constants.py의 `FOODS` dict |
| 버전 업데이트 배포 | `VERSION` 올리기 → 커밋 → `git tag vX.X.X && git push origin vX.X.X` |

---

### 의존성 그래프

```
launcher.py ──→ data/constants.py (텍스트 파싱)
            ──→ main.py

main.py ──→ data/constants, data/save
        ──→ gui/scenes (SceneManager, TitleScene, NamingScene, MainScene, NetworkScene)
        ──→ minigames/* (RPSGame, NumberGuessGame, RhythmGame, PuzzleGame, RunnerGame)

gui/scenes.py ──→ gui/ui_elements, gui/sprites, gui/animations
              ──→ pet/pet, pet/actions, pet/evolution
              ──→ data/constants, data/save
              ──→ network/manager (NetworkScene에서)

minigames/base.py ──→ gui/scenes.Scene, gui/ui_elements, data/constants, pet/actions
minigames/{각 게임}.py ──→ minigames/base

network/manager.py ──→ network/{ble_central, ble_peripheral, wifi_socket, protocol}

pet/*.py ──→ data/constants
gui/sprites.py ──→ data/constants
data/save.py ──→ pet/pet.Pet (지연 import)
```
