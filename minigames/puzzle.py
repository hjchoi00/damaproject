"""
미니게임: 슬라이드 퍼즐
3x3 슬라이드 퍼즐 (15퍼즐의 축소판)
"""
import pygame
import random
from minigames.base import MinigameScene
from gui.ui_elements import get_font, Button, draw_rounded_rect
from data.constants import (
    SCREEN_WIDTH, SCREEN_HEIGHT, COLOR_TEXT, COLOR_ACCENT, COLOR_ACCENT2,
    COLOR_ACCENT3, COLOR_GRAY, COLOR_LIGHT_GRAY, COLOR_BG, COLOR_WHITE,
    FONT_SIZE_SMALL, FONT_SIZE_MEDIUM, FONT_SIZE_LARGE, FONT_SIZE_TITLE,
)


TILE_COLORS = [
    (255, 180, 180),  # 1
    (180, 220, 255),  # 2
    (180, 255, 200),  # 3
    (255, 240, 180),  # 4
    (220, 180, 255),  # 5
    (255, 200, 220),  # 6
    (200, 240, 255),  # 7
    (240, 255, 200),  # 8
]


class PuzzleGame(MinigameScene):
    """슬라이드 퍼즐 미니게임"""

    def __init__(self):
        super().__init__(title="🧩 슬라이드 퍼즐")
        self.grid_size = 3
        self.board = []      # 2D 리스트, 0 = 빈 칸
        self.moves = 0
        self.empty_pos = (0, 0)
        self.tile_size = 100
        self.grid_x = (SCREEN_WIDTH - self.grid_size * self.tile_size) // 2
        self.grid_y = 120
        self.animating = False
        self.anim_tile = None
        self.anim_from = None
        self.anim_to = None
        self.anim_progress = 0

    def _init_game(self):
        # 정답 상태 생성
        self.board = []
        num = 1
        for r in range(self.grid_size):
            row = []
            for c in range(self.grid_size):
                if r == self.grid_size - 1 and c == self.grid_size - 1:
                    row.append(0)
                else:
                    row.append(num)
                    num += 1
            self.board.append(row)

        self.empty_pos = (self.grid_size - 1, self.grid_size - 1)

        # 셔플 (충분히 많이)
        self._shuffle(100)
        self.moves = 0
        self.state = "playing"

    def _shuffle(self, count):
        """유효한 이동만으로 셔플 (풀 수 있는 상태 보장)"""
        directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]
        last_dir = None

        for _ in range(count):
            valid_moves = []
            er, ec = self.empty_pos
            for dr, dc in directions:
                nr, nc = er + dr, ec + dc
                if 0 <= nr < self.grid_size and 0 <= nc < self.grid_size:
                    # 역방향 이동 방지 (더 다양하게)
                    if last_dir and (dr, dc) == (-last_dir[0], -last_dir[1]):
                        continue
                    valid_moves.append((dr, dc, nr, nc))

            if valid_moves:
                dr, dc, nr, nc = random.choice(valid_moves)
                self.board[er][ec] = self.board[nr][nc]
                self.board[nr][nc] = 0
                self.empty_pos = (nr, nc)
                last_dir = (dr, dc)

    def _is_solved(self):
        """퍼즐이 완성되었는지 확인"""
        num = 1
        for r in range(self.grid_size):
            for c in range(self.grid_size):
                if r == self.grid_size - 1 and c == self.grid_size - 1:
                    if self.board[r][c] != 0:
                        return False
                else:
                    if self.board[r][c] != num:
                        return False
                    num += 1
        return True

    def _try_move(self, row, col):
        """타일 이동 시도"""
        if self.animating:
            return

        er, ec = self.empty_pos
        # 인접한 타일만 이동 가능
        if abs(row - er) + abs(col - ec) != 1:
            return

        # 이동
        self.board[er][ec] = self.board[row][col]
        self.board[row][col] = 0
        self.empty_pos = (row, col)
        self.moves += 1

        # 완성 체크
        if self._is_solved():
            if self.moves <= 30:
                self.finish_game("win", score=max(50, 300 - self.moves * 5))
            elif self.moves <= 60:
                self.finish_game("draw", score=max(30, 200 - self.moves * 3))
            else:
                self.finish_game("win", score=max(20, 150 - self.moves * 2))

    def _handle_game_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mx, my = event.pos
            # 클릭 위치 → 그리드 좌표
            col = (mx - self.grid_x) // self.tile_size
            row = (my - self.grid_y) // self.tile_size
            if 0 <= row < self.grid_size and 0 <= col < self.grid_size:
                self._try_move(row, col)

        elif event.type == pygame.KEYDOWN:
            er, ec = self.empty_pos
            if event.key == pygame.K_UP and er < self.grid_size - 1:
                self._try_move(er + 1, ec)
            elif event.key == pygame.K_DOWN and er > 0:
                self._try_move(er - 1, ec)
            elif event.key == pygame.K_LEFT and ec < self.grid_size - 1:
                self._try_move(er, ec + 1)
            elif event.key == pygame.K_RIGHT and ec > 0:
                self._try_move(er, ec - 1)

    def _draw_game(self, surface):
        font = get_font(FONT_SIZE_MEDIUM)
        font_big = get_font(FONT_SIZE_TITLE)
        font_small = get_font(FONT_SIZE_SMALL)

        # 이동 횟수
        moves_text = f"이동 횟수: {self.moves}"
        moves_surf = font.render(moves_text, True, COLOR_TEXT)
        surface.blit(moves_surf, (SCREEN_WIDTH // 2 - moves_surf.get_width() // 2, 60))

        # 안내
        hint = font_small.render("클릭 또는 방향키로 빈 칸 옆 타일을 밀어넣으세요", True, COLOR_GRAY)
        surface.blit(hint, (SCREEN_WIDTH // 2 - hint.get_width() // 2, 88))

        # 그리드 배경
        grid_bg = (self.grid_x - 8, self.grid_y - 8,
                   self.grid_size * self.tile_size + 16,
                   self.grid_size * self.tile_size + 16)
        draw_rounded_rect(surface, grid_bg, (240, 230, 220), radius=12,
                          border_color=COLOR_GRAY)

        # 타일 그리기
        for r in range(self.grid_size):
            for c in range(self.grid_size):
                val = self.board[r][c]
                tx = self.grid_x + c * self.tile_size
                ty = self.grid_y + r * self.tile_size

                if val == 0:
                    # 빈 칸
                    empty_rect = (tx + 4, ty + 4, self.tile_size - 8, self.tile_size - 8)
                    draw_rounded_rect(surface, empty_rect, (230, 225, 220), radius=10)
                    continue

                # 타일
                tile_rect = (tx + 4, ty + 4, self.tile_size - 8, self.tile_size - 8)
                color = TILE_COLORS[(val - 1) % len(TILE_COLORS)]

                # 정확한 위치면 더 밝게
                correct_pos = (val - 1) // self.grid_size == r and (val - 1) % self.grid_size == c
                if correct_pos:
                    color = tuple(min(255, c + 20) for c in color)

                # 그림자
                shadow_rect = (tx + 6, ty + 6, self.tile_size - 8, self.tile_size - 8)
                draw_rounded_rect(surface, shadow_rect, (200, 195, 190), radius=10)
                draw_rounded_rect(surface, tile_rect, color, radius=10,
                                  border_color=tuple(max(0, c - 40) for c in color))

                # 숫자
                num_surf = font_big.render(str(val), True, COLOR_TEXT)
                num_rect = num_surf.get_rect(center=(tx + self.tile_size // 2,
                                                     ty + self.tile_size // 2))
                surface.blit(num_surf, num_rect)

                # 정답 체크마크
                if correct_pos:
                    check = font_small.render("✓", True, (100, 200, 100))
                    surface.blit(check, (tx + self.tile_size - 24, ty + 6))

        # 완성 미리보기 (우측 작게)
        preview_size = 20
        px = SCREEN_WIDTH - 90
        py = self.grid_y + self.grid_size * self.tile_size + 20

        preview_label = font_small.render("목표:", True, COLOR_GRAY)
        surface.blit(preview_label, (px, py - 18))

        for r in range(self.grid_size):
            for c in range(self.grid_size):
                num = r * self.grid_size + c + 1
                if num > self.grid_size ** 2 - 1:
                    break
                prx = px + c * (preview_size + 2)
                pry = py + r * (preview_size + 2)
                color = TILE_COLORS[(num - 1) % len(TILE_COLORS)]
                pygame.draw.rect(surface, color, (prx, pry, preview_size, preview_size), border_radius=3)
                n_surf = get_font(10).render(str(num), True, COLOR_TEXT)
                n_rect = n_surf.get_rect(center=(prx + preview_size // 2, pry + preview_size // 2))
                surface.blit(n_surf, n_rect)
