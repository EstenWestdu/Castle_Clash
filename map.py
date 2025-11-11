import pgzrun
from pgzero.actor import Actor
from dataclasses import dataclass
from typing import Tuple, List

class Map:
    def __init__(self,mapname:str,logic_grid:tuple[tuple[int, ...], ...],start:tuple,end:tuple,block_size:int = 72):
        self.mapname = mapname
        self.block_size = block_size
        self.background = Actor(mapname)
        self.width = self.background.width
        self.height = self.background.height
        # 计算网格行列数
        self.cols = self.width // block_size
        self.rows = self.height // block_size
        # 网格逻辑数据
        self.grid = logic_grid  # 二维元组存储网格类型
        self.path = []  # 敌人路径(网格坐标)
        self.buildable = []  # 可建造区域(网格坐标)
        self.start_pos =  start # 起点方格位置
        self.end_pos = end  # 终点方格位置
        self.analyze_logic_grid()#读取网格信息
    def analyze_logic_grid(self):
        """分析逻辑网格，提取路径和可建造区域"""
        for y in range(self.rows):
            for x in range(self.cols):
                cell = self.grid[y][x]
                if cell == 1:  # 路径
                    self.path.append((x, y))
                elif cell == 2:  # 可建造
                    self.buildable.append((x, y))
    def is_buildable(self, grid_x: int, grid_y: int) -> bool:
        """检查指定网格位置是否可以建造"""
        return (grid_x, grid_y) in self.buildable

    def get_grid_pos(self, screen_x: int, screen_y: int) -> tuple[int, int]:
        """屏幕坐标转网格坐标"""
        return screen_x // self.block_size, screen_y // self.block_size

    def get_screen_pos(self, grid_x: int, grid_y: int) -> tuple[int, int]:
        """网格坐标转屏幕坐标(返回格子中心点)"""
        return (
            grid_x * self.block_size + self.block_size // 2,
            grid_y * self.block_size + self.block_size // 2
        )
    def get_path(self) -> list:
        return self.path
    def get_buildable(self) -> list:
        return  self.buildable
    def draw(self):
        self.background.draw()

@dataclass
class Level:
    """关卡数据类"""
    name: str  # 关卡名称
    map_logic: Tuple[Tuple[int, ...], ...]  # 地图逻辑二维元组
    start_pos: Tuple[int, int]              # 起点坐标
    end_pos: Tuple[int, int]                # 终点坐标
    wave_interval:float                     # 敌人波次间隔
    enemy_interval:float                    # 同波次敌人生成间隔
    wave_count:int                          # 总波次数
    enemies_per_wave:int                    # 每波怪物数量
    enemy_path: List[Tuple[int, int]]       # 敌人移动路径
    enemy_cost:List[int]                    # 敌人价值金钱
    enemy_speed: List[float]                # 默认敌人速度
    enemy_blood:List[int]                   # 默认敌人血量
    tile_size: int = 72                     # 默认格子大小
