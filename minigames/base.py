"""
미니게임 기본 클래스
모든 미니게임은 이 클래스를 상속
"""
import pygame
from gui.scenes import Scene
from gui.ui_elements import get_font, Button, draw_rounded_rect
from data.constants import (
    SCREEN_WIDTH, SCREEN_HEIGHT, COLOR_BG, COLOR_TEXT, COLOR_ACCENT,
    COLOR_GRAY, COLOR_ACCENT2, COLOR_ACCENT3,
    FONT_SIZE_SMALL, FONT_SIZE_MEDIUM, FONT_SIZE_LARGE, FONT_SIZE_TITLE,
    GAME_REWARDS,
)
from pet import actions


class MinigameScene(Scene):
    """미니게임 기본 씬"""

    def __init__(self, title="미니게임"):
        super().__init__()
        self.pet = None
        self.title = title
        self.state = "ready"  # ready, playing, result
        self.result = None     # "win", "lose", "draw"
        self.score = 0
        self.timer = 0
        self.earned_rewards = {}  # 획득한 보상

        # 결과 화면 버튼
        cx = SCREEN_WIDTH // 2
        self.btn_retry = Button(cx - 130, 490, 120, 45, "다시하기",
                                color=COLOR_ACCENT2)
        self.btn_back = Button(cx + 10, 490, 120, 45, "돌아가기",
                               color=COLOR_GRAY)
        self.btn_retry.set_callback(self._on_retry)
        self.btn_back.set_callback(self._on_back)

        # 게임 중 나가기 버튼 (헤더 우측 상단)
        self.btn_exit = Button(SCREEN_WIDTH - 85, 10, 75, 36, "나가기",
                               color=(200, 80, 80), font_size=FONT_SIZE_SMALL)
        self.btn_exit.set_callback(self._on_exit)

    def on_enter(self, pet=None, **kwargs):
        if pet:
            self.pet = pet
        self.state = "ready"
        self.result = None
        self.score = 0
        self.timer = 0
        self.earned_rewards = {}
        self._init_game()

    def _init_game(self):
        """서브클래스에서 오버라이드 - 게임 초기화"""
        pass

    def _on_retry(self):
        self.state = "ready"
        self.result = None
        self.score = 0
        self.timer = 0
        self._init_game()

    def _on_back(self):
        # 결과 적용
        if self.result:
            actions.play(self.pet, self.result)
        self.manager.switch_to("main", pet=self.pet)

    def _on_exit(self):
        """게임 중 나가기 (보상 없이 메인으로)"""
        self.manager.switch_to("main", pet=self.pet)

    def finish_game(self, result, score=0):
        """게임 종료 처리 + 보상 지급"""
        self.state = "result"
        self.result = result
        self.score = score
        # 보상 지급
        if self.pet:
            rewards = GAME_REWARDS.get(result, {})
            self.earned_rewards = {}
            for item_name, count in rewards.items():
                self.pet.inventory[item_name] = self.pet.inventory.get(item_name, 0) + count
                self.earned_rewards[item_name] = count

    def handle_event(self, event):
        if self.state == "result":
            self.btn_retry.handle_event(event)
            self.btn_back.handle_event(event)
            return

        # ESC로 나가기
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self._on_exit()
            return

        # 나가기 버튼
        self.btn_exit.handle_event(event)

        self._handle_game_event(event)

    def _handle_game_event(self, event):
        """서브클래스에서 오버라이드"""
        pass

    def update(self, dt):
        self.timer += dt
        if self.state == "playing":
            self._update_game(dt)

    def _update_game(self, dt):
        """서브클래스에서 오버라이드"""
        pass

    def draw(self, surface):
        surface.fill(COLOR_BG)
        self._draw_header(surface)

        if self.state == "result":
            self._draw_result(surface)
        else:
            self._draw_game(surface)

    def _draw_header(self, surface):
        """상단 헤더"""
        font = get_font(FONT_SIZE_LARGE)
        text = font.render(self.title, True, COLOR_TEXT)
        surface.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, 15))

        # 게임 중일 때 나가기 버튼 표시
        if self.state in ("ready", "playing"):
            self.btn_exit.draw(surface)

    def _draw_game(self, surface):
        """서브클래스에서 오버라이드"""
        pass

    def _draw_result(self, surface):
        """결과 화면"""
        # 결과 텍스트
        font_big = get_font(FONT_SIZE_TITLE)
        if self.result == "win":
            text = "🎉 승리!"
            color = COLOR_ACCENT3
        elif self.result == "draw":
            text = "🤝 무승부"
            color = COLOR_ACCENT2
        else:
            text = "😅 패배..."
            color = COLOR_GRAY

        result_surf = font_big.render(text, True, color)
        surface.blit(result_surf, (SCREEN_WIDTH // 2 - result_surf.get_width() // 2, 180))

        # 점수
        y = 250
        if self.score > 0:
            font_score = get_font(FONT_SIZE_LARGE)
            score_text = f"점수: {self.score}"
            score_surf = font_score.render(score_text, True, COLOR_TEXT)
            surface.blit(score_surf, (SCREEN_WIDTH // 2 - score_surf.get_width() // 2, y))
            y += 50

        # 보상 표시
        font_reward = get_font(FONT_SIZE_MEDIUM)
        if self.result == "win":
            reward_text = "행복도 +20, 경험치 +25!"
        elif self.result == "draw":
            reward_text = "행복도 +12, 경험치 +15!"
        else:
            reward_text = "행복도 +10, 경험치 +15"
        reward_surf = font_reward.render(reward_text, True, COLOR_ACCENT)
        surface.blit(reward_surf, (SCREEN_WIDTH // 2 - reward_surf.get_width() // 2, y))
        y += 35

        # 음식 보상 표시
        if self.earned_rewards:
            items_str = ", ".join(f"{n} x{c}" for n, c in self.earned_rewards.items())
            bonus_text = f"🎁 획득: {items_str}"
            bonus_surf = font_reward.render(bonus_text, True, (255, 140, 60))
            surface.blit(bonus_surf, (SCREEN_WIDTH // 2 - bonus_surf.get_width() // 2, y))
            y += 35
        else:
            if self.result == "lose":
                hint = font_reward.render("승리하면 음식을 얻을 수 있어요!", True, COLOR_GRAY)
                surface.blit(hint, (SCREEN_WIDTH // 2 - hint.get_width() // 2, y))
                y += 35

        # 버튼
        self.btn_retry.draw(surface)
        self.btn_back.draw(surface)
