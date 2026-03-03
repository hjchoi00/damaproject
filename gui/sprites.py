"""
픽셀아트 스프라이트 생성기
코드로 직접 귀여운 캐릭터를 그립니다 (외부 에셋 불필요)
각 진화 단계 × 타입 × 표정별 스프라이트 생성
"""
import pygame
from data.constants import (
    STAGE_EGG, STAGE_BABY, STAGE_CHILD, STAGE_TEEN, STAGE_ADULT,
    TYPE_HAPPY, TYPE_SMART, TYPE_FOODIE, TYPE_BALANCED, TYPE_COLORS,
    COLOR_WHITE, COLOR_BLACK, COLOR_ACCENT, COLOR_ACCENT3, COLOR_HEART,
)


# 기본 픽셀 크기 (한 "도트")
PX = 4


def _make_surface(w_dots, h_dots):
    """도트 기반 서피스 생성 (투명 배경)"""
    surf = pygame.Surface((w_dots * PX, h_dots * PX), pygame.SRCALPHA)
    return surf


def _draw_dot(surf, x, y, color):
    """한 개의 도트 그리기"""
    pygame.draw.rect(surf, color, (x * PX, y * PX, PX, PX))


def _draw_dots(surf, dots, color):
    """여러 도트 한번에 그리기. dots: [(x,y), ...]"""
    for x, y in dots:
        _draw_dot(surf, x, y, color)


def _mirror_dots_h(dots, center_x):
    """좌우 대칭 도트 생성"""
    mirrored = []
    for x, y in dots:
        mirrored.append((x, y))
        mx = 2 * center_x - x - 1
        if mx != x:
            mirrored.append((mx, y))
    return mirrored


# ═══════════════════════════════════════════════
# 알 (Egg) 스프라이트
# ═══════════════════════════════════════════════

def draw_egg(mood="normal"):
    """알 스프라이트 (16x20 도트)"""
    surf = _make_surface(16, 20)

    # 알 외곽선
    body_color = (255, 235, 210)
    outline = (180, 150, 120)
    crack_color = (220, 200, 170)
    spot_color = (255, 200, 180)

    # 알 모양 (타원형)
    center_x = 8
    # 상단부터 아래로 각 행의 범위
    egg_rows = [
        (6, 9),    # 0
        (5, 10),   # 1
        (4, 11),   # 2
        (3, 12),   # 3
        (3, 12),   # 4
        (2, 13),   # 5
        (2, 13),   # 6
        (2, 13),   # 7
        (2, 13),   # 8
        (2, 13),   # 9
        (2, 13),   # 10
        (3, 12),   # 11
        (3, 12),   # 12
        (3, 12),   # 13
        (4, 11),   # 14
        (4, 11),   # 15
        (5, 10),   # 16
        (6, 9),    # 17
    ]

    y_off = 1
    for i, (left, right) in enumerate(egg_rows):
        y = y_off + i
        # 외곽선
        _draw_dot(surf, left, y, outline)
        _draw_dot(surf, right, y, outline)
        # 채우기
        for x in range(left + 1, right):
            _draw_dot(surf, x, y, body_color)

    # 상단/하단 외곽
    for x in range(egg_rows[0][0], egg_rows[0][1] + 1):
        _draw_dot(surf, x, y_off, outline)
    for x in range(egg_rows[-1][0], egg_rows[-1][1] + 1):
        _draw_dot(surf, x, y_off + len(egg_rows) - 1, outline)

    # 귀여운 무늬 (하트 또는 별)
    _draw_dot(surf, 5, 6 + y_off, spot_color)
    _draw_dot(surf, 6, 5 + y_off, spot_color)
    _draw_dot(surf, 10, 8 + y_off, spot_color)
    _draw_dot(surf, 9, 7 + y_off, spot_color)

    # 금 (부화 중이면)
    if mood == "hatching":
        crack_dots = [(6, 9 + y_off), (7, 10 + y_off), (8, 9 + y_off),
                      (9, 10 + y_off), (7, 11 + y_off)]
        _draw_dots(surf, crack_dots, crack_color)

    return surf


# ═══════════════════════════════════════════════
# 아기 (Baby) 스프라이트
# ═══════════════════════════════════════════════

def _get_baby_body_color(evo_type):
    """타입별 몸 색상"""
    colors = {
        TYPE_HAPPY: (255, 220, 180),
        TYPE_SMART: (200, 220, 255),
        TYPE_FOODIE: (255, 200, 200),
        TYPE_BALANCED: (220, 255, 220),
        None: (255, 230, 200),
    }
    return colors.get(evo_type, (255, 230, 200))


def draw_baby(mood="normal", evo_type=None):
    """아기 스프라이트 (20x24 도트)"""
    surf = _make_surface(20, 24)
    body = _get_baby_body_color(evo_type)
    outline = (140, 120, 100)
    cheek = (255, 180, 180)
    eye_color = (60, 50, 40)

    # 몸통 (둥근 형태) - 심플한 슬라임 같은 모양
    cx = 10
    body_rows = [
        (7, 12),    # 0  머리 꼭대기
        (6, 13),    # 1
        (5, 14),    # 2
        (4, 15),    # 3
        (4, 15),    # 4
        (3, 16),    # 5
        (3, 16),    # 6
        (3, 16),    # 7
        (3, 16),    # 8
        (3, 16),    # 9
        (3, 16),    # 10
        (4, 15),    # 11
        (4, 15),    # 12 몸통
        (4, 15),    # 13
        (5, 14),    # 14
        (5, 14),    # 15
        (6, 13),    # 16
        (7, 12),    # 17
    ]

    y_off = 3
    for i, (left, right) in enumerate(body_rows):
        y = y_off + i
        _draw_dot(surf, left, y, outline)
        _draw_dot(surf, right, y, outline)
        for x in range(left + 1, right):
            _draw_dot(surf, x, y, body)

    # 상하단 외곽
    for x in range(body_rows[0][0], body_rows[0][1] + 1):
        _draw_dot(surf, x, y_off, outline)
    for x in range(body_rows[-1][0], body_rows[-1][1] + 1):
        _draw_dot(surf, x, y_off + len(body_rows) - 1, outline)

    # 귀 (작은 삼각형)
    _draw_dots(surf, [(5, y_off - 1), (4, y_off - 2)], outline)
    _draw_dots(surf, [(14, y_off - 1), (15, y_off - 2)], outline)
    _draw_dot(surf, 5, y_off - 1, body)
    _draw_dot(surf, 14, y_off - 1, body)

    # 눈
    ey = y_off + 5
    if mood == "happy" or mood == "excited":
        # 웃는 눈 (^  ^)
        _draw_dots(surf, [(7, ey), (6, ey - 1), (8, ey - 1)], eye_color)
        _draw_dots(surf, [(12, ey), (11, ey - 1), (13, ey - 1)], eye_color)
    elif mood == "sad" or mood == "hungry":
        # 슬픈 눈
        _draw_dots(surf, [(7, ey), (7, ey + 1)], eye_color)
        _draw_dots(surf, [(12, ey), (12, ey + 1)], eye_color)
        # 눈물
        _draw_dot(surf, 7, ey + 2, (100, 180, 255))
    elif mood == "sleeping" or mood == "sleepy":
        # 감긴 눈 (- -)
        _draw_dots(surf, [(6, ey), (7, ey), (8, ey)], eye_color)
        _draw_dots(surf, [(11, ey), (12, ey), (13, ey)], eye_color)
    elif mood == "sick":
        # x x 눈
        _draw_dots(surf, [(6, ey - 1), (8, ey + 1), (8, ey - 1), (6, ey + 1)], eye_color)
        _draw_dots(surf, [(11, ey - 1), (13, ey + 1), (13, ey - 1), (11, ey + 1)], eye_color)
    elif mood == "eating":
        # 맛있는 눈 (> <)
        _draw_dots(surf, [(7, ey)], eye_color)
        _draw_dots(surf, [(12, ey)], eye_color)
        _draw_dots(surf, [(6, ey - 1), (6, ey + 1)], eye_color)
        _draw_dots(surf, [(13, ey - 1), (13, ey + 1)], eye_color)
    else:
        # 기본 눈 (동그란)
        _draw_dots(surf, [(7, ey), (7, ey - 1)], eye_color)
        _draw_dots(surf, [(12, ey), (12, ey - 1)], eye_color)
        # 하이라이트
        _draw_dot(surf, 7, ey - 1, COLOR_WHITE)
        _draw_dot(surf, 12, ey - 1, COLOR_WHITE)

    # 볼 터치
    _draw_dot(surf, 5, ey + 2, cheek)
    _draw_dot(surf, 14, ey + 2, cheek)

    # 입
    my = ey + 3
    if mood == "happy" or mood == "excited":
        _draw_dots(surf, [(9, my), (10, my)], eye_color)
        _draw_dots(surf, [(8, my - 1), (11, my - 1)], eye_color)
    elif mood == "sad" or mood == "sick":
        _draw_dots(surf, [(9, my - 1), (10, my - 1)], eye_color)
        _draw_dots(surf, [(8, my), (11, my)], eye_color)
    elif mood == "eating":
        _draw_dots(surf, [(8, my), (9, my), (10, my), (11, my)], eye_color)
        _draw_dots(surf, [(8, my - 1), (11, my - 1)], eye_color)
    else:
        _draw_dots(surf, [(9, my), (10, my)], eye_color)

    # 발
    fy = y_off + len(body_rows)
    _draw_dots(surf, [(6, fy), (7, fy)], outline)
    _draw_dots(surf, [(12, fy), (13, fy)], outline)

    return surf


# ═══════════════════════════════════════════════
# 어린이 (Child) 스프라이트
# ═══════════════════════════════════════════════

def draw_child(mood="normal", evo_type=None):
    """어린이 스프라이트 (24x28 도트) - 타입별 특징 추가"""
    surf = _make_surface(24, 28)
    body = _get_baby_body_color(evo_type)
    outline = (130, 110, 90)
    eye_color = (50, 40, 35)
    cheek = (255, 170, 170)

    cx = 12
    # 머리 (큰 원형)
    head_rows = [
        (8, 15),   # 0
        (7, 16),   # 1
        (6, 17),   # 2
        (5, 18),   # 3
        (5, 18),   # 4
        (4, 19),   # 5
        (4, 19),   # 6
        (4, 19),   # 7
        (5, 18),   # 8
        (5, 18),   # 9
        (6, 17),   # 10
    ]

    y_off = 2
    for i, (left, right) in enumerate(head_rows):
        y = y_off + i
        _draw_dot(surf, left, y, outline)
        _draw_dot(surf, right, y, outline)
        for x in range(left + 1, right):
            _draw_dot(surf, x, y, body)
    for x in range(head_rows[0][0], head_rows[0][1] + 1):
        _draw_dot(surf, x, y_off, outline)

    # 귀
    _draw_dots(surf, [(5, y_off - 1), (4, y_off - 2), (3, y_off - 3)], outline)
    _draw_dots(surf, [(18, y_off - 1), (19, y_off - 2), (20, y_off - 3)], outline)
    _draw_dot(surf, 4, y_off - 1, body)
    _draw_dot(surf, 19, y_off - 1, body)

    # 몸통
    body_y = y_off + len(head_rows)
    body_rows = [
        (7, 16),   # 0
        (7, 16),   # 1
        (7, 16),   # 2
        (8, 15),   # 3
        (8, 15),   # 4
        (8, 15),   # 5
        (9, 14),   # 6
    ]
    for i, (left, right) in enumerate(body_rows):
        y = body_y + i
        _draw_dot(surf, left, y, outline)
        _draw_dot(surf, right, y, outline)
        for x in range(left + 1, right):
            # 배 부분은 밝은색
            belly = tuple(min(255, c + 30) for c in body)
            _draw_dot(surf, x, y, belly if 9 <= x <= 14 else body)

    # 팔
    _draw_dots(surf, [(6, body_y + 1), (5, body_y + 2), (5, body_y + 3)], outline)
    _draw_dots(surf, [(17, body_y + 1), (18, body_y + 2), (18, body_y + 3)], outline)

    # 발
    fy = body_y + len(body_rows)
    _draw_dots(surf, [(8, fy), (7, fy), (7, fy + 1)], outline)
    _draw_dots(surf, [(15, fy), (16, fy), (16, fy + 1)], outline)

    # 눈 (더 큰 눈)
    ey = y_off + 4
    if mood == "happy" or mood == "excited":
        _draw_dots(surf, [(8, ey), (7, ey - 1), (9, ey - 1)], eye_color)
        _draw_dots(surf, [(15, ey), (14, ey - 1), (16, ey - 1)], eye_color)
    elif mood == "sad":
        _draw_dots(surf, [(8, ey), (8, ey - 1)], eye_color)
        _draw_dots(surf, [(15, ey), (15, ey - 1)], eye_color)
        _draw_dot(surf, 8, ey + 1, (100, 180, 255))
        _draw_dot(surf, 15, ey + 1, (100, 180, 255))
    elif mood == "sleeping" or mood == "sleepy":
        _draw_dots(surf, [(7, ey), (8, ey), (9, ey)], eye_color)
        _draw_dots(surf, [(14, ey), (15, ey), (16, ey)], eye_color)
    elif mood == "sick":
        _draw_dots(surf, [(7, ey - 1), (9, ey + 1), (9, ey - 1), (7, ey + 1)], eye_color)
        _draw_dots(surf, [(14, ey - 1), (16, ey + 1), (16, ey - 1), (14, ey + 1)], eye_color)
    elif mood == "eating":
        _draw_dots(surf, [(8, ey)], eye_color)
        _draw_dots(surf, [(15, ey)], eye_color)
    else:
        _draw_dots(surf, [(8, ey), (8, ey - 1), (9, ey), (9, ey - 1)], eye_color)
        _draw_dots(surf, [(14, ey), (14, ey - 1), (15, ey), (15, ey - 1)], eye_color)
        _draw_dot(surf, 8, ey - 1, COLOR_WHITE)
        _draw_dot(surf, 14, ey - 1, COLOR_WHITE)

    # 볼
    _draw_dots(surf, [(6, ey + 2), (6, ey + 3)], cheek)
    _draw_dots(surf, [(17, ey + 2), (17, ey + 3)], cheek)

    # 입
    my = ey + 4
    if mood == "happy" or mood == "excited":
        _draw_dots(surf, [(10, my), (11, my), (12, my), (13, my)], eye_color)
        _draw_dots(surf, [(9, my - 1), (14, my - 1)], eye_color)
    elif mood == "sad" or mood == "sick":
        _draw_dots(surf, [(10, my - 1), (11, my - 1), (12, my - 1), (13, my - 1)], eye_color)
        _draw_dots(surf, [(9, my), (14, my)], eye_color)
    else:
        _draw_dots(surf, [(10, my), (11, my), (12, my), (13, my)], eye_color)

    # 타입별 악세서리
    if evo_type == TYPE_SMART:
        # 안경
        _draw_dots(surf, [(6, ey - 1), (7, ey - 2), (8, ey - 2), (9, ey - 2), (10, ey - 1)], (100, 100, 120))
        _draw_dots(surf, [(13, ey - 1), (14, ey - 2), (15, ey - 2), (16, ey - 2), (17, ey - 1)], (100, 100, 120))
        _draw_dots(surf, [(10, ey - 2), (11, ey - 2), (12, ey - 2), (13, ey - 2)], (100, 100, 120))
    elif evo_type == TYPE_HAPPY:
        # 꽃
        flower_c = (255, 150, 200)
        _draw_dots(surf, [(17, y_off - 1), (18, y_off - 2), (17, y_off - 3), (16, y_off - 2)], flower_c)
        _draw_dot(surf, 17, y_off - 2, (255, 255, 100))
    elif evo_type == TYPE_FOODIE:
        # 나뭇잎 (머리 위)
        leaf_c = (100, 200, 100)
        _draw_dots(surf, [(11, y_off - 2), (12, y_off - 2), (11, y_off - 1), (12, y_off - 3)], leaf_c)

    return surf


# ═══════════════════════════════════════════════
# 청소년 (Teen) & 성인 (Adult) - 더 큰 스프라이트
# ═══════════════════════════════════════════════

def draw_teen(mood="normal", evo_type=None):
    """청소년 스프라이트 (28x32 도트)"""
    surf = _make_surface(28, 32)
    body = _get_baby_body_color(evo_type)
    outline = (120, 100, 80)
    eye_color = (45, 35, 30)
    cheek = (255, 165, 165)

    cx = 14
    # 머리
    head_rows = [
        (10, 17),   # 0
        (9, 18),    # 1
        (8, 19),    # 2
        (7, 20),    # 3
        (6, 21),    # 4
        (6, 21),    # 5
        (5, 22),    # 6
        (5, 22),    # 7
        (5, 22),    # 8
        (5, 22),    # 9
        (6, 21),    # 10
        (6, 21),    # 11
        (7, 20),    # 12
    ]

    y_off = 2
    for i, (left, right) in enumerate(head_rows):
        y = y_off + i
        _draw_dot(surf, left, y, outline)
        _draw_dot(surf, right, y, outline)
        for x in range(left + 1, right):
            _draw_dot(surf, x, y, body)
    for x in range(head_rows[0][0], head_rows[0][1] + 1):
        _draw_dot(surf, x, y_off, outline)

    # 귀 (더 크게)
    _draw_dots(surf, [(6, y_off - 1), (5, y_off - 2), (4, y_off - 3), (4, y_off - 4)], outline)
    _draw_dots(surf, [(21, y_off - 1), (22, y_off - 2), (23, y_off - 3), (23, y_off - 4)], outline)
    _draw_dots(surf, [(5, y_off - 1), (5, y_off - 2)], body)
    _draw_dots(surf, [(22, y_off - 1), (22, y_off - 2)], body)

    # 몸통 (더 길쭉)
    body_y = y_off + len(head_rows)
    body_rows = [
        (8, 19),    # 0
        (8, 19),    # 1
        (8, 19),    # 2
        (8, 19),    # 3
        (9, 18),    # 4
        (9, 18),    # 5
        (9, 18),    # 6
        (10, 17),   # 7
        (10, 17),   # 8
    ]
    for i, (left, right) in enumerate(body_rows):
        y = body_y + i
        _draw_dot(surf, left, y, outline)
        _draw_dot(surf, right, y, outline)
        for x in range(left + 1, right):
            belly = tuple(min(255, c + 25) for c in body)
            _draw_dot(surf, x, y, belly if 11 <= x <= 16 else body)

    # 팔
    _draw_dots(surf, [(7, body_y + 1), (6, body_y + 2), (5, body_y + 3), (5, body_y + 4)], outline)
    _draw_dots(surf, [(20, body_y + 1), (21, body_y + 2), (22, body_y + 3), (22, body_y + 4)], outline)

    # 발
    fy = body_y + len(body_rows)
    _draw_dots(surf, [(10, fy), (9, fy), (9, fy + 1), (8, fy + 1)], outline)
    _draw_dots(surf, [(17, fy), (18, fy), (18, fy + 1), (19, fy + 1)], outline)

    # 눈
    ey = y_off + 5
    _draw_eyes(surf, 9, 18, ey, eye_color, mood)

    # 볼
    _draw_dots(surf, [(7, ey + 3)], cheek)
    _draw_dots(surf, [(20, ey + 3)], cheek)

    # 입
    my = ey + 5
    _draw_mouth(surf, 12, 15, my, eye_color, mood)

    # 타입별 장식
    _draw_type_accessory(surf, evo_type, y_off, cx)

    return surf


def draw_adult(mood="normal", evo_type=None):
    """성인 스프라이트 (32x36 도트) - 가장 화려"""
    surf = _make_surface(32, 36)
    body = _get_baby_body_color(evo_type)
    outline = (110, 90, 70)
    eye_color = (40, 30, 25)
    cheek = (255, 160, 160)

    # 타입별 특별 색상 블렌딩
    if evo_type:
        type_c = TYPE_COLORS.get(evo_type, (255, 230, 200))
        body = tuple((b + t) // 2 for b, t in zip(body, type_c))

    cx = 16
    # 머리
    head_rows = [
        (12, 19),   # 0
        (11, 20),   # 1
        (10, 21),   # 2
        (9, 22),    # 3
        (8, 23),    # 4
        (7, 24),    # 5
        (7, 24),    # 6
        (6, 25),    # 7
        (6, 25),    # 8
        (6, 25),    # 9
        (6, 25),    # 10
        (7, 24),    # 11
        (7, 24),    # 12
        (8, 23),    # 13
    ]

    y_off = 3
    for i, (left, right) in enumerate(head_rows):
        y = y_off + i
        _draw_dot(surf, left, y, outline)
        _draw_dot(surf, right, y, outline)
        for x in range(left + 1, right):
            _draw_dot(surf, x, y, body)
    for x in range(head_rows[0][0], head_rows[0][1] + 1):
        _draw_dot(surf, x, y_off, outline)

    # 귀 (정교)
    for dy in range(5):
        _draw_dot(surf, 7 - dy, y_off - 1 - dy, outline)
        _draw_dot(surf, 24 + dy, y_off - 1 - dy, outline)
        if dy > 0:
            _draw_dot(surf, 7 - dy + 1, y_off - 1 - dy, body)
            _draw_dot(surf, 24 + dy - 1, y_off - 1 - dy, body)

    # 몸통
    body_y = y_off + len(head_rows)
    body_rows = [
        (9, 22),    # 0
        (9, 22),    # 1
        (9, 22),    # 2
        (9, 22),    # 3
        (10, 21),   # 4
        (10, 21),   # 5
        (10, 21),   # 6
        (10, 21),   # 7
        (11, 20),   # 8
        (11, 20),   # 9
        (12, 19),   # 10
    ]
    for i, (left, right) in enumerate(body_rows):
        y = body_y + i
        _draw_dot(surf, left, y, outline)
        _draw_dot(surf, right, y, outline)
        for x in range(left + 1, right):
            belly = tuple(min(255, c + 20) for c in body)
            _draw_dot(surf, x, y, belly if 13 <= x <= 18 else body)

    # 팔
    for dy in range(5):
        _draw_dot(surf, 8 - dy, body_y + 1 + dy, outline)
        _draw_dot(surf, 23 + dy, body_y + 1 + dy, outline)

    # 발
    fy = body_y + len(body_rows)
    _draw_dots(surf, [(11, fy), (10, fy), (10, fy + 1), (9, fy + 1)], outline)
    _draw_dots(surf, [(20, fy), (21, fy), (21, fy + 1), (22, fy + 1)], outline)

    # 눈 (크고 반짝이는)
    ey = y_off + 6
    _draw_eyes_large(surf, 10, 21, ey, eye_color, mood)

    # 볼
    _draw_dots(surf, [(8, ey + 3), (8, ey + 4)], cheek)
    _draw_dots(surf, [(23, ey + 3), (23, ey + 4)], cheek)

    # 입
    my = ey + 6
    _draw_mouth(surf, 14, 17, my, eye_color, mood)

    # 타입별 특별 장식
    _draw_adult_accessory(surf, evo_type, y_off, cx)

    # 왕관/후광 (성인 전용)
    if evo_type == TYPE_BALANCED:
        crown_c = (255, 215, 0)
        for x in range(12, 20):
            _draw_dot(surf, x, y_off - 2, crown_c)
        _draw_dots(surf, [(13, y_off - 3), (16, y_off - 4), (19, y_off - 3)], crown_c)

    return surf


# ─── 공용 헬퍼 ───

def _draw_eyes(surf, left_x, right_x, ey, color, mood):
    """표준 크기 눈 그리기"""
    if mood == "happy" or mood == "excited":
        _draw_dots(surf, [(left_x, ey), (left_x - 1, ey - 1), (left_x + 1, ey - 1)], color)
        _draw_dots(surf, [(right_x, ey), (right_x - 1, ey - 1), (right_x + 1, ey - 1)], color)
    elif mood == "sleeping" or mood == "sleepy":
        _draw_dots(surf, [(left_x - 1, ey), (left_x, ey), (left_x + 1, ey)], color)
        _draw_dots(surf, [(right_x - 1, ey), (right_x, ey), (right_x + 1, ey)], color)
    elif mood == "sad":
        _draw_dots(surf, [(left_x, ey), (left_x, ey - 1)], color)
        _draw_dots(surf, [(right_x, ey), (right_x, ey - 1)], color)
        _draw_dot(surf, left_x, ey + 1, (100, 180, 255))
        _draw_dot(surf, right_x, ey + 1, (100, 180, 255))
    elif mood == "sick":
        _draw_dots(surf, [(left_x - 1, ey - 1), (left_x + 1, ey + 1), (left_x + 1, ey - 1), (left_x - 1, ey + 1)], color)
        _draw_dots(surf, [(right_x - 1, ey - 1), (right_x + 1, ey + 1), (right_x + 1, ey - 1), (right_x - 1, ey + 1)], color)
    else:
        _draw_dots(surf, [(left_x, ey), (left_x, ey - 1)], color)
        _draw_dots(surf, [(right_x, ey), (right_x, ey - 1)], color)
        _draw_dot(surf, left_x, ey - 1, COLOR_WHITE)
        _draw_dot(surf, right_x, ey - 1, COLOR_WHITE)


def _draw_eyes_large(surf, left_x, right_x, ey, color, mood):
    """큰 눈 그리기 (성인용)"""
    if mood == "happy" or mood == "excited":
        _draw_dots(surf, [(left_x, ey), (left_x + 1, ey),
                          (left_x - 1, ey - 1), (left_x + 2, ey - 1)], color)
        _draw_dots(surf, [(right_x, ey), (right_x + 1, ey),
                          (right_x - 1, ey - 1), (right_x + 2, ey - 1)], color)
    elif mood == "sleeping" or mood == "sleepy":
        for dx in range(-1, 3):
            _draw_dot(surf, left_x + dx, ey, color)
            _draw_dot(surf, right_x + dx, ey, color)
    elif mood == "sick":
        for d in [(-1, -1), (2, 2), (2, -1), (-1, 2)]:
            _draw_dot(surf, left_x + d[0], ey + d[1] - 1, color)
            _draw_dot(surf, right_x + d[0], ey + d[1] - 1, color)
    else:
        # 큰 동그란 눈 + 별 반짝임
        for dy in range(-1, 2):
            for dx in range(0, 2):
                _draw_dot(surf, left_x + dx, ey + dy, color)
                _draw_dot(surf, right_x + dx, ey + dy, color)
        # 하이라이트
        _draw_dot(surf, left_x, ey - 1, COLOR_WHITE)
        _draw_dot(surf, right_x, ey - 1, COLOR_WHITE)
        _draw_dot(surf, left_x + 1, ey, (220, 220, 230))
        _draw_dot(surf, right_x + 1, ey, (220, 220, 230))


def _draw_mouth(surf, left_x, right_x, my, color, mood):
    """입 그리기"""
    if mood == "happy" or mood == "excited":
        for x in range(left_x, right_x + 1):
            _draw_dot(surf, x, my, color)
        _draw_dot(surf, left_x - 1, my - 1, color)
        _draw_dot(surf, right_x + 1, my - 1, color)
    elif mood == "sad" or mood == "sick":
        for x in range(left_x, right_x + 1):
            _draw_dot(surf, x, my - 1, color)
        _draw_dot(surf, left_x - 1, my, color)
        _draw_dot(surf, right_x + 1, my, color)
    elif mood == "eating":
        for x in range(left_x, right_x + 1):
            _draw_dot(surf, x, my, color)
            _draw_dot(surf, x, my - 1, color)
    else:
        for x in range(left_x, right_x + 1):
            _draw_dot(surf, x, my, color)


def _draw_type_accessory(surf, evo_type, y_off, cx):
    """타입별 장식 (청소년)"""
    if evo_type == TYPE_SMART:
        gc = (100, 100, 140)
        _draw_dots(surf, [(7, y_off + 4), (8, y_off + 3), (9, y_off + 3), (10, y_off + 3), (11, y_off + 4)], gc)
        _draw_dots(surf, [(16, y_off + 4), (17, y_off + 3), (18, y_off + 3), (19, y_off + 3), (20, y_off + 4)], gc)
        _draw_dots(surf, [(11, y_off + 3), (12, y_off + 3), (13, y_off + 3), (14, y_off + 3), (15, y_off + 3), (16, y_off + 3)], gc)
    elif evo_type == TYPE_HAPPY:
        sc = (255, 200, 100)
        _draw_dots(surf, [(cx, y_off - 3), (cx - 1, y_off - 2), (cx + 1, y_off - 2),
                          (cx - 2, y_off - 3), (cx + 2, y_off - 3)], sc)
    elif evo_type == TYPE_FOODIE:
        # 요리사 모자
        hat_c = (255, 255, 255)
        for x in range(cx - 4, cx + 4):
            _draw_dot(surf, x, y_off - 1, hat_c)
            _draw_dot(surf, x, y_off - 2, hat_c)
        for x in range(cx - 2, cx + 2):
            _draw_dot(surf, x, y_off - 3, hat_c)


def _draw_adult_accessory(surf, evo_type, y_off, cx):
    """타입별 장식 (성인)"""
    if evo_type == TYPE_SMART:
        # 박사모
        hat_c = (60, 60, 80)
        for x in range(cx - 5, cx + 5):
            _draw_dot(surf, x, y_off - 1, hat_c)
        for x in range(cx - 3, cx + 3):
            _draw_dot(surf, x, y_off - 2, hat_c)
            _draw_dot(surf, x, y_off - 3, hat_c)
        # 술
        tassel = (255, 215, 0)
        _draw_dots(surf, [(cx + 4, y_off - 1), (cx + 5, y_off), (cx + 6, y_off + 1)], tassel)
    elif evo_type == TYPE_HAPPY:
        # 별 이펙트
        star_c = (255, 220, 100)
        offsets = [(-6, -2), (6, -3), (-5, 5), (7, 4), (0, -5)]
        for ox, oy in offsets:
            _draw_dot(surf, cx + ox, y_off + oy, star_c)
    elif evo_type == TYPE_FOODIE:
        # 셰프 모자 (큰)
        hat_c = (255, 255, 255)
        for x in range(cx - 5, cx + 5):
            for dy in range(-1, -5, -1):
                _draw_dot(surf, x, y_off + dy, hat_c)


# ═══════════════════════════════════════════════
# 스프라이트 캐시 & 스케일링
# ═══════════════════════════════════════════════

_sprite_cache = {}


def get_sprite(stage, mood="normal", evo_type=None, scale=3):
    """
    캐시된 스프라이트 반환 (스케일 적용)
    scale: 정수 배율 (1=원본, 2=2배, 3=3배)
    """
    cache_key = (stage, mood, evo_type, scale)
    if cache_key in _sprite_cache:
        return _sprite_cache[cache_key]

    # 원본 생성
    draw_funcs = {
        STAGE_EGG: lambda: draw_egg(mood),
        STAGE_BABY: lambda: draw_baby(mood, evo_type),
        STAGE_CHILD: lambda: draw_child(mood, evo_type),
        STAGE_TEEN: lambda: draw_teen(mood, evo_type),
        STAGE_ADULT: lambda: draw_adult(mood, evo_type),
    }

    func = draw_funcs.get(stage, draw_funcs[STAGE_BABY])
    original = func()

    if scale != 1:
        w, h = original.get_size()
        sprite = pygame.transform.scale(original, (w * scale, h * scale))
    else:
        sprite = original

    _sprite_cache[cache_key] = sprite
    return sprite


def clear_sprite_cache():
    """스프라이트 캐시 초기화"""
    _sprite_cache.clear()


def get_sprite_for_pet(pet, scale=3):
    """Pet 객체에서 직접 스프라이트 가져오기"""
    return get_sprite(pet.stage, pet.mood, pet.evolution_type, scale)
