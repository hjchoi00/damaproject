"""
미니게임: 리듬 게임
화면에 떨어지는 노트에 맞춰 방향키 입력
"""
import pygame
import random
import math
from minigames.base import MinigameScene
from gui.ui_elements import get_font, draw_rounded_rect
from data.constants import (
    SCREEN_WIDTH, SCREEN_HEIGHT, COLOR_TEXT, COLOR_ACCENT, COLOR_ACCENT2,
    COLOR_ACCENT3, COLOR_GRAY, COLOR_LIGHT_GRAY, COLOR_BG,
    COLOR_HEART, COLOR_STAR,
    FONT_SIZE_SMALL, FONT_SIZE_MEDIUM, FONT_SIZE_LARGE, FONT_SIZE_TITLE,
)


# 방향키 매핑
LANES = {
    pygame.K_LEFT: 0,
    pygame.K_DOWN: 1,
    pygame.K_UP: 2,
    pygame.K_RIGHT: 3,
}
LANE_NAMES = ["←", "↓", "↑", "→"]
LANE_COLORS = [
    (255, 150, 150),  # 빨강
    (150, 200, 255),  # 파랑
    (150, 255, 150),  # 초록
    (255, 230, 150),  # 노랑
]

JUDGE_PERFECT = 30    # ±30px 이내
JUDGE_GREAT = 60      # ±60px 이내
JUDGE_GOOD = 90       # ±90px 이내


class Note:
    """떨어지는 노트"""

    def __init__(self, lane, spawn_time):
        self.lane = lane
        self.spawn_time = spawn_time
        self.y = -40
        self.hit = False
        self.missed = False
        self.judge = None  # "perfect", "great", "good", "miss"


class RhythmGame(MinigameScene):
    """리듬 게임"""

    def __init__(self):
        super().__init__(title="🎵 리듬 게임")
        self.notes = []
        self.combo = 0
        self.max_combo = 0
        self.perfect = 0
        self.great = 0
        self.good = 0
        self.miss = 0
        self.judge_text = ""
        self.judge_timer = 0
        self.game_timer = 0
        self.game_duration = 30.0  # 30초 게임
        self.note_speed = 300      # px/s
        self.spawn_timer = 0
        self.spawn_interval = 0.5  # 초당 노트 생성
        self.hit_line_y = SCREEN_HEIGHT - 120
        self.lane_width = 80
        self.lane_start_x = (SCREEN_WIDTH - 4 * self.lane_width) // 2
        self.flash_effects = []  # [(lane, timer, judge)]

    def _init_game(self):
        self.notes = []
        self.combo = 0
        self.max_combo = 0
        self.perfect = 0
        self.great = 0
        self.good = 0
        self.miss = 0
        self.judge_text = ""
        self.judge_timer = 0
        self.game_timer = 0
        self.spawn_timer = 0
        self.flash_effects = []
        self.state = "playing"

        # 패턴 사전 생성 (간단한 랜덤)
        self._generate_notes()

    def _generate_notes(self):
        """노트 패턴 생성"""
        t = 1.0  # 1초 후부터 시작
        while t < self.game_duration - 2:
            lane = random.randint(0, 3)
            self.notes.append(Note(lane, t))

            # 가끔 동시 노트
            if random.random() < 0.2:
                other_lane = random.choice([l for l in range(4) if l != lane])
                self.notes.append(Note(other_lane, t))

            t += random.uniform(0.3, 0.7)

    def _handle_game_event(self, event):
        if event.type == pygame.KEYDOWN and event.key in LANES:
            lane = LANES[event.key]
            self._try_hit(lane)

    def _try_hit(self, lane):
        """노트 판정"""
        best_note = None
        best_dist = float('inf')

        for note in self.notes:
            if note.hit or note.missed or note.lane != lane:
                continue
            dist = abs(note.y - self.hit_line_y)
            if dist < best_dist:
                best_dist = dist
                best_note = note

        if best_note and best_dist <= JUDGE_GOOD:
            best_note.hit = True
            if best_dist <= JUDGE_PERFECT:
                best_note.judge = "perfect"
                self.perfect += 1
                self.judge_text = "PERFECT! ✨"
                self.score += 100
            elif best_dist <= JUDGE_GREAT:
                best_note.judge = "great"
                self.great += 1
                self.judge_text = "GREAT! ⭐"
                self.score += 70
            else:
                best_note.judge = "good"
                self.good += 1
                self.judge_text = "GOOD"
                self.score += 40

            self.combo += 1
            self.max_combo = max(self.max_combo, self.combo)
            self.judge_timer = 0.5
            self.flash_effects.append([lane, 0.3, best_note.judge])
        else:
            # 빈 타격
            self.flash_effects.append([lane, 0.15, "miss"])

    def _update_game(self, dt):
        self.game_timer += dt

        # 노트 이동
        for note in self.notes:
            if note.hit or note.missed:
                continue
            # 스폰 타이밍에 맞춰 y 위치 계산
            elapsed = self.game_timer - note.spawn_time
            note.y = elapsed * self.note_speed

            # 히트라인 아래로 벗어남 → 미스
            if note.y > self.hit_line_y + JUDGE_GOOD:
                note.missed = True
                self.miss += 1
                self.combo = 0
                self.judge_text = "MISS..."
                self.judge_timer = 0.5

        # 판정 텍스트 타이머
        if self.judge_timer > 0:
            self.judge_timer -= dt

        # 플래시 이펙트
        self.flash_effects = [[l, t - dt, j] for l, t, j in self.flash_effects if t - dt > 0]

        # 게임 종료
        if self.game_timer >= self.game_duration:
            total = self.perfect + self.great + self.good + self.miss
            if total == 0:
                total = 1
            accuracy = (self.perfect * 100 + self.great * 70 + self.good * 40) / total

            if accuracy >= 70:
                self.finish_game("win", score=self.score + self.max_combo * 5)
            elif accuracy >= 40:
                self.finish_game("draw", score=self.score)
            else:
                self.finish_game("lose", score=self.score)

    def _draw_game(self, surface):
        font = get_font(FONT_SIZE_MEDIUM)
        font_small = get_font(FONT_SIZE_SMALL)
        font_big = get_font(FONT_SIZE_LARGE)

        # 레인 배경
        for i in range(4):
            lx = self.lane_start_x + i * self.lane_width
            lane_rect = (lx, 60, self.lane_width - 4, SCREEN_HEIGHT - 80)
            lane_color = (*LANE_COLORS[i][:3], 30)

            lane_surf = pygame.Surface((self.lane_width - 4, SCREEN_HEIGHT - 80), pygame.SRCALPHA)
            lane_surf.fill((*LANE_COLORS[i], 25))
            surface.blit(lane_surf, (lx, 60))

            # 레인 구분선
            pygame.draw.line(surface, COLOR_LIGHT_GRAY,
                           (lx, 60), (lx, SCREEN_HEIGHT - 20), 1)

        # 히트 라인
        pygame.draw.line(surface, COLOR_ACCENT,
                        (self.lane_start_x, self.hit_line_y),
                        (self.lane_start_x + 4 * self.lane_width, self.hit_line_y), 3)

        # 레인 키 표시
        for i, name in enumerate(LANE_NAMES):
            lx = self.lane_start_x + i * self.lane_width + self.lane_width // 2
            key_surf = font_big.render(name, True, LANE_COLORS[i])
            key_rect = key_surf.get_rect(center=(lx, self.hit_line_y + 30))
            surface.blit(key_surf, key_rect)

        # 플래시 이펙트
        for lane, timer, judge in self.flash_effects:
            lx = self.lane_start_x + lane * self.lane_width
            alpha = int(timer / 0.3 * 150)
            flash_surf = pygame.Surface((self.lane_width - 4, 40), pygame.SRCALPHA)
            if judge == "perfect":
                flash_surf.fill((*COLOR_STAR, alpha))
            elif judge == "great":
                flash_surf.fill((*COLOR_ACCENT3, alpha))
            elif judge == "good":
                flash_surf.fill((*COLOR_ACCENT2, alpha))
            else:
                flash_surf.fill((200, 200, 200, alpha))
            surface.blit(flash_surf, (lx, self.hit_line_y - 20))

        # 노트 그리기
        for note in self.notes:
            if note.hit or note.missed:
                continue
            if note.y < -40 or note.y > SCREEN_HEIGHT:
                continue

            lx = self.lane_start_x + note.lane * self.lane_width
            note_rect = (lx + 5, int(note.y) - 15, self.lane_width - 14, 30)
            draw_rounded_rect(surface, note_rect, LANE_COLORS[note.lane], radius=8)

            # 노트 안에 방향 표시
            arrow_surf = font.render(LANE_NAMES[note.lane], True, COLOR_TEXT)
            arrow_rect = arrow_surf.get_rect(center=(lx + self.lane_width // 2, int(note.y)))
            surface.blit(arrow_surf, arrow_rect)

        # 상단 정보
        # 점수
        score_text = f"점수: {self.score}"
        score_surf = font.render(score_text, True, COLOR_TEXT)
        surface.blit(score_surf, (10, 40))

        # 콤보
        if self.combo > 1:
            combo_surf = font_big.render(f"{self.combo} COMBO", True, COLOR_ACCENT3)
            cx = SCREEN_WIDTH // 2 - combo_surf.get_width() // 2
            surface.blit(combo_surf, (cx, self.hit_line_y - 70))

        # 판정 텍스트
        if self.judge_timer > 0 and self.judge_text:
            alpha = int(self.judge_timer / 0.5 * 255)
            if "PERFECT" in self.judge_text:
                jcolor = COLOR_STAR
            elif "GREAT" in self.judge_text:
                jcolor = COLOR_ACCENT3
            elif "GOOD" in self.judge_text:
                jcolor = COLOR_ACCENT2
            else:
                jcolor = COLOR_GRAY
            judge_surf = font.render(self.judge_text, True, jcolor)
            judge_surf.set_alpha(alpha)
            jx = SCREEN_WIDTH // 2 - judge_surf.get_width() // 2
            surface.blit(judge_surf, (jx, self.hit_line_y - 100))

        # 타이머
        remaining = max(0, self.game_duration - self.game_timer)
        time_text = f"⏱️ {remaining:.1f}s"
        time_surf = font.render(time_text, True, COLOR_TEXT)
        surface.blit(time_surf, (SCREEN_WIDTH - time_surf.get_width() - 15, 40))

        # 하단 통계
        stats_text = f"P:{self.perfect} G:{self.great} O:{self.good} M:{self.miss}"
        stats_surf = font_small.render(stats_text, True, COLOR_GRAY)
        surface.blit(stats_surf, (SCREEN_WIDTH // 2 - stats_surf.get_width() // 2,
                                  SCREEN_HEIGHT - 15))
