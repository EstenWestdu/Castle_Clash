import pgzrun
import pygame
from pgzero.actor import Actor
from pgzero.loaders import sounds

from enemy import Enemy
from typing import List
import globals
import sys
import os
# 游戏常量
WIDTH = 900  # 窗口宽度
HEIGHT = 600  # 窗口高度
TITLE = "城堡大作战"
os.environ['SDL_VIDEO_CENTERED'] = '0'  # 禁用自动居中

# 游戏状态
game_state = "start_menu"  # 可以是 "start_menu", "playing", "game_over"
start_menu_image = Actor('begin', pos=(WIDTH//2, HEIGHT//2))
# 初始化游戏变量
def init_game():
    global WAVE_INTERVAL,ENEMY_INTERVAL,WAVE_COUNT,ENEMIES_PER_WAVE
    global Now_level, now_map, enemies, game_time, current_wave
    global next_wave_time, next_enemy_time, enemies_to_spawn
    global game_over, game_result, Now_Blood

    Now_level = globals.level1
    now_map = globals.now_map
    enemies = []

    WAVE_INTERVAL = globals.level1.wave_interval
    ENEMY_INTERVAL = globals.level1.enemy_interval
    WAVE_COUNT = globals.level1.wave_count
    ENEMIES_PER_WAVE = globals.level1.enemies_per_wave
    Now_Blood = globals.level_blood

    game_time = 0.0
    current_wave = 0
    next_wave_time = 3.0
    next_enemy_time = 0.0
    enemies_to_spawn = 0
    game_over = False
    game_result = ""

def start_game():
    """从开始菜单进入游戏"""
    global game_state
    game_state = "playing"
    init_game()
def spawn_enemy(enemy_name):
    """生成一个新敌人"""
    global enemies_to_spawn
    if enemies_to_spawn > 0:
        enemy = Enemy(image_path=enemy_name, path=Now_level.enemy_path,cost=Now_level.enemy_cost[current_wave-1],
                      speed=Now_level.enemy_speed[current_wave-1], blood=Now_level.enemy_blood[current_wave-1])
        enemies.append(enemy)
        enemies_to_spawn -= 1
        return True
    return False

def draw_froze(enemy):
    """
    在敌人底部绘制蓝色填充的冰冻效果（冰刺）
    :param enemy: 敌人对象，使用 pos, width, height 属性
    """
    def draw_filled_polygon(points, color):
        """绘制带填充的多边形（混合Pygame）"""
        # 创建一个临时Surface
        surf = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        # 用pygame绘制多边形
        pygame.draw.polygon(surf, color, points)
        # 将Surface绘制到屏幕上
        screen.blit(surf, (0, 0)) # type: ignore

    ice_spike_height = 20  # 冰刺高度
    ice_fill = (80, 160, 220)  # 冰刺填充颜色（深蓝色）
    # 计算绘制区域（注意：冰刺向上生长所以用减法）
    base_y = enemy.pos[1] + enemy.height / 2  # 敌人底部Y坐标
    left_x = enemy.pos[0] - enemy.width / 2  # 敌人左侧X坐标
    spike_width = enemy.width / 6  # 每个冰刺的宽度
    ice_x = left_x
    for i in range(6):
        if ice_x < ice_x + enemy.width:
            points = [(ice_x,base_y),(ice_x + spike_width,base_y),(ice_x + spike_width//2,base_y - ice_spike_height)]
            draw_filled_polygon(points,ice_fill)
            ice_x += spike_width

def start_new_wave():
    """开始新一波敌人"""
    global current_wave, next_wave_time, next_enemy_time, enemies_to_spawn
    if current_wave < WAVE_COUNT:
        current_wave += 1
        enemies_to_spawn = ENEMIES_PER_WAVE
        next_enemy_time = game_time  # 立即生成第一个
        next_wave_time = game_time + WAVE_INTERVAL
        print(f"开始第 {current_wave} 波敌人!")

def end_game(result: str):
    """结束游戏"""
    global game_over, game_result,game_state
    game_over = True
    game_result = result
    game_state = "game_over"
    # 这里可以添加游戏结束的其他处理，如保存分数等

def update(dt):
    if game_state != "playing":
        return
    """游戏更新逻辑"""
    global game_time, next_enemy_time
    game_time += dt
    # 波次管理
    if current_wave < WAVE_COUNT and game_time >= next_wave_time:
        start_new_wave()

    # 敌人生成
    if enemies_to_spawn > 0 and game_time >= next_enemy_time:
        if spawn_enemy(f"monster{current_wave}"):
                next_enemy_time = game_time + ENEMY_INTERVAL
    # 更新所有敌人
    for enemy in enemies[:]:  # 创建副本以便安全删除
        enemy.move(dt)
        if not enemy.is_alive():
            enemies.remove(enemy)

    #防御塔绘制更新
    for tower in globals.towers:
        tower.update(dt,enemies)

    # 更新所有子弹
    for bullet in globals.bullets[:]:  # 创建副本以便安全删除
        bullet.update(dt)
        if not bullet.alive:
            globals.bullets.remove(bullet)
            continue
        # 检测子弹与敌人的碰撞
        for enemy in enemies:
            if bullet.check_hit(enemy):
                if bullet.bullet_type == "bullet3":
                    for em in enemies:
                        if bullet.check_explode_hit(em):
                            em.take_damage(bullet.damage)
                else:
                    enemy.take_damage(bullet.damage)
                break
    global Now_Blood
    Now_Blood = globals.level_blood
    # 检查游戏结束条件
    if current_wave >= WAVE_COUNT and len(enemies) == 0:
        end_game("SUCCESS!!!")
    elif Now_Blood <= 0:
        end_game("FAIL!!!")

def draw():
    if game_state == "start_menu":
        # 绘制开始菜单
        screen.clear() # type: ignore
        start_menu_image.draw()
    else:
        """游戏绘制逻辑"""
        now_map.draw()
        # 绘制选择框
        if globals.builder.slot_rect is not None :
            screen.draw.rect(globals.builder.slot_rect, 'blue') # pyright: ignore[reportUndefinedVariable]
        # 绘制防御塔预览
        if globals.builder.preview_tower is not None:
            tower_actor = Actor(globals.builder.tower_types[globals.builder.preview_tower]["Image_Name"])
            if globals.builder.preview_pos is not None:
                position = globals.grid_to_screen(globals.builder.preview_pos)
                tower_actor.pos = position
                tower_actor.draw()
                # 绘制攻击范围
                range_radius = globals.builder.tower_types[globals.builder.preview_tower]["range"] * globals.tile_size
                screen.draw.circle( # type: ignore
                    position,
                    range_radius,
                    (100, 100, 255, 50)
                )
        # 绘制所有子弹
        for bullet in globals.bullets:
            bullet.draw()
        # 绘制所有防御塔
        for tower in globals.towers:
            tower.draw()
            # 调试绘制攻击范围
            if tower.is_clicked:
                position = tower.screen_pos
                range_radius = tower.attack_range
                screen.draw.circle( # type: ignore
                    position,
                    range_radius,
                    (100, 100, 255, 50)
                )

        # 绘制所有敌人
        for enemy in enemies:
            enemy.draw()
            if enemy.is_froze():
                draw_froze(enemy)

        # 绘制游戏状态信息
        screen.draw.text( # type: ignore
            f"now_wave: {current_wave}/{WAVE_COUNT} \nenemies_num: {len(enemies)} \nmoney:${globals.money}",
            topleft=(10, 6),
            color="red",
            fontsize=28
        )
        screen.draw.text( # type: ignore
            f"Blood:{Now_Blood}/10",
            topleft=(785, 440),
            color="black",
            fontsize=30
        )
        # 显示下一波倒计时
        if current_wave < WAVE_COUNT:
            countdown = max(0, next_wave_time - game_time)
            screen.draw.text( # type: ignore
                f"next wave: {countdown:.0f} seconds",
                topleft=(10, 70),
                color="blue",
                fontsize=30
            )
        if game_over:
            screen.draw.text( # type: ignore
                f"GAME OVER: {game_result}",
                topleft=(250, 250),
                color="red",
                fontsize=50
            )

def on_mouse_down(pos):
    """鼠标点击事件处理"""
    global game_state
    if game_state == "start_menu":
        sounds.click.play()
        start_game()
    elif game_state == "game_over":
        sys.exit()
    else:
        for tower in globals.towers:
            tower.on_mouse_down(pos)
        globals.builder.on_mouse_down(pos)

def on_mouse_move(pos):
    globals.builder.on_mouse_move(pos)

# 启动游戏
pgzrun.go()