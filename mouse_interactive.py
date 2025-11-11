import pgzrun
import pygame
from pgzero.actor import Actor
from typing import Optional, Tuple, List

from pgzero.loaders import sounds
from pygame import Rect, Surface
from map import Map
from tower import Tower
import globals
from pygame.math import Vector2

class TowerBuilder:
    def __init__(self,now_map:Map, tile_size: int = 72):
        """
        初始化防御塔建造系统
        :param tile_size: 每个网格的像素大小
        """
        self.tile_size = tile_size
        self.now_map = now_map
        # 可建造的防御塔类型
        self.tower_types = [
            {"name": "1","cost": 100, "range": 3, "Image_Name":"preview_tower1", "speed":400},
            {"name": "2","cost": 150, "range": 2, "Image_Name":"preview_tower2", "speed":400},
            {"name": "3","cost": 200, "range": 4, "Image_Name":"preview_tower3", "speed":600}
        ]

        # 建造栏位置和大小
        self.build_bar_rect = Rect(243, 0, 256, 70)
        self.tower_slot_size = 62
        self.selected_tower = None  # 当前选中的防御塔类型
        self.preview_tower = None  # 预览防御塔
        self.preview_pos = None  # 预览位置(网格坐标)
        self.slot_rect = None
        # 攻击范围预览
        self.range_surface = Surface((tile_size * 10, tile_size * 10), pygame.SRCALPHA)
        self.map = map

    def on_mouse_down(self, pos):
        """处理鼠标点击事件"""
        # 检查是否点击了建造栏
        if self.build_bar_rect.collidepoint(pos):
            self._handle_build_bar_click(pos)
        elif self.selected_tower is not None:
            # 检查是否点击了可建造区域
            grid_pos = self._screen_to_grid(pos)
            if self._is_valid_build_position(grid_pos):
                self._build_tower(grid_pos)

    def on_mouse_move(self, pos):
        """处理鼠标移动事件"""
        if self.selected_tower is not None:
            grid_pos = self._screen_to_grid(pos)
            if self._is_valid_build_position(grid_pos):
                self.preview_pos = grid_pos
                self.preview_tower = self.selected_tower
            else:
                self.preview_pos = None

    def _handle_build_bar_click(self, pos):
        """处理建造栏点击"""
        i = -1
        if 243 <= pos[0] <= 305:
            i = 0
        elif 340 < pos[0] < 402:
            i = 1
        elif 437 < pos[0] < 499:
            i = 2
        if i >= 0:
            self.slot_rect = Rect(
                243 + i * (self.tower_slot_size + 35),
                5,
                self.tower_slot_size,
                self.tower_slot_size
            )
            if self.slot_rect.collidepoint(pos):
                # 如果点击已选中的防御塔，则取消选择
                if self.selected_tower == i:
                    self.selected_tower = None
                    self.preview_tower = None
                    self.slot_rect = None
                    sounds.click.play()
                else:
                    # 检查是否有足够金钱
                    if globals.money >= self.tower_types[i]["cost"]:
                        self.selected_tower = i
                        self.preview_tower = i
                        sounds.click.play()
                    else:
                        self.slot_rect = None
                        self.selected_tower = None
                        self.preview_tower = None
                        sounds.cute_bubble.play()
                        print("金钱不足!")

    def _build_tower(self, grid_pos):
        """在指定位置建造防御塔"""
        if self.selected_tower is None:
            return

        tower_type = self.tower_types[self.selected_tower]
        sounds.click.play()
        # 扣除金钱
        globals.money -= tower_type["cost"]
        # 创建防御塔
        tower = Tower(
                turret_type=self.selected_tower + 1,
                position=grid_pos,
                attack_range=tower_type["range"],
        )

        # 添加到游戏
        globals.towers.append(tower)

        # 重置选择
        self.slot_rect = None
        self.selected_tower = None
        self.preview_tower = None
        self.preview_pos = None

    def _is_valid_build_position(self, grid_pos:Tuple) -> bool:
        """检查位置是否可以建造防御塔"""
        if not self.now_map.is_buildable(grid_pos[0],grid_pos[1]):
            return False
        # 检查是否已有塔在该位置
        for tower in globals.towers:
            if tower.grid_pos == grid_pos:
                return False

        return True

    def _screen_to_grid(self, pos) -> Tuple[int, int]:
        """屏幕坐标转网格坐标"""
        return pos[0] // self.tile_size , pos[1] // self.tile_size

    def _grid_to_screen(self, grid_pos) -> Tuple[int, int]:
        """网格坐标转屏幕坐标(中心点)"""
        return (
            grid_pos[0] * self.tile_size + self.tile_size // 2,
            grid_pos[1] * self.tile_size + self.tile_size // 2
        )
