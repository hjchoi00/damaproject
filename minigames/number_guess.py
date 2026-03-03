"""
미니게임: 숫자 맞추기
1~100 사이 숫자를 맞추기. 힌트: 높다/낮다
"""
import pygame
import random
from minigames.base import MinigameScene
from gui.ui_elements import get_font, Button, TextInput, draw_rounded_rect
from data.constants import (
    SCREEN_WIDTH, SCREEN_HEIGHT, COLOR_TEXT, COLOR_ACCENT, COLOR_ACCENT2,
    COLOR_ACCENT3, COLOR_GRAY, COLOR_LIGHT_GRAY, COLOR_BG,
    FONT_SIZE_SMALL, FONT_SIZE_MEDIUM, FONT_SIZE_LARGE, FONT_SIZE_TITLE,
)


class NumberGuessGame(MinigameScene):
    """숫자 맞추기 미니게임"""

    def __init__(self):
        super().__init__(title="🔢 숫자 맞추기")
        self.target = 0
        self.attempts = 0
        self.max_attempts = 7
        self.hint = ""
        self.history = []  # [(guessed_number, "높아요"/"낮아요")]
        self.current_input = ""

        cx = SCREEN_WIDTH // 2
        self.input_field = TextInput(cx - 80, 350, 160, 45,
                                     placeholder="숫자 입력", max_length=3,
                                     font_size=FONT_SIZE_LARGE)

        self.btn_guess = Button(cx - 60, 410, 120, 45, "확인!",
                                color=COLOR_ACCENT, font_size=FONT_SIZE_LARGE)
        self.btn_guess.set_callback(self._on_guess)

        # 숫자 퀵 버튼
        self.quick_buttons = []

    def _init_game(self):
        self.target = random.randint(1, 100)
        self.attempts = 0
        self.hint = "1~100 사이의 숫자를 맞춰보세요!"
        self.history = []
        self.input_field.text = ""
        self.input_field.active = True
        self.input_field.confirmed = False
        self.state = "playing"
        pygame.key.start_text_input()

    def _on_guess(self):
        text = self.input_field.get_text()
        if not text.isdigit():
            self.hint = "숫자를 입력해주세요!"
            return

        guess = int(text)
        if guess < 1 or guess > 100:
            self.hint = "1~100 사이의 숫자를 입력해주세요!"
            return

        self.attempts += 1

        if guess == self.target:
            # 정답!
            self.hint = f"🎉 정답! {self.attempts}번 만에 맞췄어요!"
            score = max(50, 200 - (self.attempts - 1) * 25)
            self.finish_game("win", score=score)
        elif guess < self.target:
            self.hint = f"⬆️ {guess}보다 높아요!"
            self.history.append((guess, "⬆️ 높아요"))
        else:
            self.hint = f"⬇️ {guess}보다 낮아요!"
            self.history.append((guess, "⬇️ 낮아요"))

        # 시도 횟수 초과
        if self.attempts >= self.max_attempts and self.state != "result":
            self.hint = f"😅 실패! 정답은 {self.target}이었어요"
            self.finish_game("lose", score=self.attempts * 10)

        self.input_field.text = ""

    def _handle_game_event(self, event):
        if self.input_field.handle_event(event):
            self._on_guess()
        self.btn_guess.handle_event(event)

    def _update_game(self, dt):
        self.input_field.update(dt)

    def _draw_game(self, surface):
        font = get_font(FONT_SIZE_MEDIUM)
        font_big = get_font(FONT_SIZE_TITLE)
        font_small = get_font(FONT_SIZE_SMALL)

        # 시도 횟수
        attempt_text = f"시도: {self.attempts} / {self.max_attempts}"
        attempt_surf = font.render(attempt_text, True, COLOR_TEXT)
        surface.blit(attempt_surf, (SCREEN_WIDTH // 2 - attempt_surf.get_width() // 2, 55))

        # 큰 물음표
        q_surf = font_big.render("?", True, COLOR_ACCENT)
        surface.blit(q_surf, (SCREEN_WIDTH // 2 - q_surf.get_width() // 2, 90))

        # 범위 표시
        low = 1
        high = 100
        for guess, hint in self.history:
            if "높아요" in hint:
                low = max(low, guess + 1)
            elif "낮아요" in hint:
                high = min(high, guess - 1)

        range_text = f"범위: {low} ~ {high}"
        range_surf = font.render(range_text, True, COLOR_ACCENT2)
        surface.blit(range_surf, (SCREEN_WIDTH // 2 - range_surf.get_width() // 2, 150))

        # 범위 바
        bar_x = 40
        bar_w = SCREEN_WIDTH - 80
        bar_y = 190
        bar_h = 20

        draw_rounded_rect(surface, (bar_x, bar_y, bar_w, bar_h),
                          COLOR_LIGHT_GRAY, radius=6)

        # 가능 범위 표시
        low_x = bar_x + int((low - 1) / 99 * bar_w)
        high_x = bar_x + int((high - 1) / 99 * bar_w)
        if high_x > low_x:
            draw_rounded_rect(surface, (low_x, bar_y, high_x - low_x, bar_h),
                              COLOR_ACCENT2, radius=6)

        # 히스토리 마커
        for guess, hint in self.history:
            gx = bar_x + int((guess - 1) / 99 * bar_w)
            marker_color = (255, 100, 100) if "낮아요" in hint else (100, 100, 255)
            pygame.draw.circle(surface, marker_color, (gx, bar_y + bar_h // 2), 5)

        # 힌트 메시지
        hint_surf = font.render(self.hint, True, COLOR_ACCENT)
        surface.blit(hint_surf, (SCREEN_WIDTH // 2 - hint_surf.get_width() // 2, 240))

        # 히스토리 목록
        if self.history:
            hist_panel = (20, 275, SCREEN_WIDTH - 40, min(60, len(self.history) * 22 + 10))
            draw_rounded_rect(surface, hist_panel, (255, 250, 245), radius=8)

            for i, (guess, hint) in enumerate(self.history[-3:]):
                text = f"  {guess} → {hint}"
                hist_surf = font_small.render(text, True, COLOR_GRAY)
                surface.blit(hist_surf, (30, 280 + i * 22))

        # 입력 필드 & 버튼
        self.input_field.draw(surface)
        self.btn_guess.draw(surface)

        # 키보드 안내
        hint2 = font_small.render("숫자 입력 후 Enter 또는 확인 클릭", True, COLOR_GRAY)
        surface.blit(hint2, (SCREEN_WIDTH // 2 - hint2.get_width() // 2, 470))
