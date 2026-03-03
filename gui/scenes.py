"""
씬(Scene) 시스템
화면 전환 관리: 타이틀 → 이름 입력 → 메인 → 미니게임 → 네트워크 등
"""
import pygame
import math
import time
import random

from data.constants import (
    SCREEN_WIDTH, SCREEN_HEIGHT, FPS, COLOR_BG, COLOR_BG_DARK,
    COLOR_TEXT, COLOR_WHITE, COLOR_BLACK, COLOR_ACCENT, COLOR_ACCENT2,
    COLOR_ACCENT3, COLOR_HEART, COLOR_STAR, COLOR_GRAY, COLOR_LIGHT_GRAY,
    COLOR_HUNGER, COLOR_HAPPY, COLOR_CLEAN, COLOR_HEALTH, COLOR_ENERGY,
    STAT_BAR_WIDTH, STAT_BAR_HEIGHT,
    FONT_SIZE_SMALL, FONT_SIZE_MEDIUM, FONT_SIZE_LARGE, FONT_SIZE_TITLE,
    STAGE_EGG, STAGE_NAMES, FOODS,
    EGG_HATCH_TIME, AUTO_SAVE_INTERVAL,
)
from gui.ui_elements import (
    Button, StatBar, TextInput, Toast, Particle, Dialog, ExpBar,
    get_font, draw_rounded_rect,
)
from gui.sprites import get_sprite_for_pet, get_sprite, clear_sprite_cache
from gui.animations import (
    BounceAnimation, ShakeAnimation, FloatingText, ZZZAnimation
)
from pet.pet import Pet
from pet import actions
from pet.evolution import get_evolution_description, get_next_evolution_level
from data.save import save_pet, load_pet, has_save, delete_save


class SceneManager:
    """씬 전환 관리"""

    def __init__(self, screen):
        self.screen = screen
        self.current_scene = None
        self.scenes = {}

    def add_scene(self, name, scene):
        self.scenes[name] = scene
        scene.manager = self

    def switch_to(self, name, **kwargs):
        if self.current_scene:
            self.current_scene.on_exit()
        self.current_scene = self.scenes[name]
        self.current_scene.on_enter(**kwargs)

    def handle_event(self, event):
        if self.current_scene:
            self.current_scene.handle_event(event)

    def update(self, dt):
        if self.current_scene:
            self.current_scene.update(dt)

    def draw(self):
        if self.current_scene:
            self.current_scene.draw(self.screen)


class Scene:
    """씬 기본 클래스"""

    def __init__(self):
        self.manager = None

    def on_enter(self, **kwargs):
        pass

    def on_exit(self):
        pass

    def handle_event(self, event):
        pass

    def update(self, dt):
        pass

    def draw(self, surface):
        pass


# ═══════════════════════════════════════════════
# 타이틀 씬
# ═══════════════════════════════════════════════

class TitleScene(Scene):
    """타이틀 화면"""

    def __init__(self):
        super().__init__()
        self.timer = 0
        self.particles = []

        # 버튼
        cx = SCREEN_WIDTH // 2
        self.btn_new = Button(cx - 100, 400, 200, 55, "새 게임",
                              color=COLOR_ACCENT, font_size=FONT_SIZE_LARGE)
        self.btn_load = Button(cx - 100, 470, 200, 55, "이어하기",
                               color=COLOR_ACCENT2, font_size=FONT_SIZE_LARGE)

        self.btn_new.set_callback(self._on_new_game)
        self.btn_load.set_callback(self._on_load_game)

    def on_enter(self, **kwargs):
        self.btn_load.enabled = has_save()
        self.timer = 0

    def _on_new_game(self):
        self.manager.switch_to("naming")

    def _on_load_game(self):
        pet = load_pet()
        if pet:
            self.manager.switch_to("main", pet=pet)
        else:
            self.manager.switch_to("naming")

    def handle_event(self, event):
        self.btn_new.handle_event(event)
        self.btn_load.handle_event(event)

    def update(self, dt):
        self.timer += dt
        # 파티클 생성
        if random.random() < 0.05:
            x = random.randint(50, SCREEN_WIDTH - 50)
            char = random.choice(["♥", "★", "♪", "✿"])
            color = random.choice([COLOR_HEART, COLOR_STAR, COLOR_ACCENT, COLOR_ACCENT2])
            self.particles.append(Particle(x, SCREEN_HEIGHT, char, color, life=3.0))

        self.particles = [p for p in self.particles if p.update(dt)]

    def draw(self, surface):
        surface.fill(COLOR_BG)

        # 배경 장식
        for p in self.particles:
            p.draw(surface)

        # 제목
        font_title = get_font(FONT_SIZE_TITLE + 8)
        title_y = 120 + math.sin(self.timer * 2) * 8

        # 그림자
        shadow = font_title.render("다마고치 ♥", True, (200, 180, 170))
        surface.blit(shadow, (SCREEN_WIDTH // 2 - shadow.get_width() // 2 + 3,
                              title_y + 3))

        title = font_title.render("다마고치 ♥", True, COLOR_ACCENT)
        surface.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, title_y))

        # 부제
        font_sub = get_font(FONT_SIZE_MEDIUM)
        sub = font_sub.render("~ 나만의 가상 펫 ~", True, COLOR_TEXT)
        surface.blit(sub, (SCREEN_WIDTH // 2 - sub.get_width() // 2, title_y + 60))

        # 알 미리보기 (흔들흔들)
        egg = get_sprite(STAGE_EGG, "normal", scale=4)
        egg_x = SCREEN_WIDTH // 2 - egg.get_width() // 2
        egg_y = 230 + math.sin(self.timer * 3) * 5
        egg_angle = math.sin(self.timer * 4) * 5
        rotated = pygame.transform.rotate(egg, egg_angle)
        surface.blit(rotated, (egg_x - (rotated.get_width() - egg.get_width()) // 2, egg_y))

        # 버튼
        self.btn_new.draw(surface)
        self.btn_load.draw(surface)

        # 하단 안내
        font_small = get_font(FONT_SIZE_SMALL)
        info = font_small.render("블루투스 / WiFi로 친구 펫과 만나보세요!", True, COLOR_GRAY)
        surface.blit(info, (SCREEN_WIDTH // 2 - info.get_width() // 2, SCREEN_HEIGHT - 40))


# ═══════════════════════════════════════════════
# 이름 입력 씬
# ═══════════════════════════════════════════════

class NamingScene(Scene):
    """펫 이름 입력"""

    def __init__(self):
        super().__init__()
        cx = SCREEN_WIDTH // 2
        self.text_input = TextInput(cx - 150, 320, 300, 50,
                                    placeholder="이름 입력...", max_length=10)
        self.btn_confirm = Button(cx - 80, 400, 160, 50, "확인!",
                                  color=COLOR_ACCENT, font_size=FONT_SIZE_LARGE)
        self.btn_confirm.set_callback(self._on_confirm)
        self.timer = 0

    def on_enter(self, **kwargs):
        self.text_input.text = ""
        self.text_input.confirmed = False
        self.text_input.active = True
        self.timer = 0
        # IME 활성화
        pygame.key.start_text_input()

    def on_exit(self):
        pygame.key.stop_text_input()

    def _on_confirm(self):
        name = self.text_input.get_text()
        if name:
            # 기존 세이브 삭제
            delete_save()
            # 새 펫 생성
            pet = Pet(name=name)
            self.manager.switch_to("main", pet=pet)

    def handle_event(self, event):
        if self.text_input.handle_event(event):
            self._on_confirm()
        self.btn_confirm.handle_event(event)

    def update(self, dt):
        self.timer += dt
        self.text_input.update(dt)

    def draw(self, surface):
        surface.fill(COLOR_BG)

        # 안내 텍스트
        font = get_font(FONT_SIZE_LARGE)
        text = font.render("펫의 이름을 지어주세요!", True, COLOR_TEXT)
        surface.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, 100))

        # 알 이미지 (흔들흔들)
        egg = get_sprite(STAGE_EGG, "normal", scale=4)
        egg_x = SCREEN_WIDTH // 2 - egg.get_width() // 2
        egg_y = 160 + math.sin(self.timer * 3) * 5
        surface.blit(egg, (egg_x, egg_y))

        font_hint = get_font(FONT_SIZE_SMALL)
        hint = font_hint.render("이 알에서 곧 무언가 태어날 거예요...", True, COLOR_GRAY)
        surface.blit(hint, (SCREEN_WIDTH // 2 - hint.get_width() // 2, 280))

        # 입력 필드
        self.text_input.draw(surface)

        # 확인 버튼
        self.btn_confirm.enabled = len(self.text_input.get_text()) > 0
        self.btn_confirm.draw(surface)


# ═══════════════════════════════════════════════
# 메인 게임 씬
# ═══════════════════════════════════════════════

class MainScene(Scene):
    """메인 게임 화면"""

    def __init__(self):
        super().__init__()
        self.pet = None
        self.toasts = []
        self.floating_texts = []
        self.particles = []
        self.dialog = None

        # 애니메이션
        self.bounce = BounceAnimation(amplitude=6, speed=1.5)
        self.shake = None
        self.zzz = None

        # 상태바
        bar_x = 15
        bar_w = SCREEN_WIDTH // 2 - 30
        self.stat_bars = {
            "hunger": StatBar(bar_x, 50, bar_w, STAT_BAR_HEIGHT, "🍚 포만감",
                              COLOR_HUNGER),
            "happy": StatBar(bar_x, 88, bar_w, STAT_BAR_HEIGHT, "😊 행복도",
                             COLOR_HAPPY),
            "clean": StatBar(bar_x + bar_w + 30, 50, bar_w, STAT_BAR_HEIGHT,
                             "✨ 청결도", COLOR_CLEAN),
            "health": StatBar(bar_x + bar_w + 30, 88, bar_w, STAT_BAR_HEIGHT,
                              "❤️ 건강", COLOR_HEALTH),
        }

        # 경험치 바
        self.exp_bar = ExpBar(bar_x, 122, SCREEN_WIDTH - 30, 12)

        # 메뉴 상태 (버튼 생성 전에 초기화!)
        self.show_food_menu = False
        self.show_play_menu = False
        self.show_net_menu = False
        self.food_buttons = []
        self.play_buttons = []
        self.net_buttons = []

        # 액션 버튼
        self.action_buttons = []
        self._create_action_buttons()

        # 타이머
        self.save_timer = 0
        self.event_timer = 0
        self.game_time = 0

    def _create_action_buttons(self):
        """하단 액션 버튼 생성"""
        btn_data = [
            ("밥", COLOR_HUNGER, self._on_feed),
            ("놀기", COLOR_HAPPY, self._on_play),
            ("청소", COLOR_CLEAN, self._on_clean),
            ("잠", COLOR_ENERGY, self._on_sleep),
            ("약", COLOR_HEALTH, self._on_medicine),
            ("훈련", COLOR_ACCENT2, self._on_train),
        ]

        btn_w = 68
        btn_h = 45
        margin = 6
        total_w = len(btn_data) * (btn_w + margin) - margin
        start_x = (SCREEN_WIDTH - total_w) // 2
        y = SCREEN_HEIGHT - 125

        self.action_buttons = []
        for i, (text, color, callback) in enumerate(btn_data):
            btn = Button(start_x + i * (btn_w + margin), y,
                         btn_w, btn_h, text, color=color, font_size=FONT_SIZE_SMALL)
            btn.set_callback(callback)
            self.action_buttons.append(btn)

        # 네트워크 버튼 (별도 줄)
        self.btn_network = Button(SCREEN_WIDTH // 2 - 90, SCREEN_HEIGHT - 65,
                                  180, 45, "📡 친구 만나기",
                                  color=COLOR_ACCENT3, font_size=FONT_SIZE_SMALL)
        self.btn_network.set_callback(self._on_network)

        # 음식/놀기 팝업은 열 때 동적 생성 (_on_feed / _on_play 에서)
        # 초기값만 설정
        self._food_popup_rect = None
        self._play_popup_rect = None

        # 놀기 서브 메뉴 (정적 — 게임 목록은 변하지 않음)
        games = [("가위바위보", "rps"), ("숫자맞추기", "number"),
                 ("리듬게임", "rhythm"), ("퍼즐", "puzzle"), ("달리기", "runner")]
        play_btn_w = 200
        play_btn_h = 44
        play_popup_w = play_btn_w + 40
        play_popup_x = (SCREEN_WIDTH - play_popup_w) // 2
        play_popup_h = 60 + len(games) * (play_btn_h + 8)
        self._play_popup_rect = (play_popup_x - 10, 200, play_popup_w + 20, play_popup_h)
        game_colors = [
            (255, 160, 140),  # 빨강
            (140, 200, 255),  # 파랑
            (255, 200, 100),  # 노랑
            (160, 230, 160),  # 초록
            (220, 170, 255),  # 보라
        ]
        for i, (name, game_id) in enumerate(games):
            bx = play_popup_x + 10
            by = 260 + i * (play_btn_h + 8)
            btn = Button(bx, by, play_btn_w, play_btn_h, name,
                         color=game_colors[i], font_size=FONT_SIZE_MEDIUM)
            btn.set_callback(lambda gid=game_id: self._start_minigame(gid))
            self.play_buttons.append(btn)

    def on_enter(self, pet=None, **kwargs):
        if pet:
            self.pet = pet
        self.toasts = []
        self.floating_texts = []
        self.show_food_menu = False
        self.show_play_menu = False
        clear_sprite_cache()

        if self.pet and self.pet.stage == STAGE_EGG:
            self.add_toast(f"'{self.pet.name}'의 알이에요! 잠시 기다려주세요...")

    def on_exit(self):
        if self.pet:
            save_pet(self.pet)

    def add_toast(self, message, color=None):
        self.toasts.append(Toast(message, duration=3.0, color=color))

    def add_floating_text(self, text, x=None, y=None, color=(255, 200, 100)):
        if x is None:
            x = SCREEN_WIDTH // 2 - 30
        if y is None:
            y = 250
        self.floating_texts.append(FloatingText(text, x, y, color))

    # ─── 액션 콜백 ───

    def _on_feed(self):
        self.show_play_menu = False
        self.show_food_menu = not self.show_food_menu
        if self.show_food_menu:
            self._build_food_buttons()

    def _build_food_buttons(self):
        """인벤토리 현황 반영하여 음식 버튼 동적 생성"""
        food_names = list(FOODS.keys())
        self.food_buttons = []

        popup_w = 380
        popup_x = (SCREEN_WIDTH - popup_w) // 2
        btn_w = popup_w - 40
        btn_h = 44
        popup_h = 60 + len(food_names) * (btn_h + 8)
        self._food_popup_rect = (popup_x - 10, 200, popup_w + 20, popup_h)

        for i, name in enumerate(food_names):
            food_info = FOODS[name]
            is_free = food_info.get("free", False)
            count = self.pet.inventory.get(name, 0) if self.pet else 0

            if is_free:
                label = f"{name}  (포만+{abs(food_info['hunger'])})  [무한]"
                color = (255, 190, 130)  # 주황
                enabled = True
            else:
                label = f"{name}  (포만+{abs(food_info['hunger'])})  x{count}"
                color = (200, 230, 255) if count > 0 else (200, 200, 200)
                enabled = count > 0

            bx = popup_x + 10
            by = 260 + i * (btn_h + 8)
            btn = Button(bx, by, btn_w, btn_h, label,
                         color=color, font_size=FONT_SIZE_SMALL)
            btn.enabled = enabled
            btn.set_callback(lambda n=name: self._do_feed(n))
            self.food_buttons.append(btn)

    def _do_feed(self, food_name):
        result = actions.feed(self.pet, food_name)
        self.add_toast(result["message"])
        if result["success"]:
            self.add_floating_text(f"+{result['exp']} EXP")
            self._spawn_particles("♥", COLOR_HEART)
        self.show_food_menu = False

    def _on_play(self):
        self.show_play_menu = not self.show_play_menu
        self.show_food_menu = False

    def _start_minigame(self, game_id):
        self.show_play_menu = False
        if self.pet.energy < 10:
            self.add_toast("에너지가 부족해요! 쉬게 해주세요.", COLOR_ACCENT)
            return
        self.manager.switch_to(f"game_{game_id}", pet=self.pet)

    def _on_clean(self):
        result = actions.clean(self.pet)
        self.add_toast(result["message"])
        if result["success"]:
            self.add_floating_text(f"+{result['exp']} EXP")
            self._spawn_particles("✨", COLOR_CLEAN)

    def _on_sleep(self):
        result = actions.sleep(self.pet)
        self.add_toast(result["message"])
        if self.pet.sleeping:
            self.zzz = ZZZAnimation(SCREEN_WIDTH // 2 + 40, 230)
        else:
            self.zzz = None

    def _on_medicine(self):
        result = actions.give_medicine(self.pet)
        self.add_toast(result["message"],
                       color=COLOR_HEALTH if result["success"] else COLOR_GRAY)
        if result["success"]:
            self.shake = None
            self._spawn_particles("💊", COLOR_HEALTH)

    def _on_train(self):
        result = actions.train(self.pet)
        self.add_toast(result["message"])
        if result["success"]:
            self.add_floating_text(f"+{result['exp']} EXP")
            self._spawn_particles("⭐", COLOR_STAR)
            # 보상 표시
            rewards = result.get("rewards", {})
            if rewards:
                reward_text = " ".join(f"{n}x{c}" for n, c in rewards.items())
                self.add_toast(f"🎁 보상: {reward_text}", COLOR_STAR)

    def _on_network(self):
        self.manager.switch_to("network", pet=self.pet)

    def _spawn_particles(self, char, color, count=5):
        cx = SCREEN_WIDTH // 2
        cy = 300
        for _ in range(count):
            x = cx + random.randint(-40, 40)
            y = cy + random.randint(-20, 20)
            self.particles.append(Particle(x, y, char, color, life=1.5))

    # ─── 이벤트 처리 ───

    def _process_pet_events(self):
        """펫에서 발생한 이벤트 처리"""
        while self.pet.pending_events:
            event = self.pet.pending_events.pop(0)
            etype = event["type"]

            if etype == "hatch":
                self.add_toast(f"🐣 {self.pet.name}이(가) 알에서 태어났어요!", COLOR_ACCENT)
                self._spawn_particles("⭐", COLOR_STAR, 10)
                clear_sprite_cache()

            elif etype == "level_up":
                lv = event["data"]["level"]
                self.add_toast(f"🎉 레벨 UP! Lv.{lv}", COLOR_ACCENT3)
                self.add_floating_text(f"Level {lv}!", color=COLOR_STAR)
                self._spawn_particles("★", COLOR_STAR, 8)

            elif etype == "evolve":
                data = event["data"]
                self.add_toast(
                    f"✨ 진화! {data['from_stage']} → {data['to_stage']}",
                    COLOR_STAR
                )
                self._spawn_particles("✨", COLOR_STAR, 15)
                clear_sprite_cache()

            elif etype == "sick":
                self.add_toast(f"😷 {self.pet.name}이(가) 아파요! 약을 주세요!", (255, 100, 100))
                self.shake = ShakeAnimation(intensity=4, speed=6)

            elif etype == "treasure":
                exp = event["data"]["exp"]
                self.add_toast(f"💎 보물 발견! +{exp} EXP", COLOR_STAR)
                self.add_floating_text(f"+{exp} EXP", color=COLOR_STAR)

            elif etype == "special_food":
                food = event["data"]["food"]
                self.add_toast(f"🌈 {food} 발견!")
                actions.apply_special_food(self.pet, food)

            elif etype == "wake_up":
                self.add_toast(f"☀️ {self.pet.name}이(가) 일어났어요!")
                self.zzz = None

            elif etype == "death":
                self.add_toast(f"😢 {self.pet.name}이(가) 하늘나라로...", (100, 100, 100))

    def handle_event(self, event):
        # 다이얼로그 활성 시
        if self.dialog and self.dialog.active:
            self.dialog.handle_event(event)
            return

        # ESC 메뉴 닫기
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.show_food_menu = False
            self.show_play_menu = False
            return

        # 서브 메뉴 버튼 (팝업 모드)
        if self.show_food_menu:
            for btn in self.food_buttons:
                btn.handle_event(event)
            # 팝업 바깥 클릭하면 닫기
            if event.type == pygame.MOUSEBUTTONDOWN:
                popup = pygame.Rect(self._food_popup_rect)
                if not popup.collidepoint(event.pos):
                    self.show_food_menu = False
            return

        if self.show_play_menu:
            for btn in self.play_buttons:
                btn.handle_event(event)
            if event.type == pygame.MOUSEBUTTONDOWN:
                popup = pygame.Rect(self._play_popup_rect)
                if not popup.collidepoint(event.pos):
                    self.show_play_menu = False
            return

        # 메인 버튼
        for btn in self.action_buttons:
            btn.handle_event(event)
        self.btn_network.handle_event(event)

    def update(self, dt):
        if not self.pet:
            return

        self.game_time += dt

        # 펫 업데이트
        self.pet.update(dt)
        self._process_pet_events()

        # 랜덤 이벤트 (60초마다)
        self.event_timer += dt
        if self.event_timer >= 60:
            self.event_timer = 0
            self.pet.check_random_events()
            self._process_pet_events()

        # 자동 저장
        self.save_timer += dt
        if self.save_timer >= AUTO_SAVE_INTERVAL:
            self.save_timer = 0
            save_pet(self.pet)

        # 상태바 업데이트
        self.stat_bars["hunger"].set_value(self.pet.get_satiety())
        self.stat_bars["happy"].set_value(self.pet.happiness)
        self.stat_bars["clean"].set_value(self.pet.cleanliness)
        self.stat_bars["health"].set_value(self.pet.health)
        for bar in self.stat_bars.values():
            bar.update(dt)

        # 경험치 바
        self.exp_bar.set_progress(self.pet.get_exp_progress())
        self.exp_bar.update(dt)

        # 애니메이션
        self.bounce.update(dt)
        if self.shake:
            if not self.shake.update(dt):
                self.shake = None
        if self.zzz:
            self.zzz.update(dt)

        # 토스트/파티클 업데이트
        self.toasts = [t for t in self.toasts if t.update(dt)]
        self.floating_texts = [f for f in self.floating_texts if f.update(dt)]
        self.particles = [p for p in self.particles if p.update(dt)]

        # 아플 때 흔들림
        if self.pet.sick and not self.shake:
            self.shake = ShakeAnimation(intensity=3, speed=5)

        # 버튼 활성화 상태
        is_egg = self.pet.stage == STAGE_EGG
        is_dead = not self.pet.alive
        for btn in self.action_buttons:
            btn.enabled = not is_egg and not is_dead

    def draw(self, surface):
        surface.fill(COLOR_BG)

        if not self.pet:
            return

        # ─── 상태바 패널 ───
        panel_rect = (5, 30, SCREEN_WIDTH - 10, 115)
        draw_rounded_rect(surface, panel_rect, (255, 250, 245), radius=12,
                          border_color=COLOR_LIGHT_GRAY)

        for bar in self.stat_bars.values():
            bar.draw(surface)
        self.exp_bar.draw(surface, level=self.pet.level)

        # ─── 펫 이름 & 정보 ───
        font_name = get_font(FONT_SIZE_LARGE)
        stage_str = STAGE_NAMES.get(self.pet.stage, "?")
        type_str = f" [{self.pet.evolution_type}]" if self.pet.evolution_type else ""
        info_text = f"{self.pet.name}  Lv.{self.pet.level} {stage_str}{type_str}"
        name_surf = font_name.render(info_text, True, COLOR_TEXT)
        surface.blit(name_surf, (SCREEN_WIDTH // 2 - name_surf.get_width() // 2, 155))

        # ─── 펫 스프라이트 ───
        sprite = get_sprite_for_pet(self.pet, scale=4)
        sx = SCREEN_WIDTH // 2 - sprite.get_width() // 2
        sy = 250

        # 애니메이션 오프셋
        ox, oy = self.bounce.get_offset()
        if self.shake:
            sox, soy = self.shake.get_offset()
            ox += sox
            oy += soy

        surface.blit(sprite, (sx + ox, sy + oy))

        # 잠자기 이펙트
        if self.zzz:
            self.zzz.draw(surface)

        # 진화 설명
        desc = get_evolution_description(self.pet.stage, self.pet.evolution_type)
        font_desc = get_font(FONT_SIZE_SMALL)
        desc_surf = font_desc.render(desc[:40], True, COLOR_GRAY)
        surface.blit(desc_surf, (SCREEN_WIDTH // 2 - desc_surf.get_width() // 2,
                                 sy + sprite.get_height() + 10))

        # 다음 진화 안내
        next_lv = get_next_evolution_level(self.pet.stage)
        if next_lv:
            next_text = f"다음 진화: Lv.{next_lv}"
            next_surf = font_desc.render(next_text, True, COLOR_ACCENT2)
            surface.blit(next_surf, (SCREEN_WIDTH // 2 - next_surf.get_width() // 2,
                                     sy + sprite.get_height() + 30))

        # ─── 액션 버튼 ───
        btn_panel = (5, SCREEN_HEIGHT - 140, SCREEN_WIDTH - 10, 135)
        draw_rounded_rect(surface, btn_panel, (255, 248, 240), radius=12,
                          border_color=COLOR_LIGHT_GRAY)

        for btn in self.action_buttons:
            btn.draw(surface)
        self.btn_network.draw(surface)

        # 서브 메뉴 (팝업 오버레이)
        if self.show_food_menu:
            # 반투명 오버레이
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 100))
            surface.blit(overlay, (0, 0))
            # 팝업 배경
            draw_rounded_rect(surface, self._food_popup_rect, (255, 255, 250),
                              radius=12, border_color=COLOR_HUNGER, border_width=3)
            # 제목
            popup_font = get_font(FONT_SIZE_MEDIUM)
            title_surf = popup_font.render("🍚 무엇을 먹을까?", True, COLOR_TEXT)
            surface.blit(title_surf, (self._food_popup_rect[0] + 20, self._food_popup_rect[1] + 12))
            for btn in self.food_buttons:
                btn.draw(surface)

        if self.show_play_menu:
            # 반투명 오버레이
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 100))
            surface.blit(overlay, (0, 0))
            # 팝업 배경
            draw_rounded_rect(surface, self._play_popup_rect, (255, 255, 250),
                              radius=12, border_color=COLOR_HAPPY, border_width=3)
            # 제목
            popup_font = get_font(FONT_SIZE_MEDIUM)
            title_surf = popup_font.render("🎮 어떤 게임을 할까?", True, COLOR_TEXT)
            surface.blit(title_surf, (self._play_popup_rect[0] + 20, self._play_popup_rect[1] + 12))
            for btn in self.play_buttons:
                btn.draw(surface)

        # ─── 이펙트 오버레이 ───
        for ft in self.floating_texts:
            ft.draw(surface)
        for p in self.particles:
            p.draw(surface)

        # 토스트 (상단)
        for i, toast in enumerate(self.toasts[-3:]):
            toast.draw(surface, y=10 + i * 40)

        # 다이얼로그
        if self.dialog and self.dialog.active:
            self.dialog.draw(surface)


# ═══════════════════════════════════════════════
# 네트워크 연결 씬
# ═══════════════════════════════════════════════

class NetworkScene(Scene):
    """네트워크 연결 화면 (BLE/WiFi)"""

    def __init__(self):
        super().__init__()
        self.pet = None
        self.status = "idle"  # idle, scanning, connected
        self.found_peers = []
        self.message = "연결 방식을 선택하세요"
        self.timer = 0

        cx = SCREEN_WIDTH // 2
        self.btn_ble = Button(cx - 100, 200, 200, 50, "🔵 블루투스 검색",
                              color=(180, 210, 255))
        self.btn_wifi = Button(cx - 100, 270, 200, 50, "🟢 WiFi 연결",
                               color=(180, 255, 210))
        self.btn_back = Button(cx - 80, SCREEN_HEIGHT - 80, 160, 45, "← 돌아가기",
                               color=COLOR_GRAY)

        self.btn_ble.set_callback(self._on_ble)
        self.btn_wifi.set_callback(self._on_wifi)
        self.btn_back.set_callback(self._on_back)

        self.wifi_input = TextInput(cx - 120, 340, 240, 40,
                                    placeholder="IP 주소 입력", max_length=15,
                                    font_size=FONT_SIZE_MEDIUM)
        self.btn_wifi_connect = Button(cx - 60, 400, 120, 40, "연결",
                                       color=COLOR_ACCENT2)
        self.show_wifi_input = False

    def on_enter(self, pet=None, **kwargs):
        if pet:
            self.pet = pet
        self.status = "idle"
        self.message = "연결 방식을 선택하세요"
        self.show_wifi_input = False

    def _on_ble(self):
        self.status = "scanning"
        self.message = "블루투스 기기를 검색 중..."
        # 실제 BLE 스캔은 network 모듈에서 처리
        # 여기서는 UI만 표시
        from network.manager import NetworkManager
        if hasattr(self.manager, 'net_manager'):
            self.manager.net_manager.start_ble_scan()

    def _on_wifi(self):
        self.show_wifi_input = True
        self.wifi_input.active = True
        pygame.key.start_text_input()

    def _on_back(self):
        self.manager.switch_to("main", pet=self.pet)

    def handle_event(self, event):
        self.btn_ble.handle_event(event)
        self.btn_wifi.handle_event(event)
        self.btn_back.handle_event(event)

        if self.show_wifi_input:
            self.wifi_input.handle_event(event)
            self.btn_wifi_connect.handle_event(event)

    def update(self, dt):
        self.timer += dt
        if self.show_wifi_input:
            self.wifi_input.update(dt)

    def draw(self, surface):
        surface.fill(COLOR_BG)

        # 제목
        font = get_font(FONT_SIZE_LARGE)
        title = font.render("📡 친구 펫 찾기", True, COLOR_TEXT)
        surface.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 50))

        # 상태 메시지
        font_msg = get_font(FONT_SIZE_MEDIUM)
        msg = font_msg.render(self.message, True, COLOR_GRAY)
        surface.blit(msg, (SCREEN_WIDTH // 2 - msg.get_width() // 2, 120))

        # 스캔 중 표시
        if self.status == "scanning":
            dots = "." * (int(self.timer * 2) % 4)
            scan_text = font_msg.render(f"검색 중{dots}", True, COLOR_ACCENT)
            surface.blit(scan_text, (SCREEN_WIDTH // 2 - scan_text.get_width() // 2, 160))

        # 버튼들
        self.btn_ble.draw(surface)
        self.btn_wifi.draw(surface)

        # WiFi 입력
        if self.show_wifi_input:
            self.wifi_input.draw(surface)
            self.btn_wifi_connect.draw(surface)

            hint = get_font(FONT_SIZE_SMALL)
            hint_text = hint.render("같은 네트워크의 상대 IP를 입력하세요", True, COLOR_GRAY)
            surface.blit(hint_text, (SCREEN_WIDTH // 2 - hint_text.get_width() // 2, 450))

        # 발견된 피어 목록
        if self.found_peers:
            y = 350 if not self.show_wifi_input else 480
            font_peer = get_font(FONT_SIZE_MEDIUM)
            for i, peer in enumerate(self.found_peers[:5]):
                text = f"  {peer.get('name', '???')} (Lv.{peer.get('level', '?')})"
                peer_surf = font_peer.render(text, True, COLOR_TEXT)
                surface.blit(peer_surf, (40, y + i * 35))

        self.btn_back.draw(surface)
