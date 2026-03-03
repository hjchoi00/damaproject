"""
Pet 클래스 - 다마고치 가상 펫의 핵심 엔티티
"""
import time
import random
from data.constants import (
    STAT_MIN, STAT_MAX, HUNGER_RATE, HAPPINESS_DECAY,
    CLEANLINESS_DECAY, ENERGY_DECAY, HEALTH_PENALTY_RATE,
    CRITICAL_THRESHOLD, WARNING_THRESHOLD, MAX_LEVEL,
    exp_for_level, STAGE_EGG, STAGE_BABY, STAGE_CHILD,
    STAGE_TEEN, STAGE_ADULT, EVOLUTION_LEVELS, STAGE_NAMES,
    TYPE_HAPPY, TYPE_SMART, TYPE_FOODIE, TYPE_BALANCED,
    EGG_HATCH_TIME, EVENT_SICK_CHANCE, EVENT_TREASURE_CHANCE,
    EVENT_SPECIAL_FOOD_CHANCE, EXP_SOCIAL
)


class Pet:
    """가상 펫 클래스"""

    def __init__(self, name="", owner_id=None):
        # 기본 정보
        self.name = name
        self.owner_id = owner_id or str(random.randint(10000, 99999))
        self.created_at = time.time()
        self.last_update = time.time()

        # 현재 상태
        self.alive = True
        self.sleeping = False
        self.sick = False

        # 기본 스탯 (0~100)
        self.hunger = 50.0        # 배고픔 (높을수록 배고픔 → 밥줘야 함)
        self.happiness = 70.0     # 행복도
        self.cleanliness = 80.0   # 청결도
        self.health = 100.0       # 건강
        self.energy = 100.0       # 에너지 (0이면 졸림)

        # 성장 스탯
        self.level = 0
        self.exp = 0
        self.stage = STAGE_EGG
        self.evolution_type = None  # 아직 미결정

        # 숨겨진 스탯 (진화 분기에 영향)
        self.bond = 0.0           # 친밀도 (총 케어 횟수 기반)
        self.intelligence = 0.0   # 지능 (훈련 횟수)
        self.play_count = 0       # 놀아준 횟수
        self.feed_count = 0       # 밥 준 횟수
        self.train_count = 0      # 훈련 횟수
        self.clean_count = 0      # 청소 횟수

        # 알 관련
        self.egg_timer = 0.0        # 알 상태 경과시간
        self.hatched = False

        # 인벤토리 (음식 이름 → 개수)
        self.inventory = {}

        # 이벤트/알림 큐
        self.pending_events = []    # [{"type": "...", "data": {...}}]

        # 표정/애니메이션 상태
        self.mood = "normal"        # normal, happy, sad, eating, sleeping, sick, excited
        self.mood_timer = 0.0       # 표정 지속 시간

    # ─── 스탯 관리 ───

    def clamp_stat(self, value):
        """스탯을 0~100 범위로 제한"""
        return max(STAT_MIN, min(STAT_MAX, value))

    def get_satiety(self):
        """포만감 (100 - 배고픔). 높을수록 배부름"""
        return STAT_MAX - self.hunger

    # ─── 시간 경과 업데이트 ───

    def update(self, dt):
        """
        매 프레임 호출. dt = 경과 시간(초)
        스탯 자연 변화, 이벤트 발생 등 처리
        """
        if not self.alive:
            return

        # 알 상태
        if self.stage == STAGE_EGG:
            self._update_egg(dt)
            return

        # 표정 타이머
        if self.mood_timer > 0:
            self.mood_timer -= dt
            if self.mood_timer <= 0:
                self.mood = self._calculate_mood()

        # 잠자는 중
        if self.sleeping:
            self._update_sleeping(dt)
            return

        # 스탯 자연 변화
        self.hunger = self.clamp_stat(self.hunger + HUNGER_RATE * dt)
        self.happiness = self.clamp_stat(self.happiness - HAPPINESS_DECAY * dt)
        self.cleanliness = self.clamp_stat(self.cleanliness - CLEANLINESS_DECAY * dt)
        self.energy = self.clamp_stat(self.energy - ENERGY_DECAY * dt)

        # 위험 상태 → 건강 감소
        critical_count = sum(1 for s in [self.get_satiety(), self.happiness, self.cleanliness]
                             if s < CRITICAL_THRESHOLD)
        if critical_count > 0:
            self.health = self.clamp_stat(
                self.health - HEALTH_PENALTY_RATE * critical_count * dt
            )

        # 병 상태 → 지속 건강 손실
        if self.sick:
            self.health = self.clamp_stat(self.health - 0.2 * dt)
            self.happiness = self.clamp_stat(self.happiness - 0.1 * dt)

        # 건강 0 → 사망
        if self.health <= 0:
            self.alive = False
            self.pending_events.append({"type": "death", "data": {}})
            return

        # 자동 표정 업데이트
        if self.mood_timer <= 0:
            self.mood = self._calculate_mood()

        self.last_update = time.time()

    def _update_egg(self, dt):
        """알 상태 업데이트"""
        self.egg_timer += dt
        if self.egg_timer >= EGG_HATCH_TIME:
            self.hatched = True
            self.stage = STAGE_BABY
            self.level = 1
            self.pending_events.append({"type": "hatch", "data": {}})

    def _update_sleeping(self, dt):
        """수면 중 업데이트"""
        from data.constants import ENERGY_RECOVERY
        self.energy = self.clamp_stat(self.energy + ENERGY_RECOVERY * dt)
        self.hunger = self.clamp_stat(self.hunger + HUNGER_RATE * 0.3 * dt)  # 잠잘 때 배고픔 느리게

        # 에너지 충분하면 자동 기상
        if self.energy >= 95:
            self.sleeping = False
            self.mood = "happy"
            self.mood_timer = 3.0
            self.pending_events.append({"type": "wake_up", "data": {}})

    def _calculate_mood(self):
        """현재 스탯 기반으로 표정 결정"""
        if self.sick:
            return "sick"
        if self.sleeping:
            return "sleeping"
        if self.energy < 20:
            return "sleepy"
        if self.hunger > 80:
            return "hungry"
        if self.happiness < 30:
            return "sad"
        if self.happiness > 80 and self.health > 70:
            return "happy"
        return "normal"

    # ─── 랜덤 이벤트 체크 (매 분) ───

    def check_random_events(self):
        """분 단위로 호출하여 랜덤 이벤트 체크"""
        if self.stage == STAGE_EGG or not self.alive:
            return

        # 병 걸림
        if not self.sick and random.random() < EVENT_SICK_CHANCE:
            if self.health < 60 or self.cleanliness < 30:
                self.sick = True
                self.mood = "sick"
                self.mood_timer = 5.0
                self.pending_events.append({"type": "sick", "data": {}})

        # 보물 발견
        if random.random() < EVENT_TREASURE_CHANCE:
            bonus_exp = random.randint(10, 30)
            self.add_exp(bonus_exp)
            self.pending_events.append({
                "type": "treasure",
                "data": {"exp": bonus_exp}
            })

        # 특별 음식
        if random.random() < EVENT_SPECIAL_FOOD_CHANCE:
            self.pending_events.append({
                "type": "special_food",
                "data": {"food": "무지개 사탕"}
            })

    # ─── 경험치 / 레벨 ───

    def add_exp(self, amount):
        """경험치 추가 및 레벨업 처리"""
        if self.stage == STAGE_EGG or not self.alive:
            return

        self.exp += amount

        while self.level < MAX_LEVEL:
            needed = exp_for_level(self.level)
            if self.exp >= needed:
                self.exp -= needed
                self.level += 1
                self._on_level_up()
            else:
                break

    def _on_level_up(self):
        """레벨업 시 처리"""
        self.pending_events.append({
            "type": "level_up",
            "data": {"level": self.level}
        })

        # 진화 체크
        old_stage = self.stage
        new_stage = self._calculate_stage()
        if new_stage > old_stage:
            self.stage = new_stage
            self._on_evolve(old_stage, new_stage)

    def _calculate_stage(self):
        """현재 레벨에 맞는 진화 단계 반환"""
        if self.level >= EVOLUTION_LEVELS[STAGE_ADULT]:
            return STAGE_ADULT
        elif self.level >= EVOLUTION_LEVELS[STAGE_TEEN]:
            return STAGE_TEEN
        elif self.level >= EVOLUTION_LEVELS[STAGE_CHILD]:
            return STAGE_CHILD
        elif self.level >= EVOLUTION_LEVELS[STAGE_BABY]:
            return STAGE_BABY
        return STAGE_EGG

    def _on_evolve(self, old_stage, new_stage):
        """진화 시 처리"""
        # 진화 타입 결정 (어린이 단계부터)
        if new_stage >= STAGE_CHILD and self.evolution_type is None:
            self.evolution_type = self._determine_type()

        self.pending_events.append({
            "type": "evolve",
            "data": {
                "from_stage": STAGE_NAMES[old_stage],
                "to_stage": STAGE_NAMES[new_stage],
                "type": self.evolution_type,
            }
        })

        # 진화 보너스
        self.happiness = self.clamp_stat(self.happiness + 20)
        self.health = self.clamp_stat(self.health + 10)

    def _determine_type(self):
        """케어 히스토리 기반 진화 타입 결정"""
        total = self.play_count + self.feed_count + self.train_count + 1
        play_ratio = self.play_count / total
        feed_ratio = self.feed_count / total
        train_ratio = self.train_count / total

        # 가장 높은 비율의 타입으로 결정
        ratios = {
            TYPE_HAPPY: play_ratio,
            TYPE_FOODIE: feed_ratio,
            TYPE_SMART: train_ratio,
        }
        max_ratio = max(ratios.values())

        # 차이가 크지 않으면 균형형 (레어)
        if max_ratio < 0.4:
            return TYPE_BALANCED

        return max(ratios, key=ratios.get)

    # ─── 직렬화 ───

    def to_dict(self):
        """저장용 딕셔너리 반환"""
        return {
            "name": self.name,
            "owner_id": self.owner_id,
            "created_at": self.created_at,
            "last_update": self.last_update,
            "alive": self.alive,
            "sleeping": self.sleeping,
            "sick": self.sick,
            "hunger": self.hunger,
            "happiness": self.happiness,
            "cleanliness": self.cleanliness,
            "health": self.health,
            "energy": self.energy,
            "level": self.level,
            "exp": self.exp,
            "stage": self.stage,
            "evolution_type": self.evolution_type,
            "bond": self.bond,
            "intelligence": self.intelligence,
            "play_count": self.play_count,
            "feed_count": self.feed_count,
            "train_count": self.train_count,
            "clean_count": self.clean_count,
            "egg_timer": self.egg_timer,
            "hatched": self.hatched,
            "inventory": self.inventory,
        }

    @classmethod
    def from_dict(cls, data):
        """딕셔너리에서 Pet 객체 복원"""
        pet = cls(name=data.get("name", ""), owner_id=data.get("owner_id"))
        pet.created_at = data.get("created_at", time.time())
        pet.last_update = data.get("last_update", time.time())
        pet.alive = data.get("alive", True)
        pet.sleeping = data.get("sleeping", False)
        pet.sick = data.get("sick", False)
        pet.hunger = data.get("hunger", 50.0)
        pet.happiness = data.get("happiness", 70.0)
        pet.cleanliness = data.get("cleanliness", 80.0)
        pet.health = data.get("health", 100.0)
        pet.energy = data.get("energy", 100.0)
        pet.level = data.get("level", 0)
        pet.exp = data.get("exp", 0)
        pet.stage = data.get("stage", STAGE_EGG)
        pet.evolution_type = data.get("evolution_type")
        pet.bond = data.get("bond", 0.0)
        pet.intelligence = data.get("intelligence", 0.0)
        pet.play_count = data.get("play_count", 0)
        pet.feed_count = data.get("feed_count", 0)
        pet.train_count = data.get("train_count", 0)
        pet.clean_count = data.get("clean_count", 0)
        pet.egg_timer = data.get("egg_timer", 0.0)
        pet.hatched = data.get("hatched", False)
        pet.inventory = data.get("inventory", {})
        return pet

    def get_brief_info(self):
        """네트워크 전송용 간략 정보"""
        return {
            "name": self.name,
            "level": self.level,
            "stage": self.stage,
            "type": self.evolution_type,
            "happiness": int(self.happiness),
            "owner_id": self.owner_id,
        }

    def get_exp_progress(self):
        """현재 레벨 경험치 진행률 (0.0 ~ 1.0)"""
        if self.level >= MAX_LEVEL:
            return 1.0
        needed = exp_for_level(self.level)
        return self.exp / needed if needed > 0 else 0

    def __repr__(self):
        return (f"Pet(name={self.name!r}, lv={self.level}, "
                f"stage={STAGE_NAMES.get(self.stage, '?')}, "
                f"hp={self.health:.0f}, happy={self.happiness:.0f})")
