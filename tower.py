import pgzrun
import math
from pgzero.actor import Actor
from typing import Tuple, List, Optional

from pgzero.loaders import sounds

import globals
from bullet import Bullet

turret1 = "tower1"
turret2 = "tower2"
turret3 = "tower3"
anchors1 = (20,48)
anchors2 = (25,32)
anchors3 = (24,44)
class Tower:
    def __init__(self,
                 turret_type: int,
                 position: Tuple[int, int],
                 speed: int = 400,
                 base_image:str = "basic_towers",
                 tile_size: int = 72,
                 attack_range: int = 3,
                 attack_rate: float = 1.0):
        """
        初始化防御塔

        :param base_image: 基座图片路径
        :param turret_type: 炮塔类型
        :param position: 塔的位置(网格坐标)
        :param tile_size: 每个网格的像素大小
        :param attack_range: 攻击范围(格子数)
        """
        # 加载基座和炮塔图像
        self.turret_type = turret_type
        self.base = Actor(base_image)
        if turret_type == 1:
            self.turret = Actor(turret1, anchor=anchors1)
            self.bullet_type = "bullet1"
            self.bullet_damage = 10
            self.attack_rate = attack_rate  # 攻击速度(次/秒)
        elif turret_type == 2:
            self.turret = Actor(turret2, anchor=anchors2)
            self.bullet_type = "bullet2"
            self.bullet_damage = 7
            self.attack_rate = attack_rate # 攻击速度(次/秒)
        else:
            self.turret = Actor(turret3, anchor=anchors3)
            self.bullet_type = "bullet3"
            self.bullet_damage = 4
            self.attack_rate = 0.6  # 攻击速度(次/秒)

        self.bullet_speed = speed

        # 设置位置
        self.grid_pos = position
        self.tile_size = tile_size
        self.screen_pos = (
            position[0]  * tile_size + tile_size // 2,
            position[1] * tile_size + tile_size // 2
        )

        # 设置初始位置
        self.base.pos = self.screen_pos
        self.turret.pos = self.screen_pos
        # 战斗属性
        self.attack_range = attack_range * tile_size  # 转换为像素距离
        self.target = None                            # 当前目标敌人
        self.angle = 0                                # 炮塔角度
        self.cooldown = 0                             # 攻击冷却时间
        self.is_clicked = False                       # 是否被点击
    def update(self, dt: float, enemies: List[Actor]) -> bool:
        """
        更新塔状态
        :param dt: 时间增量(秒)
        :param enemies: 敌人列表
        :return: 是否进行了攻击
        """
        attacked = False
        self.cooldown = max(0, self.cooldown - dt)
        # 寻找目标
        self.target = self._find_target(enemies)
        # 如果有目标且冷却结束，则攻击
        if self.target and self.cooldown <= 0:
            attacked = self._attack()
            self.cooldown = 1.0 / self.attack_rate
        return attacked
    def on_mouse_down(self,pos):
        if self.base.collidepoint(pos):
            sounds.click.play()
            if self.is_clicked:
                self.is_clicked = False
            else:
                self.is_clicked = True

    def _find_target(self, enemies: List[Actor]) -> Optional[Actor]:
        """寻找攻击范围内的敌人
        当bullet_type=bullet2时返回最远的敌人，否则返回最近的敌人
        """
        if not enemies:
            return None
        # 根据子弹类型决定比较函数和目标距离
        if self.bullet_type == "bullet2":
            compare = lambda d, md: d > md  # 寻找更远的
            init_dist = 0
        else:
            compare = lambda d, md: d < md  # 寻找更近的
            init_dist = float('inf')

        target = None
        current_dist = init_dist
        for enemy in enemies:
            dist = self._distance_to(enemy.pos)
            if dist <= self.attack_range and compare(dist, current_dist):
                target = enemy
                current_dist = dist
        return target

    def _distance_to(self, pos: Tuple[float, float]) -> float:
        """计算到指定位置的距离"""
        dx = pos[0] - self.screen_pos[0]
        dy = pos[1] - self.screen_pos[1]
        return math.sqrt(dx * dx + dy * dy)

    def _attack(self) -> bool:
        """执行攻击并创建子弹"""
        if not self.target:
            return False
        # 创建子弹实例
        bullet = Bullet(
            bullet_type=self.bullet_type,
            start_pos=self.screen_pos,
            target_pos=self.target.pos,
            speed=self.bullet_speed,
            damage=self.bullet_damage
        )
        # 这里需要将子弹添加到游戏管理的子弹列表中
        if self.bullet_type == "bullet1":
            sounds.shoot1.play()
        elif self.bullet_type == "bullet2":
            sounds.shoot2.play()
        globals.add_bullet(bullet)
        return True

    def draw(self):
        """绘制防御塔"""
        # 更新炮塔角度指向目标
        if self.target:
            # 计算目标方向角度(注意y轴方向)
            dx = self.target.pos[0] - self.screen_pos[0]
            dy = self.target.pos[1] - self.screen_pos[1]
            self.angle =  math.degrees(math.atan2(-dy, dx)) - 90 % 360
            self.turret.angle = self.angle

        # 绘制基座和炮塔
        self.base.draw()
        self.turret.draw()

