"""
진화 시스템 - 진화 단계 및 분기 로직
"""
from data.constants import (
    STAGE_EGG, STAGE_BABY, STAGE_CHILD, STAGE_TEEN, STAGE_ADULT,
    STAGE_NAMES, EVOLUTION_LEVELS,
    TYPE_HAPPY, TYPE_SMART, TYPE_FOODIE, TYPE_BALANCED, TYPE_COLORS,
)


# ─── 진화 분기별 캐릭터 설명 ───
EVOLUTION_DESCRIPTIONS = {
    STAGE_EGG: {
        None: "신비로운 알이에요. 곧 무언가 태어날 것 같아요!",
    },
    STAGE_BABY: {
        None: "작고 귀여운 아기가 태어났어요! 잘 돌봐주세요.",
    },
    STAGE_CHILD: {
        TYPE_HAPPY: "활발하고 밝은 아이로 자랐어요! 웃음이 끊이지 않아요.",
        TYPE_SMART: "호기심 많고 똑똑한 아이로 자랐어요! 책을 좋아해요.",
        TYPE_FOODIE: "먹는 걸 좋아하는 귀여운 아이에요! 볼이 통통해요.",
        TYPE_BALANCED: "모든 면에서 균형 잡힌 특별한 아이에요!",
    },
    STAGE_TEEN: {
        TYPE_HAPPY: "활기 넘치는 청소년이에요! 춤추는 걸 좋아해요.",
        TYPE_SMART: "공부를 잘하는 모범생이에요! 안경이 잘 어울려요.",
        TYPE_FOODIE: "요리에 관심이 많은 미식가에요! 맛 감별사!",
        TYPE_BALANCED: "뭐든 잘하는 만능 청소년이에요! 빛나는 존재!",
    },
    STAGE_ADULT: {
        TYPE_HAPPY: "태양처럼 빛나는 댄서로 성장했어요! ⭐",
        TYPE_SMART: "천재 과학자가 되었어요! 발명의 달인! 🔬",
        TYPE_FOODIE: "전설의 셰프가 되었어요! 미슐랭 별 획득! 🍳",
        TYPE_BALANCED: "전설의 존재... 모든 능력을 갖춘 완벽체! 👑",
    },
}


def get_evolution_description(stage, evo_type):
    """현재 진화 단계의 설명 반환"""
    stage_descs = EVOLUTION_DESCRIPTIONS.get(stage, {})
    if evo_type and evo_type in stage_descs:
        return stage_descs[evo_type]
    return stage_descs.get(None, "신비로운 생명체에요!")


def get_stage_for_level(level):
    """레벨에 맞는 진화 단계 반환"""
    if level >= EVOLUTION_LEVELS[STAGE_ADULT]:
        return STAGE_ADULT
    elif level >= EVOLUTION_LEVELS[STAGE_TEEN]:
        return STAGE_TEEN
    elif level >= EVOLUTION_LEVELS[STAGE_CHILD]:
        return STAGE_CHILD
    elif level >= EVOLUTION_LEVELS[STAGE_BABY]:
        return STAGE_BABY
    return STAGE_EGG


def get_next_evolution_level(current_stage):
    """다음 진화까지 필요한 레벨 반환 (없으면 None)"""
    next_stages = {
        STAGE_EGG: STAGE_BABY,
        STAGE_BABY: STAGE_CHILD,
        STAGE_CHILD: STAGE_TEEN,
        STAGE_TEEN: STAGE_ADULT,
    }
    next_stage = next_stages.get(current_stage)
    if next_stage is not None:
        return EVOLUTION_LEVELS[next_stage]
    return None


def get_type_color(evo_type):
    """진화 타입에 맞는 색상 반환"""
    return TYPE_COLORS.get(evo_type, (200, 200, 200))
