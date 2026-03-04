"""
UI 기본 요소 - 버튼, 상태바, 텍스트 입력 등
파스텔톤 픽셀아트 스타일
"""
import pygame
import time
from data.constants import (
    COLOR_BTN, COLOR_BTN_HOVER, COLOR_BTN_PRESS, COLOR_BTN_DISABLED,
    COLOR_TEXT, COLOR_WHITE, COLOR_BLACK, COLOR_ACCENT,
    COLOR_GRAY, COLOR_LIGHT_GRAY, COLOR_BG,
    STAT_BAR_WIDTH, STAT_BAR_HEIGHT,
    FONT_SIZE_SMALL, FONT_SIZE_MEDIUM, FONT_SIZE_LARGE, FONT_SIZE_TITLE,
    SCREEN_WIDTH, SCREEN_HEIGHT,
)


# ─── 폰트 매니저 ───

_fonts = {}


def get_font(size=FONT_SIZE_MEDIUM):
    """폰트 가져오기 (캐시)"""
    if size not in _fonts:
        # Windows 한글 지원 폰트 사용
        try:
            _fonts[size] = pygame.font.SysFont("malgungothic", size)
        except Exception:
            try:
                _fonts[size] = pygame.font.SysFont("gulim", size)
            except Exception:
                _fonts[size] = pygame.font.Font(None, size)
    return _fonts[size]


# ─── 픽셀아트 스타일 사각형 그리기 ───

def draw_rounded_rect(surface, rect, color, radius=8, border_color=None, border_width=2):
    """둥근 모서리 사각형"""
    r = pygame.Rect(rect)
    pygame.draw.rect(surface, color, r, border_radius=radius)
    if border_color:
        pygame.draw.rect(surface, border_color, r, width=border_width, border_radius=radius)


# ─── 버튼 클래스 ───

class Button:
    """파스텔 스타일 버튼"""

    def __init__(self, x, y, width, height, text, color=None, icon=None,
                 font_size=FONT_SIZE_MEDIUM, enabled=True):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color or COLOR_BTN
        self.icon = icon
        self.font_size = font_size
        self.enabled = enabled

        self.hovered = False
        self.pressed = False
        self.click_callback = None

        # 색상 계산
        self.hover_color = tuple(max(0, c - 25) for c in self.color)
        self.press_color = tuple(max(0, c - 50) for c in self.color)
        self.border_color = tuple(max(0, c - 60) for c in self.color)

    def set_callback(self, callback):
        self.click_callback = callback
        return self

    def handle_event(self, event):
        """이벤트 처리. 클릭 시 True 반환"""
        if not self.enabled:
            return False

        if event.type == pygame.MOUSEMOTION:
            self.hovered = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                self.pressed = True
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if self.pressed and self.rect.collidepoint(event.pos):
                self.pressed = False
                if self.click_callback:
                    self.click_callback()
                return True
            self.pressed = False
        return False

    def draw(self, surface):
        """렌더링"""
        if not self.enabled:
            color = COLOR_BTN_DISABLED
            border = COLOR_GRAY
        elif self.pressed:
            color = self.press_color
            border = self.border_color
        elif self.hovered:
            color = self.hover_color
            border = self.border_color
        else:
            color = self.color
            border = self.border_color

        # 그림자
        shadow_rect = self.rect.copy()
        shadow_rect.y += 3
        shadow_surf = pygame.Surface((shadow_rect.width, shadow_rect.height), pygame.SRCALPHA)
        pygame.draw.rect(shadow_surf, (150, 150, 150, 60), shadow_surf.get_rect(),
                         border_radius=10)
        surface.blit(shadow_surf, shadow_rect.topleft)

        # 본체
        offset = 2 if self.pressed else 0
        btn_rect = self.rect.copy()
        btn_rect.y += offset
        draw_rounded_rect(surface, btn_rect, color, radius=10, border_color=border)

        # 텍스트
        font = get_font(self.font_size)
        text_surf = font.render(self.text, True, COLOR_TEXT)
        text_rect = text_surf.get_rect(center=btn_rect.center)
        surface.blit(text_surf, text_rect)

        # 아이콘
        if self.icon:
            icon_rect = self.icon.get_rect(midright=(text_rect.left - 4, btn_rect.centery))
            surface.blit(self.icon, icon_rect)


# ─── 상태바 ───

class StatBar:
    """스탯 게이지 바"""

    def __init__(self, x, y, width, height, label, color, max_val=100):
        self.rect = pygame.Rect(x, y, width, height)
        self.label = label
        self.color = color
        self.max_val = max_val
        self.current_val = max_val
        self.display_val = max_val  # 부드러운 애니메이션용

    def set_value(self, value):
        self.current_val = max(0, min(self.max_val, value))

    def update(self, dt):
        """부드러운 바 이동"""
        diff = self.current_val - self.display_val
        self.display_val += diff * min(1.0, dt * 5)

    def draw(self, surface):
        # 라벨
        font = get_font(FONT_SIZE_SMALL)
        label_surf = font.render(self.label, True, COLOR_TEXT)
        surface.blit(label_surf, (self.rect.x, self.rect.y - 16))

        # 배경 바
        draw_rounded_rect(surface, self.rect, COLOR_LIGHT_GRAY, radius=4)

        # 채워진 바
        ratio = self.display_val / self.max_val
        fill_width = max(0, int(self.rect.width * ratio))
        if fill_width > 0:
            fill_rect = pygame.Rect(self.rect.x, self.rect.y, fill_width, self.rect.height)
            # 색상이 낮으면 빨간색으로
            if ratio < 0.2:
                bar_color = (255, 80, 80)
            elif ratio < 0.4:
                bar_color = (255, 180, 80)
            else:
                bar_color = self.color
            draw_rounded_rect(surface, fill_rect, bar_color, radius=4)

        # 수치 표시
        val_text = f"{int(self.display_val)}"
        val_surf = font.render(val_text, True, COLOR_TEXT)
        val_rect = val_surf.get_rect(midright=(self.rect.right, self.rect.y - 8))
        surface.blit(val_surf, val_rect)


# ─── 텍스트 입력 필드 ───

class TextInput:
    """한글/영어 텍스트 입력 필드"""

    def __init__(self, x, y, width, height, placeholder="이름을 입력하세요",
                 max_length=12, font_size=FONT_SIZE_LARGE):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = ""
        self.placeholder = placeholder
        self.max_length = max_length
        self.font_size = font_size
        self.active = False
        self.cursor_visible = True
        self.cursor_timer = 0
        self.confirmed = False
        # 한국어 IME 조합 지원
        self.composition = ""          # IME 조합 중인 문자열
        self._last_textinput_text = "" # 중복 TEXTINPUT 방지
        self._last_textinput_time = 0.0

    def handle_event(self, event):
        """이벤트 처리. 확정 시 True 반환"""
        if event.type == pygame.MOUSEBUTTONDOWN:
            prev_active = self.active
            self.active = self.rect.collidepoint(event.pos)
            if not self.active and prev_active:
                self.composition = ""
            return False

        if not self.active:
            return False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                if self.text.strip():
                    self.composition = ""
                    self.confirmed = True
                    return True
            elif event.key == pygame.K_BACKSPACE:
                if self.composition:
                    # 조합 중이면 조합 취소
                    self.composition = ""
                else:
                    self.text = self.text[:-1]
            elif event.key == pygame.K_ESCAPE:
                self.composition = ""
                self.active = False
            return False

        # IME 조합 중인 문자열 처리 (TEXTEDITING)
        if event.type == pygame.TEXTEDITING:
            self.composition = event.text
            return False

        if event.type == pygame.TEXTINPUT:
            self.composition = ""
            now = time.time()
            # Windows 한국어 IME 중복 TEXTINPUT 버그 방지
            if (event.text == self._last_textinput_text
                    and now - self._last_textinput_time < 0.05):
                return False
            self._last_textinput_text = event.text
            self._last_textinput_time = now
            if len(self.text) < self.max_length:
                self.text += event.text
            return False

        return False

    def update(self, dt):
        """커서 깜빡임"""
        self.cursor_timer += dt
        if self.cursor_timer >= 0.5:
            self.cursor_timer = 0
            self.cursor_visible = not self.cursor_visible

    def draw(self, surface):
        # 배경
        bg_color = COLOR_WHITE if self.active else (245, 240, 235)
        border = COLOR_ACCENT if self.active else COLOR_GRAY
        draw_rounded_rect(surface, self.rect, bg_color, radius=8, border_color=border, border_width=3)

        font = get_font(self.font_size)
        display_text = self.text + self.composition  # 조합 중인 문자 포함
        if display_text:
            if self.composition:
                # 조합 중인 부분은 밑줄로 구분
                base_surf = font.render(self.text, True, COLOR_TEXT)
                comp_surf = font.render(self.composition, True, COLOR_ACCENT)
                total_w = base_surf.get_width() + comp_surf.get_width()
                total_h = max(base_surf.get_height(), comp_surf.get_height())
                text_surf = pygame.Surface((max(total_w, 1), total_h), pygame.SRCALPHA)
                text_surf.blit(base_surf, (0, 0))
                text_surf.blit(comp_surf, (base_surf.get_width(), 0))
                # 조합 중인 글자 아래 밑줄
                underline_y = total_h - 2
                pygame.draw.line(text_surf, COLOR_ACCENT,
                                 (base_surf.get_width(), underline_y),
                                 (total_w, underline_y), 2)
            else:
                text_surf = font.render(self.text, True, COLOR_TEXT)
        else:
            text_surf = font.render(self.placeholder, True, COLOR_GRAY)

        # 텍스트 위치 (세로 중앙)
        text_rect = text_surf.get_rect(midleft=(self.rect.x + 12, self.rect.centery))
        surface.blit(text_surf, text_rect)

        # 커서
        if self.active and self.cursor_visible and not self.composition:
            cursor_x = text_rect.right + 2 if display_text else self.rect.x + 12
            pygame.draw.line(surface, COLOR_TEXT,
                             (cursor_x, self.rect.y + 8),
                             (cursor_x, self.rect.bottom - 8), 2)

    def get_text(self):
        return self.text.strip()


# ─── 알림 메시지 (토스트) ───

class Toast:
    """화면 상단에 나타나는 알림"""

    def __init__(self, message, duration=3.0, color=None):
        self.message = message
        self.duration = duration
        self.timer = 0
        self.color = color or COLOR_ACCENT
        self.alpha = 255

    def update(self, dt):
        self.timer += dt
        # 페이드아웃
        if self.timer > self.duration - 0.5:
            self.alpha = max(0, int(255 * (self.duration - self.timer) / 0.5))
        return self.timer < self.duration

    def draw(self, surface, y=50):
        if self.alpha <= 0:
            return
        font = get_font(FONT_SIZE_MEDIUM)
        text_surf = font.render(self.message, True, COLOR_WHITE)
        tw = text_surf.get_width() + 30
        th = text_surf.get_height() + 16

        # 배경
        toast_surf = pygame.Surface((tw, th), pygame.SRCALPHA)
        bg_color = (*self.color, min(200, self.alpha))
        draw_rounded_rect(toast_surf, (0, 0, tw, th), bg_color, radius=12)
        text_surf.set_alpha(self.alpha)
        toast_surf.blit(text_surf, (15, 8))

        x = (surface.get_width() - tw) // 2
        surface.blit(toast_surf, (x, y))


# ─── 파티클 이펙트 ───

class Particle:
    """간단한 파티클 (하트, 별 등)"""

    def __init__(self, x, y, char="♥", color=None, life=1.5):
        self.x = x
        self.y = y
        self.char = char
        self.color = color or COLOR_HEART
        self.life = life
        self.timer = 0
        self.vy = -30  # 위로 올라감
        self.vx = (pygame.time.get_ticks() % 20 - 10) * 2

    def update(self, dt):
        self.timer += dt
        self.y += self.vy * dt
        self.x += self.vx * dt
        self.vy += 10 * dt  # 약간의 중력
        return self.timer < self.life

    def draw(self, surface):
        alpha = max(0, int(255 * (1 - self.timer / self.life)))
        font = get_font(FONT_SIZE_MEDIUM)
        text_surf = font.render(self.char, True, self.color)
        text_surf.set_alpha(alpha)
        surface.blit(text_surf, (int(self.x), int(self.y)))


# ─── 대화 상자 (다이얼로그) ───

class Dialog:
    """모달 대화 상자"""

    def __init__(self, title, message, buttons=None):
        self.title = title
        self.message = message
        self.buttons_text = buttons or ["확인"]
        self.result = None
        self.active = True

        # 위치 계산 (화면 중앙 동적 배치)
        self.width = min(400, SCREEN_WIDTH - 80)
        self.height = 200
        self.x = (SCREEN_WIDTH - self.width) // 2
        self.y = (SCREEN_HEIGHT - self.height) // 2

        self.buttons = []
        btn_width = 100
        total_btn = len(self.buttons_text) * (btn_width + 20) - 20
        start_x = self.x + (self.width - total_btn) // 2
        for i, text in enumerate(self.buttons_text):
            color = COLOR_ACCENT if i == 0 else COLOR_GRAY
            btn = Button(start_x + i * (btn_width + 20),
                         self.y + self.height - 60,
                         btn_width, 40, text, color=color)
            btn.set_callback(lambda idx=i: self._on_button(idx))
            self.buttons.append(btn)

    def _on_button(self, index):
        self.result = index
        self.active = False

    def handle_event(self, event):
        for btn in self.buttons:
            btn.handle_event(event)

    def draw(self, surface):
        if not self.active:
            return

        # 어두운 오버레이
        overlay = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 100))
        surface.blit(overlay, (0, 0))

        # 다이얼로그 배경
        rect = (self.x, self.y, self.width, self.height)
        draw_rounded_rect(surface, rect, COLOR_BG, radius=16,
                          border_color=COLOR_ACCENT, border_width=3)

        # 제목
        font_title = get_font(FONT_SIZE_LARGE)
        title_surf = font_title.render(self.title, True, COLOR_ACCENT)
        surface.blit(title_surf, (self.x + 20, self.y + 15))

        # 메시지
        font = get_font(FONT_SIZE_MEDIUM)
        # 여러 줄 지원
        lines = self.message.split('\n')
        for i, line in enumerate(lines):
            text_surf = font.render(line, True, COLOR_TEXT)
            surface.blit(text_surf, (self.x + 20, self.y + 55 + i * 28))

        # 버튼
        for btn in self.buttons:
            btn.draw(surface)


# ─── 진행 바 (경험치용) ───

class ExpBar:
    """경험치 진행 바"""

    def __init__(self, x, y, width, height):
        self.rect = pygame.Rect(x, y, width, height)
        self.progress = 0.0  # 0.0 ~ 1.0
        self.display_progress = 0.0

    def set_progress(self, value):
        self.progress = max(0.0, min(1.0, value))

    def update(self, dt):
        diff = self.progress - self.display_progress
        self.display_progress += diff * min(1.0, dt * 3)

    def draw(self, surface, level=0):
        from data.constants import COLOR_EXP

        # 배경
        draw_rounded_rect(surface, self.rect, COLOR_LIGHT_GRAY, radius=6)

        # 채우기
        fill_w = int(self.rect.width * self.display_progress)
        if fill_w > 0:
            fill_rect = pygame.Rect(self.rect.x, self.rect.y, fill_w, self.rect.height)
            draw_rounded_rect(surface, fill_rect, COLOR_EXP, radius=6)

        # 레벨 텍스트
        font = get_font(FONT_SIZE_SMALL)
        lv_text = f"Lv.{level}"
        lv_surf = font.render(lv_text, True, COLOR_TEXT)
        surface.blit(lv_surf, (self.rect.x, self.rect.y - 16))

        # 퍼센트
        pct = f"{int(self.display_progress * 100)}%"
        pct_surf = font.render(pct, True, COLOR_TEXT)
        pct_rect = pct_surf.get_rect(midright=(self.rect.right, self.rect.y - 8))
        surface.blit(pct_surf, pct_rect)
