"""
게임 상수 정의
다마고치 가상 펫 게임의 모든 수치/설정값
"""

# ─── 버전 ───
VERSION = "1.0.2"
GITHUB_REPO = "hjchoi00/damaproject"  # ← GitHub 아이디로 수정

# ─── 화면 설정 ───
SCREEN_WIDTH = 480
SCREEN_HEIGHT = 640
FPS = 30
TITLE = "다마고치 ♥"

# ─── 색상 팔레트 (파스텔톤) ───
COLOR_BG = (255, 245, 235)          # 크림색 배경
COLOR_BG_DARK = (240, 228, 215)     # 어두운 크림
COLOR_WHITE = (255, 255, 255)
COLOR_BLACK = (40, 40, 40)
COLOR_TEXT = (80, 60, 50)           # 따뜻한 갈색 텍스트
COLOR_ACCENT = (255, 140, 105)      # 코랄 핑크
COLOR_ACCENT2 = (120, 200, 180)     # 민트 그린
COLOR_ACCENT3 = (255, 200, 100)     # 따뜻한 노란색
COLOR_HEART = (255, 100, 120)       # 하트 색
COLOR_STAR = (255, 215, 0)          # 별 색
COLOR_GRAY = (180, 170, 165)        # 회색
COLOR_LIGHT_GRAY = (220, 215, 210)  # 밝은 회색

# 스탯 바 색상
COLOR_HUNGER = (255, 150, 80)       # 주황 (배고픔)
COLOR_HAPPY = (255, 200, 80)        # 노랑 (행복도)
COLOR_CLEAN = (100, 200, 255)       # 하늘 (청결도)
COLOR_HEALTH = (120, 220, 120)      # 초록 (건강)
COLOR_ENERGY = (180, 130, 255)      # 보라 (에너지)
COLOR_EXP = (255, 180, 200)         # 핑크 (경험치)

# 버튼 색상
COLOR_BTN = (255, 200, 180)         # 버튼 기본
COLOR_BTN_HOVER = (255, 170, 140)   # 버튼 호버
COLOR_BTN_PRESS = (230, 140, 110)   # 버튼 누름
COLOR_BTN_DISABLED = (200, 195, 190)

# ─── 펫 스탯 설정 ───
STAT_MIN = 0
STAT_MAX = 100

# 시간 경과에 따른 스탯 변화 (초당)
HUNGER_RATE = 0.15          # 배고픔 증가율 (높을수록 빨리 배고파짐)
HAPPINESS_DECAY = 0.08      # 행복도 감소율
CLEANLINESS_DECAY = 0.05    # 청결도 감소율
ENERGY_RECOVERY = 0.1       # 에너지 회복율 (잠잘 때)
ENERGY_DECAY = 0.03         # 에너지 자연 감소

# 스탯이 낮을 때 건강 영향 임계값
CRITICAL_THRESHOLD = 20     # 이 이하면 위험 상태
WARNING_THRESHOLD = 40      # 이 이하면 경고 상태
HEALTH_PENALTY_RATE = 0.1   # 위험 상태일 때 건강 감소율

# ─── 경험치 / 레벨 시스템 ───
# 레벨별 필요 경험치 (누적 아님, 각 레벨당)
def exp_for_level(level):
    """레벨업에 필요한 경험치 계산 (점진적 증가)"""
    return int(50 + level * 20 + (level ** 1.5) * 5)

MAX_LEVEL = 50

# 액션별 경험치
EXP_FEED = 5
EXP_PLAY = 15           # 미니게임 기본
EXP_PLAY_WIN = 25       # 미니게임 승리
EXP_CLEAN = 5
EXP_TRAIN = 20
EXP_MEDICINE = 3
EXP_SLEEP = 2           # 잠자기 (시간당)
EXP_SOCIAL = 30         # 다른 펫과 만남

# ─── 진화 시스템 ───
# 진화 단계
STAGE_EGG = 0       # 알
STAGE_BABY = 1      # 아기 (Lv 1~5)
STAGE_CHILD = 2     # 어린이 (Lv 6~15)
STAGE_TEEN = 3      # 청소년 (Lv 16~30)
STAGE_ADULT = 4     # 성인 (Lv 31~50)

STAGE_NAMES = {
    STAGE_EGG: "알",
    STAGE_BABY: "아기",
    STAGE_CHILD: "어린이",
    STAGE_TEEN: "청소년",
    STAGE_ADULT: "성인",
}

# 진화 레벨 경계
EVOLUTION_LEVELS = {
    STAGE_EGG: 0,
    STAGE_BABY: 1,
    STAGE_CHILD: 6,
    STAGE_TEEN: 16,
    STAGE_ADULT: 31,
}

# 진화 타입 (케어 패턴 기반)
TYPE_HAPPY = "활발형"       # 행복도 케어 위주
TYPE_SMART = "지능형"       # 훈련 위주
TYPE_FOODIE = "먹보형"      # 밥 위주
TYPE_BALANCED = "균형형"    # 레어 - 균형

TYPE_COLORS = {
    TYPE_HAPPY: (255, 180, 100),
    TYPE_SMART: (130, 170, 255),
    TYPE_FOODIE: (255, 140, 160),
    TYPE_BALANCED: (180, 230, 140),
}

# ─── 음식 종류 ───
# free=True: 언제든 무료 사용, free=False: 인벤토리에서 소모
FOODS = {
    "밥":     {"hunger": -30, "happiness": 5,  "weight": 3, "free": True},
    "간식":   {"hunger": -15, "happiness": 15, "weight": 5, "free": False},
    "샐러드": {"hunger": -20, "happiness": 3,  "weight": 1, "free": False},
    "케이크": {"hunger": -25, "happiness": 25, "weight": 8, "free": False},
    "약초차": {"hunger": -10, "happiness": 5,  "weight": 0, "health": 10, "free": False},
}

# 미니게임 보상 테이블 (결과 → 획득 아이템)
GAME_REWARDS = {
    "win":  {"간식": 1, "케이크": 1},
    "draw": {"간식": 1},
    "lose": {},
}

# 훈련 보상 테이블
TRAIN_REWARDS = {
    "win":  {"약초차": 1, "샐러드": 1},
    "draw": {"샐러드": 1},
    "lose": {},
}

# ─── 시간대 설정 ───
TIME_MORNING = (6, 12)      # 아침
TIME_AFTERNOON = (12, 18)   # 오후
TIME_EVENING = (18, 21)     # 저녁
TIME_NIGHT = (21, 6)        # 밤

# ─── 알 부화 시간 (초) ───
EGG_HATCH_TIME = 30  # 30초 후 부화 (테스트용, 실제로는 더 길게)

# ─── 자동 저장 간격 (초) ───
AUTO_SAVE_INTERVAL = 300  # 5분

# ─── 오프라인 경과 최대 시간 (초) ───
MAX_OFFLINE_TIME = 86400  # 24시간

# ─── 네트워크 설정 ───
BLE_SERVICE_UUID = "12345678-1234-5678-1234-56789abcdef0"
BLE_CHAR_PET_DATA_UUID = "12345678-1234-5678-1234-56789abcdef1"
BLE_CHAR_MESSAGE_UUID = "12345678-1234-5678-1234-56789abcdef2"

WIFI_DEFAULT_PORT = 19876
WIFI_BROADCAST_PORT = 19877
WIFI_DISCOVERY_MSG = "DAMAGOCHI_DISCOVER"

# 네트워크 메시지 타입
MSG_HELLO = "hello"
MSG_PET_INFO = "pet_info"
MSG_GIFT = "gift"
MSG_BATTLE_REQUEST = "battle_req"
MSG_BATTLE_CHOICE = "battle_choice"
MSG_BATTLE_RESULT = "battle_result"
MSG_BYE = "bye"

# ─── 랜덤 이벤트 확률 (매 분 체크) ───
EVENT_SICK_CHANCE = 0.02        # 2% 확률로 병 걸림
EVENT_TREASURE_CHANCE = 0.05    # 5% 확률로 보물 발견
EVENT_SPECIAL_FOOD_CHANCE = 0.03  # 3% 확률로 특별 음식

# ─── UI 레이아웃 ───
STAT_BAR_HEIGHT = 16
STAT_BAR_WIDTH = 120
STAT_PANEL_Y = 10
STAT_PANEL_X = 10

MENU_BTN_WIDTH = 130
MENU_BTN_HEIGHT = 50
MENU_PANEL_Y = 520

PET_AREA_Y = 180
PET_AREA_HEIGHT = 300

# ─── 폰트 크기 ───
FONT_SIZE_SMALL = 14
FONT_SIZE_MEDIUM = 20
FONT_SIZE_LARGE = 28
FONT_SIZE_TITLE = 36
