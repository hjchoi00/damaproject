"""
간단한 애니메이션 시퀀스
펫의 흔들림, 점프, 이펙트 등
"""
import math
import pygame


class BounceAnimation:
    """펫이 통통 뛰는 기본 아이들 애니메이션"""

    def __init__(self, amplitude=5, speed=2.0):
        self.amplitude = amplitude
        self.speed = speed
        self.timer = 0
        self.offset_y = 0

    def update(self, dt):
        self.timer += dt * self.speed
        self.offset_y = math.sin(self.timer * math.pi) * self.amplitude

    def get_offset(self):
        return (0, -abs(self.offset_y))


class ShakeAnimation:
    """흔들림 (아플 때, 배고플 때)"""

    def __init__(self, intensity=3, speed=8.0, duration=0):
        self.intensity = intensity
        self.speed = speed
        self.duration = duration  # 0 = 무한
        self.timer = 0
        self.offset_x = 0

    def update(self, dt):
        self.timer += dt
        if self.duration > 0 and self.timer > self.duration:
            self.offset_x = 0
            return False
        self.offset_x = math.sin(self.timer * self.speed * math.pi * 2) * self.intensity
        return True

    def get_offset(self):
        return (self.offset_x, 0)


class PulseAnimation:
    """크기 맥동 (진화 이펙트)"""

    def __init__(self, scale_range=(0.9, 1.1), speed=3.0, duration=2.0):
        self.min_scale = scale_range[0]
        self.max_scale = scale_range[1]
        self.speed = speed
        self.duration = duration
        self.timer = 0
        self.scale = 1.0

    def update(self, dt):
        self.timer += dt
        if self.timer > self.duration:
            self.scale = 1.0
            return False
        t = math.sin(self.timer * self.speed * math.pi * 2) * 0.5 + 0.5
        self.scale = self.min_scale + t * (self.max_scale - self.min_scale)
        return True

    def apply(self, surface):
        """스케일된 서피스 반환"""
        w, h = surface.get_size()
        new_w = int(w * self.scale)
        new_h = int(h * self.scale)
        return pygame.transform.scale(surface, (new_w, new_h))


class FadeAnimation:
    """페이드 인/아웃"""

    def __init__(self, fade_in=True, duration=1.0):
        self.fade_in = fade_in
        self.duration = duration
        self.timer = 0
        self.alpha = 0 if fade_in else 255

    def update(self, dt):
        self.timer += dt
        progress = min(1.0, self.timer / self.duration)
        if self.fade_in:
            self.alpha = int(255 * progress)
        else:
            self.alpha = int(255 * (1 - progress))
        return self.timer < self.duration

    def apply(self, surface):
        surface.set_alpha(self.alpha)
        return surface


class FloatingText:
    """떠오르는 텍스트 (경험치 획득 등)"""

    def __init__(self, text, x, y, color=(255, 200, 100), duration=1.5):
        self.text = text
        self.x = x
        self.y = y
        self.color = color
        self.duration = duration
        self.timer = 0
        self._font = None

    def update(self, dt):
        self.timer += dt
        self.y -= 30 * dt
        return self.timer < self.duration

    def draw(self, surface):
        from gui.ui_elements import get_font, FONT_SIZE_MEDIUM
        if self._font is None:
            self._font = get_font(FONT_SIZE_MEDIUM)
        alpha = max(0, int(255 * (1 - self.timer / self.duration)))
        text_surf = self._font.render(self.text, True, self.color)
        text_surf.set_alpha(alpha)
        surface.blit(text_surf, (int(self.x), int(self.y)))


class ZZZAnimation:
    """잠자는 Z 이펙트"""

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.timer = 0
        self.z_list = []  # [(x, y, alpha, size)]

    def update(self, dt):
        self.timer += dt

        # 1초마다 새 Z 생성
        if int(self.timer * 2) > len(self.z_list):
            self.z_list.append({
                "x": self.x + len(self.z_list) * 8,
                "y": self.y,
                "alpha": 255,
                "size": 14 + len(self.z_list) * 4,
            })

        # 올라가면서 사라짐
        for z in self.z_list:
            z["y"] -= 15 * dt
            z["alpha"] = max(0, z["alpha"] - 80 * dt)

        self.z_list = [z for z in self.z_list if z["alpha"] > 0]
        return True

    def draw(self, surface):
        from gui.ui_elements import get_font
        for z in self.z_list:
            font = get_font(int(z["size"]))
            text_surf = font.render("Z", True, (150, 150, 200))
            text_surf.set_alpha(int(z["alpha"]))
            surface.blit(text_surf, (int(z["x"]), int(z["y"])))
