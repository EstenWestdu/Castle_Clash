import pygame
import time
import globals
from pgzero.actor import Actor

class Enemy:
    def __init__(self,image_path: str,path: list[tuple[int, int]],cost:int,speed: float = 0.5,blood: int = 30,tile_size: int = 72):
        """
        初始化敌人
        image_path: 敌人图像路径
        path: 移动路径(网格坐标列表)
        tile_size: 每个网格的像素大小
        speed: 移动速度(格子/秒)
        blood: 血量
        """
        self.normal_img = image_path
        self.hurt_img = image_path + "hurted"
        self.player = Actor(image_path)
        self.path = path
        self.tile_size = tile_size
        self.cost = cost

        self.base_speed = speed  # 基础速度
        self.current_speed = speed  # 当前速度(可能被减速)
        self.slow_timer = 0  # 减速剩余时间
        self.slow_factor = 1.0  # 当前减速系数(1.0表示无减速)

        self.blood = blood
        self.alive = True
        self.is_hurt = False
        self.hurt_end_time = 0
        self.pos = self.player.pos
        self.width = self.player.width
        self.height = self.player.height
        self.current_segment = 0
        self.progress = 0.0  # 在当前路径段上的进度(0.0-1.0)
        # 初始化位置在路径起点的左侧(屏幕外)
        if len(path) > 0:
            start_x, start_y = path[0]
            # 计算起点左侧屏幕外的位置
            self.player.pos = (
                -self.player.width,  # 完全在屏幕左侧外
                start_y * tile_size + tile_size // 2  # 与起点y坐标对齐
            )
            # 存储目标位置(路径起点)
            self.target_pos = (
                start_x * tile_size + tile_size // 2,
                start_y * tile_size + tile_size // 2
            )
        else:
            self.player.pos = (-1000, -500)
            self.target_pos = (0, 0)
            self.alive = False

    def take_damage(self, amount: int):
        """敌人受到伤害"""
        if not self.alive:
            return

        self.blood = max(0, self.blood - amount)
        self.is_hurt = True
        self.hurt_end_time = time.time() + 0.5  # 0.5秒后恢复
        # 切换到受伤图片
        self.player.image = self.hurt_img
        # 检查是否死亡
        if self.blood <= 0:
            self.alive = False
            globals.money += self.cost
            print("敌人被消灭!")

    def update_hurt_state(self):
        """更新受伤状态"""
        if self.is_hurt and time.time() >= self.hurt_end_time:
            self.is_hurt = False
            self.player.image = self.normal_img

    def move(self, dt: float):
        """移动敌人
        :param dt: 距离上次移动的时间(秒)
        """
        if not self.alive or len(self.path) < 2:
            return
        # 更新减速状态
        if self.slow_timer > 0:
            self.slow_timer -= dt
            if self.slow_timer <= 0:
                self.slow_factor = 1.0  # 减速结束，恢复原速
                self.current_speed = self.base_speed
        # 更新受伤状态
        self.update_hurt_state()

        # 如果还没到达路径起点(从左侧进入)
        if self.current_segment == 0 and self.progress == 0.0:
            # 计算朝向起点的移动方向
            dx = self.target_pos[0] - self.player.x
            dy = self.target_pos[1] - self.player.y
            distance = (dx ** 2 + dy ** 2) ** 0.5
            # 如果已经到达起点，开始沿路径移动
            if distance < self.current_speed * dt * self.tile_size:
                self.player.pos = self.target_pos
                self.current_segment = 0
                self.progress = 0.0
            else:
                # 继续向起点移动
                if distance > 0:
                    self.player.x += (dx / distance) * self.current_speed * dt * self.tile_size
                    self.player.y += (dy / distance) * self.current_speed * dt * self.tile_size
                return
        # 沿路径移动
        segment_length = self._get_segment_length(self.current_segment)
        if segment_length == 0:
            self.alive = False
            return

        # 计算移动距离
        move_distance = self.current_speed * dt
        self.progress += move_distance / segment_length
        # 检查是否需要切换到下一段路径
        while self.progress >= 1.0 and self.current_segment < len(self.path) - 2:
            self.progress -= 1.0
            self.current_segment += 1
            segment_length = self._get_segment_length(self.current_segment)
            if segment_length > 0:
                self.progress = min(self.progress, move_distance / segment_length)

        # 检查是否到达终点
        if self.current_segment >= len(self.path) - 1 or self.progress >= 1.0:
            globals.level_blood -= 1
            self.alive = False
            return

        # 更新位置
        self._update_position()

    def apply_slow(self, factor: float, duration: float):
        """
        应用减速效果
        :param factor: 减速系数(0.5表示速度减半)
        :param duration: 减速持续时间(秒)
        """
        # 如果已经有更强的减速效果，则不覆盖
        if self.slow_factor <= factor:
            return
        self.slow_factor = factor
        self.current_speed = self.base_speed * factor
        self.slow_timer = duration

    def _get_segment_length(self, segment: int) -> float:
        """获取路径段的长度(格子单位)"""
        if segment >= len(self.path) - 1:
            return 0.0
        start_x, start_y = self.path[segment]
        end_x, end_y = self.path[segment + 1]
        return ((end_x - start_x) ** 2 + (end_y - start_y) ** 2) ** 0.5

    def _update_position(self):
        """根据当前路径段和进度更新位置"""
        if self.current_segment >= len(self.path) - 1:
            return

        start_x, start_y = self.path[self.current_segment]
        end_x, end_y = self.path[self.current_segment + 1]

        # 计算当前位置(基于progress)
        current_x = start_x + (end_x - start_x) * self.progress
        current_y = start_y + (end_y - start_y) * self.progress

        # 转换为屏幕坐标
        self.player.pos = (
            current_x * self.tile_size + self.tile_size // 2,
            current_y * self.tile_size + self.tile_size // 2
        )
        self.pos = (self.player.pos[0], self.player.pos[1])

    def draw(self):
        """绘制敌人"""
        if self.alive:
            self.player.draw()

    def is_alive(self) -> bool:
        """检查敌人是否还存在"""
        return self.alive
    def is_froze(self) -> bool:
        if self.slow_factor < 1:
            return True
        else:
            return False