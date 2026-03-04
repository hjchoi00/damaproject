"""
다마고치 (Damagochi) - 가상 펫 게임
메인 엔트리포인트
"""
import sys
import pygame

from data.constants import (
    SCREEN_WIDTH, SCREEN_HEIGHT, FPS,
)
from gui.scenes import (
    SceneManager, TitleScene, NamingScene, MainScene, NetworkScene,
    CharacterSelectScene,
)
from minigames.rps import RPSGame
from minigames.number_guess import NumberGuessGame
from minigames.rhythm import RhythmGame
from minigames.puzzle import PuzzleGame
from minigames.runner import RunnerGame
from data.save import save_pet


def main():
    pygame.init()
    pygame.display.set_caption("🐣 다마고치 - Damagochi")
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    clock = pygame.time.Clock()

    # 씬 매니저 생성
    scene_manager = SceneManager(screen)

    # 씬 등록
    scene_manager.add_scene("title", TitleScene())
    scene_manager.add_scene("naming", NamingScene())
    scene_manager.add_scene("select", CharacterSelectScene())
    scene_manager.add_scene("main", MainScene())
    scene_manager.add_scene("network", NetworkScene())
    scene_manager.add_scene("game_rps", RPSGame())
    scene_manager.add_scene("game_number", NumberGuessGame())
    scene_manager.add_scene("game_rhythm", RhythmGame())
    scene_manager.add_scene("game_puzzle", PuzzleGame())
    scene_manager.add_scene("game_runner", RunnerGame())

    # 시작 씬
    scene_manager.switch_to("title")

    running = True
    while running:
        dt = clock.tick(FPS) / 1000.0  # 초 단위
        dt = min(dt, 0.1)  # 프레임 드롭 방지

        # 이벤트 처리
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                break
            scene_manager.handle_event(event)

        if not running:
            break

        # 현재 씬 업데이트 및 렌더링
        scene_manager.update(dt)
        scene_manager.draw()
        pygame.display.flip()

    # ─── 종료 처리 ───
    _cleanup(scene_manager)
    pygame.quit()
    sys.exit()


def _cleanup(scene_manager):
    """종료 시 저장 및 정리"""
    # 메인 씬에서 펫 저장
    main_scene = scene_manager.scenes.get("main")
    if main_scene and hasattr(main_scene, "pet") and main_scene.pet:
        try:
            save_pet(main_scene.pet)
            print("✅ 펫 데이터 저장 완료!")
        except Exception as e:
            print(f"⚠️ 저장 실패: {e}")

    # 네트워크 정리
    if main_scene and hasattr(main_scene, "network_manager"):
        nm = main_scene.network_manager
        if nm:
            try:
                nm.stop_all()
            except Exception:
                pass

    print("👋 다마고치를 종료합니다. 또 만나요!")


if __name__ == "__main__":
    main()
