"""
펫 케어 액션 - 밥주기, 놀기, 청소, 잠, 약, 훈련
"""
from data.constants import (
    FOODS, EXP_FEED, EXP_PLAY, EXP_PLAY_WIN, EXP_CLEAN,
    EXP_TRAIN, EXP_MEDICINE, STAT_MAX,
    GAME_REWARDS, TRAIN_REWARDS,
)


def feed(pet, food_name="밥"):
    """밥 주기 (인벤토리 시스템 적용)"""
    if not pet.alive or pet.stage == 0 or pet.sleeping:
        return {"success": False, "message": "지금은 밥을 줄 수 없어요!"}

    food = FOODS.get(food_name)
    if not food:
        return {"success": False, "message": "알 수 없는 음식이에요!"}

    # 무료 음식이 아닌 경우 인벤토리 확인
    if not food.get("free", False):
        count = pet.inventory.get(food_name, 0)
        if count <= 0:
            return {"success": False, "message": f"{food_name}이(가) 없어요! 게임에서 얻을 수 있어요."}
        pet.inventory[food_name] = count - 1
        if pet.inventory[food_name] <= 0:
            del pet.inventory[food_name]

    # 배고픔 감소 (hunger -> 낮아질수록 배부름)
    pet.hunger = pet.clamp_stat(pet.hunger + food["hunger"])
    pet.happiness = pet.clamp_stat(pet.happiness + food["happiness"])
    if "health" in food:
        pet.health = pet.clamp_stat(pet.health + food["health"])

    pet.feed_count += 1
    pet.bond += 1
    pet.add_exp(EXP_FEED)

    pet.mood = "eating"
    pet.mood_timer = 2.0

    return {
        "success": True,
        "message": f"{pet.name}에게 {food_name}을(를) 줬어요!",
        "exp": EXP_FEED,
    }


def play(pet, game_result="win"):
    """
    놀아주기 (미니게임 결과 반영)
    game_result: "win", "lose", "draw"
    """
    if not pet.alive or pet.stage == 0 or pet.sleeping:
        return {"success": False, "message": "지금은 놀 수 없어요!"}

    if pet.energy < 10:
        return {"success": False, "message": f"{pet.name}이(가) 너무 피곤해요..."}

    exp_gained = EXP_PLAY
    happiness_gain = 10

    if game_result == "win":
        exp_gained = EXP_PLAY_WIN
        happiness_gain = 20
    elif game_result == "draw":
        happiness_gain = 12

    pet.happiness = pet.clamp_stat(pet.happiness + happiness_gain)
    pet.energy = pet.clamp_stat(pet.energy - 15)
    pet.hunger = pet.clamp_stat(pet.hunger + 8)  # 놀면 배고파짐
    pet.play_count += 1
    pet.bond += 2
    pet.add_exp(exp_gained)

    pet.mood = "happy" if game_result == "win" else "normal"
    pet.mood_timer = 3.0

    # 보상은 미니게임 base.py에서 직접 인벤토리에 지급함
    # 여기서는 중복 지급하지 않음

    return {
        "success": True,
        "message": f"{pet.name}이(가) 즐겁게 놀았어요!",
        "exp": exp_gained,
        "result": game_result,
    }


def clean(pet):
    """청소하기"""
    if not pet.alive or pet.stage == 0:
        return {"success": False, "message": "지금은 청소할 수 없어요!"}

    pet.cleanliness = pet.clamp_stat(pet.cleanliness + 40)
    pet.happiness = pet.clamp_stat(pet.happiness + 5)
    pet.clean_count += 1
    pet.bond += 1
    pet.add_exp(EXP_CLEAN)

    return {
        "success": True,
        "message": f"{pet.name}이(가) 깨끗해졌어요!",
        "exp": EXP_CLEAN,
    }


def sleep(pet):
    """재우기 / 깨우기 토글"""
    if not pet.alive or pet.stage == 0:
        return {"success": False, "message": "지금은 안돼요!"}

    if pet.sleeping:
        pet.sleeping = False
        pet.mood = "normal"
        pet.mood_timer = 1.0
        return {
            "success": True,
            "message": f"{pet.name}이(가) 잠에서 깼어요!",
        }
    else:
        pet.sleeping = True
        pet.mood = "sleeping"
        pet.mood_timer = 0  # 잠자는 동안 계속 유지
        return {
            "success": True,
            "message": f"{pet.name}이(가) 잠들었어요... 💤",
        }


def give_medicine(pet):
    """약 주기"""
    if not pet.alive or pet.stage == 0:
        return {"success": False, "message": "지금은 안돼요!"}

    if not pet.sick:
        return {"success": False, "message": f"{pet.name}은(는) 아프지 않아요!"}

    pet.sick = False
    pet.health = pet.clamp_stat(pet.health + 30)
    pet.happiness = pet.clamp_stat(pet.happiness - 5)  # 약은 맛없어...
    pet.bond += 2
    pet.add_exp(EXP_MEDICINE)

    pet.mood = "normal"
    pet.mood_timer = 2.0

    return {
        "success": True,
        "message": f"{pet.name}이(가) 건강해졌어요!",
        "exp": EXP_MEDICINE,
    }


def train(pet):
    """훈련하기"""
    if not pet.alive or pet.stage == 0 or pet.sleeping:
        return {"success": False, "message": "지금은 훈련할 수 없어요!"}

    if pet.energy < 20:
        return {"success": False, "message": f"{pet.name}이(가) 너무 피곤해요..."}

    pet.intelligence += 1
    pet.energy = pet.clamp_stat(pet.energy - 20)
    pet.hunger = pet.clamp_stat(pet.hunger + 10)
    pet.happiness = pet.clamp_stat(pet.happiness + 5)
    pet.train_count += 1
    pet.bond += 2
    pet.add_exp(EXP_TRAIN)

    pet.mood = "excited"
    pet.mood_timer = 2.0

    # 훈련 보상 지급
    rewards = give_rewards(pet, TRAIN_REWARDS, "win")

    return {
        "success": True,
        "message": f"{pet.name}이(가) 열심히 훈련했어요!",
        "exp": EXP_TRAIN,
        "intelligence": pet.intelligence,
        "rewards": rewards,
    }


def give_rewards(pet, reward_table, result):
    """보상 테이블에 따라 인벤토리에 아이템 추가. 획득한 아이템 dict 반환"""
    items = reward_table.get(result, {})
    gained = {}
    for item_name, count in items.items():
        pet.inventory[item_name] = pet.inventory.get(item_name, 0) + count
        gained[item_name] = count
    return gained


def apply_special_food(pet, food_name="무지개 사탕"):
    """특별 음식 이벤트 사용"""
    if not pet.alive or pet.stage == 0:
        return {"success": False, "message": "지금은 안돼요!"}

    pet.hunger = pet.clamp_stat(pet.hunger - 30)
    pet.happiness = pet.clamp_stat(pet.happiness + 30)
    pet.health = pet.clamp_stat(pet.health + 10)

    pet.mood = "excited"
    pet.mood_timer = 3.0

    return {
        "success": True,
        "message": f"{pet.name}이(가) {food_name}을(를) 먹고 기뻐해요!",
    }
