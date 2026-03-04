"""
저장/불러오기 시스템
JSON 기반 멀티 세이브 지원
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


def _load_raw():
    """저장 파일 원본 로드 + v1→v2 자동 마이그레이션"""
    if not SAVE_FILE.exists():
        return {"version": 2, "saves": []}

    try:
        with open(SAVE_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception:
        return {"version": 2, "saves": []}

    # v1 단일 세이브 → v2 멀티 세이브 마이그레이션
    if data.get("version", 1) == 1 and "pet" in data:
        saves = [{"saved_at": data.get("saved_at", time.time()),
                  "pet": data["pet"]}]
        new_data = {"version": 2, "saves": saves}
        _write_raw(new_data)
        return new_data

    return data


def _write_raw(data):
    """저장 파일 쓰기"""
    ensure_save_dir()
    try:
        with open(SAVE_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        print(f"[SAVE ERROR] {e}")
        return False


def save_pet(pet):
    """펫 데이터 저장 (이름 기준으로 업데이트 또는 추가)"""
    data = _load_raw()
    saves = data.get("saves", [])
    pet_dict = pet.to_dict()
    entry = {"saved_at": time.time(), "pet": pet_dict}

    # 같은 이름의 세이브가 있으면 덮어쓰기
    for i, s in enumerate(saves):
        if s.get("pet", {}).get("name") == pet.name:
            saves[i] = entry
            break
    else:
        saves.append(entry)

    data["version"] = 2
    data["saves"] = saves
    return _write_raw(data)


def load_pet():
    """첫 번째 저장된 펫 로드 (호환용)"""
    pets = load_all_pets()
    return pets[0] if pets else None


def load_all_pets():
    """모든 저장된 펫 목록 로드"""
    data = _load_raw()
    saves = data.get("saves", [])
    pets = []

    from pet.pet import Pet

    for s in saves:
        try:
            pet = Pet.from_dict(s["pet"])
            saved_at = s.get("saved_at", time.time())
            offline_seconds = time.time() - saved_at
            _apply_offline_time(pet, offline_seconds)
            pets.append(pet)
        except Exception as e:
            print(f"[LOAD ERROR] {e}")

    return pets


def delete_pet_save(name):
    """특정 이름의 펫 세이브 삭제"""
    data = _load_raw()
    saves = data.get("saves", [])
    data["saves"] = [s for s in saves if s.get("pet", {}).get("name") != name]
    return _write_raw(data)


def _apply_offline_time(pet, seconds):
    """오프라인 경과 시간에 따른 스탯 변화 적용"""
    from data.constants import (
        MAX_OFFLINE_TIME, HUNGER_RATE, HAPPINESS_DECAY,
        CLEANLINESS_DECAY, ENERGY_DECAY
    )

    if not pet.alive or pet.stage == 0:
        return

    seconds = min(seconds, MAX_OFFLINE_TIME)

    if seconds < 60:
        return

    decay_factor = 0.5
    pet.hunger = pet.clamp_stat(pet.hunger + HUNGER_RATE * seconds * decay_factor)
    pet.happiness = pet.clamp_stat(pet.happiness - HAPPINESS_DECAY * seconds * decay_factor)
    pet.cleanliness = pet.clamp_stat(pet.cleanliness - CLEANLINESS_DECAY * seconds * decay_factor)

    if pet.sleeping:
        pet.energy = pet.clamp_stat(pet.energy + 0.05 * seconds)
    else:
        pet.energy = pet.clamp_stat(pet.energy - ENERGY_DECAY * seconds * decay_factor)

    pet.last_update = time.time()


def has_save():
    """저장 파일에 최소 1개의 세이브가 있는지"""
    data = _load_raw()
    return len(data.get("saves", [])) > 0


def delete_save():
    """저장 파일 전체 삭제 (새 게임용)"""
    if SAVE_FILE.exists():
        os.remove(SAVE_FILE)
        return True
    return False
