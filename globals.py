#存储共享变量
from bullet import Bullet
from tower import Tower
from typing import List, Tuple
from map import Level, Map
from mouse_interactive import TowerBuilder
bullets: List[Bullet] = [] # 存储所有活跃的子弹
towers: List[Tower] = []  #存储所有建造的防御塔
money = 200;          #存储当前金钱数
level_blood = 10
tile_size = 72
# 创建第一关实例
level1 = Level(
    name="第一关",
    map_logic=(
        (0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0),
        (0, 0, 0, 2, 2, 2, 2, 2, 2, 2, 0, 0),
        (0, 0, 0, 2, 1, 1, 1, 1, 1, 2, 0, 0),
        (0, 0, 0, 2, 1, 2, 2, 2, 1, 2, 0, 0),
        (0, 2, 2, 2, 1, 2, 0, 0, 1, 2, 2, 2),
        (1, 1, 1, 1, 1, 2, 0, 0, 1, 1, 1, 1),
        (0, 2, 2, 2, 0, 2, 2, 2, 2, 2, 0, 0),
        (0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0),
    ),
    start_pos=(5, 0),
    end_pos=(5, 11),
    enemy_path=[
        (0, 5), (1, 5), (2, 5), (3, 5), (4, 5), (4, 4), (4, 3), (4, 2),
        (5, 2), (6, 2), (7, 2), (8, 2), (8, 3), (8, 4), (8, 5), (9, 5),
        (10, 5), (11, 5),
    ],
    tile_size=72,
    wave_interval=25,                   # 敌人波次间隔
    enemy_interval=2.0,                   # 同波次敌人生成间隔
    wave_count=3,                         # 总波次数
    enemies_per_wave=6,
    enemy_cost=[50,70,80],
    enemy_speed=[0.6,0.45,0.6],
    enemy_blood=[50,150,350]
)
now_map = Map("map1", level1.map_logic, level1.start_pos, level1.end_pos)
builder = TowerBuilder(now_map)
def add_bullet(bullet):
    bullets.append(bullet)


def screen_to_grid(pos) -> Tuple[int, int]:
        """屏幕坐标转网格坐标"""
        return pos[0] // tile_size , pos[1] // tile_size

def grid_to_screen(grid_pos) -> Tuple[int, int]:
        """网格坐标转屏幕坐标(中心点)"""
        return (
            grid_pos[0] * tile_size + tile_size // 2,
            grid_pos[1] * tile_size + tile_size // 2
        )