"""
미니게임: 가위바위보
3판 2선승제
"""
import pygame
import random
from minigames.base import MinigameScene
from gui.ui_elements import get_font, Button, draw_rounded_rect
from data.constants import (
    SCREEN_WIDTH, SCREEN_HEIGHT, COLOR_BG, COLOR_TEXT, COLOR_ACCENT,
    COLOR_ACCENT2, COLOR_ACCENT3, COLOR_GRAY, COLOR_LIGHT_GRAY,
    FONT_SIZE_SMALL, FONT_SIZE_MEDIUM, FONT_SIZE_LARGE, FONT_SIZE_TITLE,
)


CHOICES = ["✊ 바위", "✌️ 가위", "✋ 보"]
CHOICE_NAMES = ["바위", "가위", "보"]


class RPSGame(MinigameScene):
    """가위바위보 미니게임"""

    def __init__(self):
        super().__init__(title="✊✌️✋ 가위바위보")
        self.player_wins = 0
        self.pet_wins = 0
        self.round = 0
        self.max_rounds = 3  # 3판 2선승
        self.player_choice = None
        self.pet_choice = None
        self.round_result = None  # "win", "lose", "draw"
        self.show_result_timer = 0
        self.round_history = []

        # 선택 버튼
        cx = SCREEN_WIDTH // 2
        self.choice_buttons = []
        for i, name in enumerate(CHOICES):
            btn = Button(cx - 180 + i * 130, 400, 110, 60, name,
                         color=[(255, 200, 180), (200, 220, 255), (200, 255, 200)][i],
                         font_size=FONT_SIZE_MEDIUM)
            btn.set_callback(lambda idx=i: self._on_choose(idx))
            self.choice_buttons.append(btn)

    def _init_game(self):
        self.player_wins = 0
        self.pet_wins = 0
        self.round = 0
        self.player_choice = None
        self.pet_choice = None
        self.round_result = None
        self.show_result_timer = 0
        self.round_history = []
        self.state = "playing"

    def _on_choose(self, choice_idx):
        if self.round_result is not None:
            return  # 결과 표시 중

        self.player_choice = choice_idx
        self.pet_choice = random.randint(0, 2)
        self.round += 1

        # 승패 판정 (0=바위, 1=가위, 2=보)
        if self.player_choice == self.pet_choice:
            self.round_result = "draw"
        elif (self.player_choice - self.pet_choice) % 3 == 2:
            # 바위→가위 승, 가위→보 승, 보→바위 승
            self.round_result = "win"
            self.player_wins += 1
        else:
            self.round_result = "lose"
            self.pet_wins += 1

        self.round_history.append({
            "player": CHOICE_NAMES[self.player_choice],
            "pet": CHOICE_NAMES[self.pet_choice],
            "result": self.round_result,
        })

        self.show_result_timer = 2.0  # 2초간 결과 표시

    def _handle_game_event(self, event):
        if self.round_result is None:  # 선택 대기 중
            for btn in self.choice_buttons:
                btn.handle_event(event)

        # 키보드 단축키
        if event.type == pygame.KEYDOWN and self.round_result is None:
            if event.key == pygame.K_1 or event.key == pygame.K_LEFT:
                self._on_choose(0)
            elif event.key == pygame.K_2 or event.key == pygame.K_UP:
                self._on_choose(1)
            elif event.key == pygame.K_3 or event.key == pygame.K_RIGHT:
                self._on_choose(2)

    def _update_game(self, dt):
        if self.show_result_timer > 0:
            self.show_result_timer -= dt
            if self.show_result_timer <= 0:
                # 결과 리셋
                self.round_result = None
                self.player_choice = None
                self.pet_choice = None

                # 게임 종료 체크
                if self.player_wins >= 2:
                    self.finish_game("win", score=self.player_wins * 100)
                elif self.pet_wins >= 2:
                    self.finish_game("lose", score=self.player_wins * 50)
                elif self.round >= self.max_rounds:
                    if self.player_wins > self.pet_wins:
                        self.finish_game("win", score=self.player_wins * 100)
                    elif self.player_wins < self.pet_wins:
                        self.finish_game("lose", score=self.player_wins * 50)
                    else:
                        self.finish_game("draw", score=75)

    def _draw_game(self, surface):
        font = get_font(FONT_SIZE_MEDIUM)
        font_big = get_font(FONT_SIZE_TITLE)

        # 스코어보드
        score_bg = (20, 60, SCREEN_WIDTH - 40, 50)
        draw_rounded_rect(surface, score_bg, (255, 248, 240), radius=10,
                          border_color=COLOR_LIGHT_GRAY)

        score_text = f"나 {self.player_wins} : {self.pet_wins} {self.pet.name if self.pet else '상대'}"
        score_surf = font.render(score_text, True, COLOR_TEXT)
        surface.blit(score_surf, (SCREEN_WIDTH // 2 - score_surf.get_width() // 2, 72))

        round_text = f"Round {min(self.round + 1, self.max_rounds)} / {self.max_rounds}"
        round_surf = get_font(FONT_SIZE_SMALL).render(round_text, True, COLOR_GRAY)
        surface.blit(round_surf, (SCREEN_WIDTH // 2 - round_surf.get_width() // 2, 52))

        if self.round_result is not None:
            # 선택 결과 표시
            # 플레이어
            p_text = CHOICES[self.player_choice]
            p_surf = font_big.render(p_text, True, COLOR_ACCENT)
            surface.blit(p_surf, (80, 180))

            vs_surf = font.render("VS", True, COLOR_GRAY)
            surface.blit(vs_surf, (SCREEN_WIDTH // 2 - vs_surf.get_width() // 2, 210))

            # 펫
            pet_text = CHOICES[self.pet_choice]
            pet_surf = font_big.render(pet_text, True, COLOR_ACCENT2)
            surface.blit(pet_surf, (SCREEN_WIDTH - 180, 180))

            # 라운드 결과
            if self.round_result == "win":
                result_text = "이겼다! ✨"
                result_color = COLOR_ACCENT3
            elif self.round_result == "lose":
                result_text = "졌다... 😅"
                result_color = COLOR_GRAY
            else:
                result_text = "비겼다!"
                result_color = COLOR_ACCENT2

            result_surf = font.render(result_text, True, result_color)
            surface.blit(result_surf, (SCREEN_WIDTH // 2 - result_surf.get_width() // 2, 300))
        else:
            # 선택 대기
            hint = font.render("선택하세요! (1/2/3 또는 클릭)", True, COLOR_TEXT)
            surface.blit(hint, (SCREEN_WIDTH // 2 - hint.get_width() // 2, 200))

            # 물음표 애니메이션
            q_surf = font_big.render("❓", True, COLOR_ACCENT)
            surface.blit(q_surf, (SCREEN_WIDTH // 2 - q_surf.get_width() // 2, 260))

        # 선택 버튼 (결과 표시 중이 아닐 때만)
        if self.round_result is None:
            for btn in self.choice_buttons:
                btn.draw(surface)

        # 히스토리
        if self.round_history:
            hist_y = 490
            font_small = get_font(FONT_SIZE_SMALL)
            for i, h in enumerate(self.round_history[-3:]):
                mark = {"win": "⭕", "lose": "❌", "draw": "➖"}[h["result"]]
                text = f"  {mark} {h['player']} vs {h['pet']}"
                hist_surf = font_small.render(text, True, COLOR_GRAY)
                surface.blit(hist_surf, (30, hist_y + i * 22))
