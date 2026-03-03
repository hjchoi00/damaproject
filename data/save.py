"""
저장/불러오기 시스템
JSON 기반 펫 데이터 영속화
"""
import json
import os
import time
from pathlib import Path


SAVE_DIR = Path.home() / ".damagochi"
SAVE_FILE = SAVE_DIR / "save.json"


def ensure_save_dir():
    """저장 디렉터리 생성"""
    SAVE_DIR.mkdir(parents=True, exist_ok=True)


def save_pet(pet):
    """펫 데이터를 JSON 파일로 저장"""
    ensure_save_dir()
    data = {
        "version": 1,
        "saved_at": time.time(),
        "pet": pet.to_dict(),
    }
    try:
        with open(SAVE_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        print(f"[SAVE ERROR] {e}")
        return False


def load_pet():
    """
    저장된 펫 데이터 로드
    Returns: Pet 객체 또는 None (저장 파일 없음)
    """
    if not SAVE_FILE.exists():
        return None

    try:
        with open(SAVE_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)

        from pet.pet import Pet
        pet = Pet.from_dict(data["pet"])

        # 오프라인 경과 시간 처리
        saved_at = data.get("saved_at", time.time())
        offline_seconds = time.time() - saved_at
        _apply_offline_time(pet, offline_seconds)

        return pet
    except Exception as e:
        print(f"[LOAD ERROR] {e}")
        return None


def _apply_offline_time(pet, seconds):
    """오프라인 경과 시간에 따른 스탯 변화 적용"""
    from data.constants import (
        MAX_OFFLINE_TIME, HUNGER_RATE, HAPPINESS_DECAY,
        CLEANLINESS_DECAY, ENERGY_DECAY
    )

    if not pet.alive or pet.stage == 0:
        return

    # 최대 24시간분만 적용
    seconds = min(seconds, MAX_OFFLINE_TIME)

    if seconds < 60:  # 1분 이하는 무시
        return

    # 오프라인 동안의 스탯 변화 (감쇠 계수 0.5 적용 - 자비)
    decay_factor = 0.5
    pet.hunger = pet.clamp_stat(pet.hunger + HUNGER_RATE * seconds * decay_factor)
    pet.happiness = pet.clamp_stat(pet.happiness - HAPPINESS_DECAY * seconds * decay_factor)
    pet.cleanliness = pet.clamp_stat(pet.cleanliness - CLEANLINESS_DECAY * seconds * decay_factor)

    # 오프라인 중 잠자고 있었다면 에너지 회복
    if pet.sleeping:
        pet.energy = pet.clamp_stat(pet.energy + 0.05 * seconds)
    else:
        pet.energy = pet.clamp_stat(pet.energy - ENERGY_DECAY * seconds * decay_factor)

    pet.last_update = time.time()


def delete_save():
    """저장 파일 삭제 (새 게임용)"""
    if SAVE_FILE.exists():
        os.remove(SAVE_FILE)
        return True
    return False


def has_save():
    """저장 파일 존재 여부"""
    return SAVE_FILE.exists()
