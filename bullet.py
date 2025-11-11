import pgzrun
import math

import pygame
from pgzero.actor import Actor
from typing import Tuple, List

from pgzero.loaders import sounds
from pygame import Rect
from pygame.examples.aliens import load_image
from sympy.physics.units import volume

bullet1 = "bullet1"
bullet2 = "bullet2"
bullet3 = "bullet3"
class Bullet:
    def __init__(self,
                 bullet_type: str,
                 start_pos: Tuple[float, float],
                 target_pos: Tuple[float, float],
                 speed: float = 500.0,
                 damage: int = 10):
        """
        初始化子弹
        :param bullet_type: 子弹类型
        :param start_pos: 起始位置(屏幕坐标)
        :param target_pos: 目标位置(屏幕坐标)
        :param speed: 移动速度(像素/秒)
        :param damage: 伤害值
        """
        self.actor = Actor(bullet_type, pos=start_pos, anchor=('center', 'center'))
        dx = target_pos[0] - start_pos[0]
        dy = target_pos[1] - start_pos[1]
        self.actor.angle = math.degrees(math.atan2(-dy, dx)) - 90 % 360
        distance = max(1, math.sqrt(dx * dx + dy * dy))  # 避免除零

        # 标准化方向向量
        self.bullet_type = bullet_type
        self.direction = (dx / distance, dy / distance)
        self.speed = speed
        self.damage = damage
        self.alive = True
        # 爆炸效果相关属性
        self.exploding = False
        self.explode_sound = False
        # 预加载并缩放所有爆炸帧
        self.explode_frames = [f"explosion{i}"for i in range(1,9)]
        self.explode_index = 0
        self.explode_time = 0
        self.explode_pos = None
        self.explode_radius = 100  # 爆炸范围半径
    def update(self, dt: float):
        """更新子弹位置"""
        if not self.alive:
            return
        #如果发生爆炸，更新爆炸动画
        if self.exploding:
            if not self.explode_sound:
                sounds.explodesmall.play()
                self.explode_sound = True
            # 更新爆炸动画
            self.explode_time += dt
            if self.explode_time > 0.1:  # 每0.1秒切换一帧
                self.explode_time = 0
                self.explode_index += 1
                if self.explode_index >= len(self.explode_frames):
                    self.alive = False
            return
        # 移动子弹
        self.actor.x += self.direction[0] * self.speed * dt
        self.actor.y += self.direction[1] * self.speed * dt

    def draw(self):
        """绘制子弹或爆炸动画"""
        if not self.alive:
            return
        if self.exploding:
            # 更新当前帧
            self.actor.pos = self.explode_pos
            frame = self.explode_frames[min(self.explode_index, len(self.explode_frames) - 1)]
            self.actor.image = frame

        self.actor.draw()

    def check_hit(self, enemy) -> bool:
        """检查是否击中敌人"""
        if not self.alive:
            return False
        #子弹的碰撞检测
        bullet_pos = self.actor.pos
        enemy_rect = Rect(enemy.pos[0] - 18, enemy.pos[1] - 18, 36, 36)
        if enemy_rect.collidepoint(bullet_pos):
            if self.bullet_type == bullet2:# 减速子弹效果
                enemy.apply_slow(0.5, 3.0)  # 敌人有apply_slow方法，减速50%，持续3秒
                self.alive = False
            elif self.bullet_type == bullet3:
                self.exploding = True
                self.explode_pos = self.actor.pos
            else:# 普通子弹效果
                self.alive = False
            return True
        return False

    def check_explode_hit(self, enemy) -> bool:
        """检查敌人是否在爆炸范围(仅对爆炸子弹有效)"""
        if not self.exploding or self.bullet_type != bullet3:
            return False
        # 当前爆炸帧达到一定阶段才开始计算伤害
        if self.explode_index == 0:  # 例如从第0帧开始计算伤害
            explode_pos = (self.actor.x, self.actor.y)
            distance = math.sqrt((enemy.pos[0] - explode_pos[0]) ** 2 +
                                     (enemy.pos[1] - explode_pos[1]) ** 2)
            if distance <= self.explode_radius:
                return True
