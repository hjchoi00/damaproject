"""
미니게임: 횡스크롤 달리기/점프
장애물을 피하며 최대한 멀리 달리기
"""
import pygame
import random
import math
from minigames.base import MinigameScene
from gui.ui_elements import get_font, draw_rounded_rect
from data.constants import (
    SCREEN_WIDTH, SCREEN_HEIGHT, COLOR_TEXT, COLOR_ACCENT, COLOR_ACCENT2,
    COLOR_ACCENT3, COLOR_GRAY, COLOR_LIGHT_GRAY, COLOR_BG, COLOR_WHITE,
    COLOR_BLACK, COLOR_HEART,
    FONT_SIZE_SMALL, FONT_SIZE_MEDIUM, FONT_SIZE_LARGE, FONT_SIZE_TITLE,
)


GROUND_Y = SCREEN_HEIGHT - 160
GRAVITY = 1200
JUMP_FORCE = -500
RUN_SPEED_INIT = 200
RUN_SPEED_MAX = 450
SPEED_ACCEL = 5  # 초당 속도 증가


class Obstacle:
    """장애물"""

    def __init__(self, x, obs_type="cactus"):
        self.x = x
        self.type = obs_type
        self.passed = False

        if obs_type == "cactus":
            self.width = 20
            self.height = 40
            self.color = (100, 180, 100)
        elif obs_type == "rock":
            self.width = 30
            self.height = 25
            self.color = (160, 150, 140)
        elif obs_type == "bird":
            self.width = 25
            self.height = 20
            self.y_offset = -50  # 공중에 떠있음
            self.color = (180, 140, 100)
        else:
            self.width = 20
            self.height = 35
            self.color = (150, 150, 150)

    @property
    def rect(self):
        y = GROUND_Y - self.height
        if self.type == "bird":
            y += getattr(self, 'y_offset', 0)
        return pygame.Rect(self.x, y, self.width, self.height)


class Star:
    """수집 가능한 별"""

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.collected = False
        self.size = 15


class Cloud:
    """배경 구름"""

    def __init__(self):
        self.x = random.randint(0, SCREEN_WIDTH)
        self.y = random.randint(80, 200)
        self.speed = random.uniform(20, 50)
        self.size = random.randint(30, 60)


class RunnerGame(MinigameScene):
    """횡스크롤 달리기 미니게임"""

    def __init__(self):
        super().__init__(title="🏃 달리기!")
        self.player_x = 80
        self.player_y = GROUND_Y
        self.player_vy = 0
        self.is_jumping = False
        self.is_ducking = False
        self.run_speed = RUN_SPEED_INIT
        self.distance = 0
        self.obstacles = []
        self.stars = []
        self.stars_collected = 0
        self.spawn_timer = 0
        self.clouds = [Cloud() for _ in range(5)]

        # 플레이어 크기
        self.player_w = 24
        self.player_h = 36
        self.duck_h = 20

        # 달리기 애니메이션
        self.run_frame = 0
        self.run_timer = 0

    def _init_game(self):
        self.player_y = GROUND_Y
        self.player_vy = 0
        self.is_jumping = False
        self.is_ducking = False
        self.run_speed = RUN_SPEED_INIT
        self.distance = 0
        self.obstacles = []
        self.stars = []
        self.stars_collected = 0
        self.spawn_timer = 0
        self.run_frame = 0
        self.run_timer = 0
        self.state = "playing"

    def _handle_game_event(self, event):
        if event.type == pygame.KEYDOWN:
            if (event.key == pygame.K_SPACE or event.key == pygame.K_UP) and not self.is_jumping:
                self.player_vy = JUMP_FORCE
                self.is_jumping = True
            elif event.key == pygame.K_DOWN:
                self.is_ducking = True

        elif event.type == pygame.KEYUP:
            if event.key == pygame.K_DOWN:
                self.is_ducking = False

        # 마우스/터치 점프
        elif event.type == pygame.MOUSEBUTTONDOWN and not self.is_jumping:
            self.player_vy = JUMP_FORCE
            self.is_jumping = True

    def _update_game(self, dt):
        # 속도 증가
        self.run_speed = min(RUN_SPEED_MAX, self.run_speed + SPEED_ACCEL * dt)
        self.distance += self.run_speed * dt

        # 점프 물리
        if self.is_jumping:
            self.player_vy += GRAVITY * dt
            self.player_y += self.player_vy * dt

            if self.player_y >= GROUND_Y:
                self.player_y = GROUND_Y
                self.player_vy = 0
                self.is_jumping = False

        # 달리기 애니메이션
        self.run_timer += dt
        if self.run_timer >= 0.15:
            self.run_timer = 0
            self.run_frame = (self.run_frame + 1) % 4

        # 장애물/별 스폰
        self.spawn_timer += dt
        spawn_interval = max(0.8, 2.0 - self.distance / 2000)
        if self.spawn_timer >= spawn_interval:
            self.spawn_timer = 0
            self._spawn_obstacle()

        # 장애물 이동
        for obs in self.obstacles:
            obs.x -= self.run_speed * dt
        self.obstacles = [o for o in self.obstacles if o.x > -50]

        # 별 이동
        for star in self.stars:
            star.x -= self.run_speed * dt
        self.stars = [s for s in self.stars if s.x > -30 and not s.collected]

        # 충돌 체크
        ph = self.duck_h if self.is_ducking else self.player_h
        player_rect = pygame.Rect(self.player_x, self.player_y - ph,
                                  self.player_w, ph)

        for obs in self.obstacles:
            if player_rect.colliderect(obs.rect):
                # 게임 오버
                score = int(self.distance / 10) + self.stars_collected * 20
                if self.distance > 3000:
                    self.finish_game("win", score=score)
                elif self.distance > 1500:
                    self.finish_game("draw", score=score)
                else:
                    self.finish_game("lose", score=score)
                return

            # 통과 보너스
            if not obs.passed and obs.x + obs.width < self.player_x:
                obs.passed = True
                self.score += 10

        # 별 수집
        for star in self.stars:
            if star.collected:
                continue
            star_rect = pygame.Rect(star.x - star.size // 2, star.y - star.size // 2,
                                    star.size, star.size)
            if player_rect.colliderect(star_rect):
                star.collected = True
                self.stars_collected += 1
                self.score += 20

        # 구름 이동
        for cloud in self.clouds:
            cloud.x -= cloud.speed * dt
            if cloud.x < -cloud.size:
                cloud.x = SCREEN_WIDTH + random.randint(0, 100)
                cloud.y = random.randint(80, 200)

    def _spawn_obstacle(self):
        """장애물/별 생성"""
        x = SCREEN_WIDTH + 50
        obs_type = random.choice(["cactus", "cactus", "rock", "rock", "bird"])
        self.obstacles.append(Obstacle(x, obs_type))

        # 가끔 별도 생성
        if random.random() < 0.4:
            star_x = x + random.randint(50, 150)
            star_y = GROUND_Y - random.randint(40, 100)
            self.stars.append(Star(star_x, star_y))

    def _draw_game(self, surface):
        font = get_font(FONT_SIZE_MEDIUM)
        font_small = get_font(FONT_SIZE_SMALL)
        font_big = get_font(FONT_SIZE_LARGE)

        # 하늘 그라데이션 효과 (간단)
        sky_rect = (0, 0, SCREEN_WIDTH, GROUND_Y + 20)
        surface.fill((240, 248, 255))

        # 구름
        for cloud in self.clouds:
            cx, cy = int(cloud.x), int(cloud.y)
            cs = cloud.size
            pygame.draw.ellipse(surface, COLOR_WHITE,
                              (cx, cy, cs, cs // 2), 0)
            pygame.draw.ellipse(surface, COLOR_WHITE,
                              (cx + cs // 4, cy - cs // 4, cs // 2, cs // 3), 0)

        # 땅
        pygame.draw.line(surface, (180, 160, 140),
                        (0, GROUND_Y), (SCREEN_WIDTH, GROUND_Y), 3)
        # 땅 텍스처 (점선)
        for i in range(0, SCREEN_WIDTH, 30):
            offset = int(self.distance * 0.5) % 30
            x = i - offset
            pygame.draw.line(surface, (200, 185, 165),
                           (x, GROUND_Y + 10), (x + 15, GROUND_Y + 10), 1)

        # 장애물
        for obs in self.obstacles:
            r = obs.rect
            if obs.type == "cactus":
                # 선인장 모양
                pygame.draw.rect(surface, obs.color, r, border_radius=3)
                # 가지
                pygame.draw.rect(surface, obs.color,
                               (r.x - 6, r.y + 10, 6, 8), border_radius=2)
                pygame.draw.rect(surface, obs.color,
                               (r.right, r.y + 15, 6, 8), border_radius=2)
            elif obs.type == "rock":
                pygame.draw.ellipse(surface, obs.color, r)
                # 하이라이트
                pygame.draw.ellipse(surface, (190, 185, 175),
                                  (r.x + 5, r.y + 3, r.width // 2, r.height // 3))
            elif obs.type == "bird":
                # 새 모양
                pygame.draw.polygon(surface, obs.color, [
                    (r.x, r.centery),
                    (r.centerx, r.y),
                    (r.right, r.centery),
                    (r.centerx, r.bottom),
                ])
                # 날개
                wing_y = r.y - 5 + math.sin(self.timer * 10) * 5
                pygame.draw.line(surface, obs.color,
                               (r.centerx, r.y), (r.centerx - 10, wing_y), 2)
                pygame.draw.line(surface, obs.color,
                               (r.centerx, r.y), (r.centerx + 10, wing_y), 2)

        # 별
        for star in self.stars:
            if star.collected:
                continue
            sx, sy = int(star.x), int(star.y)
            # 별 반짝임
            glow = abs(math.sin(self.timer * 5)) * 3
            star_color = (255, 220, 80)
            points = []
            for i in range(5):
                angle = math.radians(-90 + i * 72)
                px = sx + math.cos(angle) * (star.size + glow)
                py = sy + math.sin(angle) * (star.size + glow)
                points.append((px, py))
                angle2 = math.radians(-90 + i * 72 + 36)
                px2 = sx + math.cos(angle2) * (star.size // 2)
                py2 = sy + math.sin(angle2) * (star.size // 2)
                points.append((px2, py2))
            if len(points) >= 3:
                pygame.draw.polygon(surface, star_color, points)

        # 플레이어
        ph = self.duck_h if self.is_ducking else self.player_h
        py = int(self.player_y) - ph

        # 몸
        body_color = (255, 200, 170)
        body_rect = (self.player_x, py, self.player_w, ph)
        draw_rounded_rect(surface, body_rect, body_color, radius=6)

        # 눈
        eye_y = py + 6 if not self.is_ducking else py + 3
        pygame.draw.circle(surface, COLOR_BLACK,
                          (self.player_x + 16, eye_y), 3)
        pygame.draw.circle(surface, COLOR_WHITE,
                          (self.player_x + 16, eye_y - 1), 1)

        # 다리 (달리기 애니메이션)
        if not self.is_jumping:
            leg_offsets = [(0, 0), (4, -4), (0, 0), (-4, 4)]
            lo = leg_offsets[self.run_frame]
            # 왼쪽 다리
            pygame.draw.line(surface, (200, 160, 130),
                           (self.player_x + 6, self.player_y),
                           (self.player_x + 6 + lo[0], self.player_y + 8), 3)
            # 오른쪽 다리
            pygame.draw.line(surface, (200, 160, 130),
                           (self.player_x + 16, self.player_y),
                           (self.player_x + 16 + lo[1], self.player_y + 8), 3)

        # 점프 중이면 팔 올리기
        if self.is_jumping:
            pygame.draw.line(surface, body_color,
                           (self.player_x + 4, py + 10),
                           (self.player_x - 6, py - 5), 3)
            pygame.draw.line(surface, body_color,
                           (self.player_x + self.player_w - 4, py + 10),
                           (self.player_x + self.player_w + 6, py - 5), 3)

        # 엎드리기 (↓) 시 표정 변화
        if self.is_ducking:
            fear_y = py + 3
            pygame.draw.line(surface, COLOR_BLACK,
                           (self.player_x + 14, fear_y),
                           (self.player_x + 18, fear_y + 2), 2)

        # HUD
        # 거리
        dist_text = f"거리: {int(self.distance)}m"
        dist_surf = font.render(dist_text, True, COLOR_TEXT)
        surface.blit(dist_surf, (15, 50))

        # 점수
        score_text = f"점수: {self.score}"
        score_surf = font.render(score_text, True, COLOR_TEXT)
        surface.blit(score_surf, (15, 75))

        # 별 수집
        star_text = f"⭐ ×{self.stars_collected}"
        star_surf = font.render(star_text, True, (255, 200, 60))
        surface.blit(star_surf, (SCREEN_WIDTH - star_surf.get_width() - 15, 50))

        # 속도 표시
        speed_pct = (self.run_speed - RUN_SPEED_INIT) / (RUN_SPEED_MAX - RUN_SPEED_INIT)
        speed_text = f"속도: {'▮' * int(speed_pct * 10)}{'▯' * (10 - int(speed_pct * 10))}"
        speed_surf = font_small.render(speed_text, True, COLOR_GRAY)
        surface.blit(speed_surf, (SCREEN_WIDTH - speed_surf.get_width() - 15, 75))

        # 조작 안내
        hint = font_small.render("SPACE/↑: 점프  |  ↓: 엎드리기", True, COLOR_GRAY)
        surface.blit(hint, (SCREEN_WIDTH // 2 - hint.get_width() // 2, SCREEN_HEIGHT - 30))
