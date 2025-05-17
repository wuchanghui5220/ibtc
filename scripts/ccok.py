import pandas as pd
from dataclasses import dataclass
from typing import Dict, Optional, Tuple, List, Any
import itertools


@dataclass
class CablePathInfo:
    """用于存储布线路径信息的数据类"""
    total_length: float
    path_type: str  # 'same_cabinet', 'direct', 'conduit', 'cross_room'
    source_device: str
    target_device: str
    source_room: str
    target_room: str
    source_coords: Tuple[int, int, int]  # (x, y, u)
    target_coords: Tuple[int, int, int]  # (x, y, u)
    conduit_coords: Optional[Tuple[int, int]] = None
    vertical_distance1: float = 0  # 设备到顶部/底部的垂直距离
    vertical_distance2: float = 0  # 设备到顶部/底部的垂直距离
    horizontal_distance: float = 0  # 水平方向总距离
    source_distance: float = 0  # 源水平方向总距离
    target_distance: float = 0  # 目标水平方向总距离
    conduit_vertical_distance: float = 0  # 纵向线槽上的距离
    room_distance: float = 0
    floor_size: float = 0.6  # 每块地板的尺寸
    exit_path: Optional[str] = None

    # 新增属性，表示固定的垂直距离和调整高度
    cabinet_to_conduit_top: float = 1  # 机柜顶部到横向线槽的固定距离(米)
    cabinet_to_conduit_bottom: float = 1  # 机柜底部到横向线槽的固定距离(米)
    fixed_height_adjustment: float = 0.5  # 用于调整固定高度的附加值(米)

    # 新增属性，存储使用的出口信息
    source_exit: Optional[str] = None
    target_exit: Optional[str] = None
    source_conduit_x: Optional[int] = None  # 源机房使用的纵向线槽X坐标
    target_conduit_x: Optional[int] = None  # 目标机房使用的纵向线槽X坐标

    def get_detailed_path(self, is_top_routing: bool) -> str:
        """生成详细的布线路径说明"""
        if self.path_type == 'same_cabinet':
            routing_direction = "上" if is_top_routing else "下"
            vertical_distance = self.cabinet_to_conduit_top if is_top_routing else self.cabinet_to_conduit_bottom
            vertical_distance += self.fixed_height_adjustment
            return (f"同机柜布线：从设备 {self.source_device}({self.source_coords[2]}U) "
                    f"{routing_direction}走线 {vertical_distance:.2f}米 "
                    f"至设备 {self.target_device}({self.target_coords[2]}U)")
        
        elif self.path_type == 'direct':
            routing_direction = "上" if is_top_routing else "下"
            source_x, source_y = self.source_coords[0], self.source_coords[1]
            target_x, target_y = self.target_coords[0], self.target_coords[1]
            
            # 判断是否是同排设备的直连
            if source_y == target_y:
                dx = abs(target_x - source_x) * self.floor_size
                route = [
                    f"从设备 {self.source_device}({self.source_coords[2]}U) {routing_direction}走线 {self.vertical_distance1:.2f}米至机柜顶部",
                    f"在第{source_y}排横向线槽向{'东' if target_x > source_x else '西'}走线 {dx:.2f}米至坐标({target_x}, {source_y})",
                    f"{routing_direction}走线 {self.vertical_distance2:.2f}米至设备 {self.target_device}({self.target_coords[2]}U)"
                ]
                return "同排布线：" + " -> ".join(route)
            else:
                # 原有的不同排直连逻辑
                dx = abs(target_x - source_x) * self.floor_size
                dy = abs(target_y - source_y) * self.floor_size
    
                route = [
                    f"从设备 {self.source_device}({self.source_coords[2]}U) {routing_direction}走线 {self.vertical_distance1:.2f}米至机柜顶部",
                    f"在第{source_y}排横向线槽向{'东' if target_x > source_x else '西'}走线 {dx:.2f}米至坐标({target_x}, {source_y})",
                    f"从坐标({target_x}, {source_y})向{'南' if target_y > source_y else '北'}直接走线 {dy:.2f}米至坐标({target_x}, {target_y})",
                    f"{routing_direction}走线 {self.vertical_distance2:.2f}米至设备 {self.target_device}({self.target_coords[2]}U)"
                ]
                return "直接布线：" + " -> ".join(route)
        
        elif self.path_type == 'conduit':
            routing_direction = "上" if is_top_routing else "下"
            source_x, source_y = self.source_coords[0], self.source_coords[1]
            target_x, target_y = self.target_coords[0], self.target_coords[1]
            conduit_x = self.conduit_coords[0]
            
            dx1 = abs(conduit_x - source_x) * self.floor_size
            dy = abs(target_y - source_y) * self.floor_size
            dx2 = abs(target_x - conduit_x) * self.floor_size
            
            route = [
                f"从设备 {self.source_device}({self.source_coords[2]}U) {routing_direction}走线 {self.vertical_distance1:.2f}米至机柜顶部",
                f"在第{source_y}排横向线槽向{'东' if conduit_x > source_x else '西'}走线 {dx1:.2f}米至纵向线槽({conduit_x}, {source_y})",
                f"在纵向线槽向{'北' if target_y > source_y else '南'}走线 {dy:.2f}米至第{target_y}排",
                f"在第{target_y}排横向线槽向{'东' if target_x > conduit_x else '西'}走线 {dx2:.2f}米至坐标({target_x}, {target_y})",
                f"{routing_direction}走线 {self.vertical_distance2:.2f}米至设备 {self.target_device}({self.target_coords[2]}U)"
            ]
            return "线槽布线：" + " -> ".join(route)
        
        elif self.path_type == 'cross_room':
            routing_direction = "上" if is_top_routing else "下"
            path_segments = self.exit_path.split(" -> ")
            source_exit = path_segments[0]
            target_exit = path_segments[1]
            
            # 解析出口信息
            source_room, source_exit_id = source_exit.split(":")
            target_room, target_exit_id = target_exit.split(":")
            
            source_x, source_y = self.source_coords[0], self.source_coords[1]
            target_x, target_y = self.target_coords[0], self.target_coords[1]
            
            route = [
                f"从设备 {self.source_device}({self.source_coords[2]}U) {routing_direction}走线 {self.vertical_distance1:.2f}米至机柜顶部"
            ]
            
            # 添加源机房内的详细路径
            if self.source_conduit_x is not None:
                source_conduit_x = self.source_conduit_x
                source_dx = abs(source_conduit_x - source_x) * self.floor_size
                source_dx_direction = '东' if source_conduit_x > source_x else '西'
                
                route.append(f"在第{source_y}排横向线槽向{source_dx_direction}走线 {source_dx:.2f}米至纵向线槽({source_conduit_x}, {source_y})")
                
                # 找到出口坐标
                if '_' in source_exit_id:
                    try:
                        exit_number = source_exit_id.split('_')[1]
                        try:
                            exit_x = int(exit_number)
                            exit_dx = abs(exit_x - source_conduit_x) * self.floor_size
                            direction = '东' if exit_x > source_conduit_x else '西'
                            route.append(f"在纵向线槽向南走线至出口排，然后在横向线槽向{direction}走线 {exit_dx:.2f}米至机房出口 {source_exit_id}")
                        except ValueError:
                            route.append(f"在纵向线槽向南走线至出口排，然后在横向线槽向机房出口 {source_exit_id}")
                    except (IndexError, ValueError):
                        route.append(f"在纵向线槽向南走线至出口排，然后向机房出口 {source_exit_id}")
                else:
                    route.append(f"在纵向线槽向南走线至出口排，然后向机房出口 {source_exit_id}")
            
            # 添加机房间通道距离
            route.append(f"通过机房间通道 {self.room_distance:.2f}米至目标机房入口 {target_exit_id}")
            
            # 添加目标机房内的详细路径
            if self.target_conduit_x is not None:
                target_conduit_x = self.target_conduit_x
                
                if '_' in target_exit_id:
                    try:
                        exit_number = target_exit_id.split('_')[1]
                        try:
                            entry_x = int(exit_number)
                            entry_dx = abs(target_conduit_x - entry_x) * self.floor_size
                            direction = '东' if target_conduit_x > entry_x else '西'
                            route.append(f"从入口在横向线槽向{direction}走线 {entry_dx:.2f}米至纵向线槽({target_conduit_x}, -)")
                        except ValueError:
                            route.append(f"从入口在横向线槽至纵向线槽({target_conduit_x}, -)")
                    except (IndexError, ValueError):
                        route.append(f"从入口在横向线槽至纵向线槽({target_conduit_x}, -)")
                else:
                    route.append(f"从入口在横向线槽至纵向线槽({target_conduit_x}, -)")
                
                # 计算从纵向线槽到目标设备的路径
                target_dx = abs(target_x - target_conduit_x) * self.floor_size
                target_dx_direction = '东' if target_x > target_conduit_x else '西'
                
                # route.append(f"在纵向线槽向{'北' if target_y > 0 else '南'}走线至第{target_y}排")
                route.append(f"在纵向线槽走线至第{target_y}排")
                route.append(f"在第{target_y}排横向线槽向{target_dx_direction}走线 {target_dx:.2f}米至坐标({target_x}, {target_y})")
            
            route.append(f"{routing_direction}走线 {self.vertical_distance2:.2f}米至设备 {self.target_device}({self.target_coords[2]}U)")
            
            return "跨机房布线：" + " -> ".join(route)
        
        return "未知布线类型"


@dataclass
class RoomExit:
    """机房出口信息"""
    room_id: str
    exit_id: str
    x: int
    y: int

@dataclass
class ExitDistance:
    """机房出口间距离"""
    from_room: str
    from_exit: str
    to_room: str
    to_exit: str
    distance: float

class DataCenter:
    def __init__(self, room_id, floor_size=0.6):
        self.room_id = room_id
        self.floor_size = floor_size
        self.devices = {}
        self.vertical_conduits = set()  # 改用集合存储纵向线槽的 X 坐标
        self.room_exits = {}  # 初始化 room_exits 字典
        self.exits = {}  # 存储出口信息，包括坐标
        self.config = {
            'u_height': 0.0445,  # 每U的高度(米)
            'total_u_height': 54,  # 机柜总高度(U)
            'cabinet_to_conduit_top': 1,  # 机柜顶部到横向线槽的固定距离(米)
            'cabinet_to_conduit_bottom': 1,  # 机柜底部到横向线槽的固定距离(米)
            'is_top_routing': True,  # True为上走线，False为下走线
            'fixed_height_adjustment': 0.5,  # 用于调整固定高度的附加值(米)
        }
        self.exit_distances = []

    def add_vertical_conduit(self, x: int):
        """添加纵向线槽的 X 坐标"""
        self.vertical_conduits.add(x)

    def find_nearest_vertical_conduit(self, source_x: int) -> Optional[int]:
        """找到最近的纵向线槽的 X 坐标"""
        if not self.vertical_conduits:
            return None
            
        min_distance = float('inf')
        nearest_x = None
        
        for conduit_x in self.vertical_conduits:
            distance = abs(source_x - conduit_x)
            if distance < min_distance:
                min_distance = distance
                nearest_x = conduit_x
                
        return nearest_x

    def add_room_exit(self, x: int, y: int, exit_id: str):
        """添加机房出口"""
        self.room_exits[exit_id] = RoomExit(
            room_id=self.room_id,
            exit_id=exit_id,
            x=x,
            y=y
        )
        # 同时将出口添加到exits字典中
        self.exits[exit_id] = {
            'x': x,
            'y': y,
            'u_position': self.config['total_u_height'],  # 使用机柜最大高度
            'floor_x': x * self.floor_size,
            'floor_y': y * self.floor_size
        }

    def add_device(self, device_id: str, x: int, y: int, u_position: int):
        """添加设备到机房"""
        self.devices[device_id] = {
            'x': x,
            'y': y,
            'u_position': u_position,
            'floor_x': x * self.floor_size,
            'floor_y': y * self.floor_size
        }

    def get_all_room_exits_to_target(self, target_room: str) -> Dict[str, float]:
        """获取所有可以到达目标机房的出口"""
        valid_exits = {}
        
        for exit_id, exit_info in self.room_exits.items():
            # 检查是否有到目标机房的路径
            for d in self.exit_distances:
                if (d.from_room == self.room_id and 
                    d.from_exit == exit_id and 
                    d.to_room == target_room):
                    # 找到到目标机房的路径
                    valid_exits[exit_id] = d.distance
                    break
                    
        return valid_exits

    def find_nearest_vertical_conduit_to_exit(self, exit_id: str) -> Optional[int]:
        """找到最接近出口的纵向线槽"""
        if exit_id not in self.room_exits or not self.vertical_conduits:
            return None
            
        exit_x = self.room_exits[exit_id].x
        return self.find_nearest_vertical_conduit(exit_x)

    def calculate_path_to_exit(self, device_coords: Tuple[int, int, int], exit_id: str) -> Dict[str, Any]:
        """计算设备到出口的路径距离"""
        if exit_id not in self.room_exits:
            raise ValueError(f"Exit {exit_id} not found in room {self.room_id}")
        
        device_x, device_y, device_u = device_coords
        exit_info = self.room_exits[exit_id]
        exit_x, exit_y = exit_info.x, exit_info.y
        
        # 找到最接近出口的纵向线槽
        conduit_x = self.find_nearest_vertical_conduit_to_exit(exit_id)
        
        if conduit_x is None:
            # 没有纵向线槽，直接计算距离
            dx = abs(exit_x - device_x) * self.floor_size
            dy = abs(exit_y - device_y) * self.floor_size
            
            # 计算固定高度调整值
            fixed_height = (self.config['cabinet_to_conduit_top'] + 
                           self.config['fixed_height_adjustment']
                           if self.config['is_top_routing'] 
                           else self.config['cabinet_to_conduit_bottom'] + 
                           self.config['fixed_height_adjustment'])
            
            # 计算垂直距离
            if self.config['is_top_routing']:
                v1 = ((self.config['total_u_height'] - device_u) * 
                     self.config['u_height'] + fixed_height)
            else:
                v1 = device_u * self.config['u_height'] + fixed_height
            
            return {
                'total_distance': dx + dy + v1,
                'horizontal_distance': dx + dy,
                'vertical_distance': v1,
                'path_type': 'direct',
                'conduit_x': None
            }
        else:
            # 通过纵向线槽走线
            dx1 = abs(conduit_x - device_x) * self.floor_size
            dy1 = abs(conduit_x - device_y) * self.floor_size
            dx2 = abs(exit_x - conduit_x) * self.floor_size
            dy2 = abs(exit_y - device_y) * self.floor_size
            
            # 计算固定高度调整值
            fixed_height = (self.config['cabinet_to_conduit_top'] + 
                           self.config['fixed_height_adjustment']
                           if self.config['is_top_routing'] 
                           else self.config['cabinet_to_conduit_bottom'] + 
                           self.config['fixed_height_adjustment'])
            
            # 计算垂直距离
            if self.config['is_top_routing']:
                v1 = ((self.config['total_u_height'] - device_u) * 
                     self.config['u_height'] + fixed_height)
            else:
                v1 = device_u * self.config['u_height'] + fixed_height
            
            return {
                'total_distance': dx1 + dy2 + dx2 + v1,
                'horizontal_distance': dx1 + dy2 + dx2,
                'vertical_distance': v1,
                'path_type': 'conduit',
                'conduit_x': conduit_x
            }

    def calculate_cable_length(self, source_device: str, target_device: str, 
                         target_datacenter: Optional['DataCenter'] = None) -> CablePathInfo:
        """计算两个设备之间的布线路径和长度"""
        # 检查源设备是否在devices或exits中
        if source_device not in self.devices and source_device not in self.exits:
            raise ValueError(f"Source device/exit {source_device} not found")
        
        # 获取源设备/出口的信息
        source = self.devices.get(source_device) or self.exits.get(source_device)
        source_coords = (source['x'], source['y'], source['u_position'])
        
        # 同机房布线
        if target_datacenter is None:
            # 检查目标设备是否在devices或exits中
            if target_device not in self.devices and target_device not in self.exits:
                raise ValueError(f"Target device/exit {target_device} not found")
            
            # 获取目标设备/出口的信息
            target = self.devices.get(target_device) or self.exits.get(target_device)
            target_coords = (target['x'], target['y'], target['u_position'])
            
            # 计算固定高度调整
            fixed_height = (self.config['cabinet_to_conduit_top'] + self.config['fixed_height_adjustment'] 
                           if self.config['is_top_routing'] 
                           else self.config['cabinet_to_conduit_bottom'] + self.config['fixed_height_adjustment'])
            
            # 1. 同机柜设备
            if source['x'] == target['x'] and source['y'] == target['y']:
                # 如果涉及出口点，使用固定高度调整
                if source_device in self.exits or target_device in self.exits:
                    vertical_dist = fixed_height
                else:
                    vertical_dist = abs(source['u_position'] - target['u_position']) * self.config['u_height'] + fixed_height
                
                return CablePathInfo(
                    total_length=vertical_dist,
                    path_type='same_cabinet',
                    source_device=source_device,
                    target_device=target_device,
                    source_room=self.room_id,
                    target_room=self.room_id,
                    source_coords=source_coords,
                    target_coords=target_coords,
                    vertical_distance1=vertical_dist,
                    floor_size=self.floor_size,
                    cabinet_to_conduit_top=self.config['cabinet_to_conduit_top'],
                    cabinet_to_conduit_bottom=self.config['cabinet_to_conduit_bottom'],
                    fixed_height_adjustment=self.config['fixed_height_adjustment']
                )
            
            # 2. 判断是否在同一排，如果是直接使用横向线槽，不经过纵向线槽
            if source['y'] == target['y']:  # 同一排设备
                dx = abs(target['x'] - source['x']) * self.floor_size
                
                # 处理出口点的垂直距离
                if source_device in self.exits:
                    v1 = fixed_height
                else:
                    v1 = ((self.config['total_u_height'] - source['u_position']) * self.config['u_height'] + fixed_height 
                          if self.config['is_top_routing'] 
                          else source['u_position'] * self.config['u_height'] + fixed_height)
                
                if target_device in self.exits:
                    v2 = fixed_height
                else:
                    v2 = ((self.config['total_u_height'] - target['u_position']) * self.config['u_height'] + fixed_height
                          if self.config['is_top_routing']
                          else target['u_position'] * self.config['u_height'] + fixed_height)
                
                return CablePathInfo(
                    total_length=dx + v1 + v2,
                    path_type='direct',  # 同排设备使用直接布线
                    source_device=source_device,
                    target_device=target_device,
                    source_room=self.room_id,
                    target_room=self.room_id,
                    source_coords=source_coords,
                    target_coords=target_coords,
                    horizontal_distance=dx,
                    vertical_distance1=v1,
                    vertical_distance2=v2,
                    floor_size=self.floor_size,
                    cabinet_to_conduit_top=self.config['cabinet_to_conduit_top'],
                    cabinet_to_conduit_bottom=self.config['cabinet_to_conduit_bottom'],
                    fixed_height_adjustment=self.config['fixed_height_adjustment']
                )
            
            # 3. 查找最近的纵向线槽（只有在不同排才执行此逻辑）
            nearest_conduit_x = self.find_nearest_vertical_conduit(source['x'])
            
            # 如果没有线槽，直接布线
            if nearest_conduit_x is None:
                dx = abs(target['x'] - source['x']) * self.floor_size
                dy = abs(target['y'] - source['y']) * self.floor_size
                
                # 处理出口点的垂直距离
                if source_device in self.exits:
                    v1 = fixed_height
                else:
                    v1 = ((self.config['total_u_height'] - source['u_position']) * self.config['u_height'] + fixed_height 
                          if self.config['is_top_routing'] 
                          else source['u_position'] * self.config['u_height'] + fixed_height)
                
                if target_device in self.exits:
                    v2 = fixed_height
                else:
                    v2 = ((self.config['total_u_height'] - target['u_position']) * self.config['u_height'] + fixed_height
                          if self.config['is_top_routing']
                          else target['u_position'] * self.config['u_height'] + fixed_height)
                
                return CablePathInfo(
                    total_length=dx + dy + v1 + v2,
                    path_type='direct',
                    source_device=source_device,
                    target_device=target_device,
                    source_room=self.room_id,
                    target_room=self.room_id,
                    source_coords=source_coords,
                    target_coords=target_coords,
                    horizontal_distance=dx + dy,
                    vertical_distance1=v1,
                    vertical_distance2=v2,
                    floor_size=self.floor_size,
                    cabinet_to_conduit_top=self.config['cabinet_to_conduit_top'],
                    cabinet_to_conduit_bottom=self.config['cabinet_to_conduit_bottom'],
                    fixed_height_adjustment=self.config['fixed_height_adjustment']
                )
            
            # 4. 通过线槽布线
            dx1 = abs(nearest_conduit_x - source['x']) * self.floor_size
            dy = abs(target['y'] - source['y']) * self.floor_size
            dx2 = abs(target['x'] - nearest_conduit_x) * self.floor_size
            
            # 处理出口点的垂直距离
            if source_device in self.exits:
                v1 = fixed_height
            else:
                v1 = ((self.config['total_u_height'] - source['u_position']) * self.config['u_height'] + fixed_height 
                     if self.config['is_top_routing'] 
                     else source['u_position'] * self.config['u_height'] + fixed_height)
            
            if target_device in self.exits:
                v2 = fixed_height
            else:
                v2 = ((self.config['total_u_height'] - target['u_position']) * self.config['u_height'] + fixed_height
                     if self.config['is_top_routing']
                     else target['u_position'] * self.config['u_height'] + fixed_height)
            
            # 存储线槽的x坐标用于路径描述
            path_info = CablePathInfo(
                total_length=dx1 + dy + dx2 + v1 + v2,
                path_type='conduit',
                source_device=source_device,
                target_device=target_device,
                source_room=self.room_id,
                target_room=self.room_id,
                source_coords=source_coords,
                target_coords=target_coords,
                conduit_coords=(nearest_conduit_x, source['y']),  # 保存完整的线槽坐标
                horizontal_distance=dx1 + dx2,
                vertical_distance1=v1,
                vertical_distance2=v2,
                conduit_vertical_distance=dy,
                floor_size=self.floor_size,
                cabinet_to_conduit_top=self.config['cabinet_to_conduit_top'],
                cabinet_to_conduit_bottom=self.config['cabinet_to_conduit_bottom'],
                fixed_height_adjustment=self.config['fixed_height_adjustment'],
                source_conduit_x=nearest_conduit_x
            )
            return path_info
        
        # 跨机房布线 - 改进逻辑，考虑所有出口入口组合
        else:
            if target_device not in target_datacenter.devices:
                raise ValueError(f"Target device {target_device} not found in target datacenter")
            
            # 获取目标设备的信息
            target = target_datacenter.devices[target_device]
            target_coords = (target['x'], target['y'], target['u_position'])
            
            # 1. 获取所有可能的出口入口组合
            source_exits = self.get_all_room_exits_to_target(target_datacenter.room_id)
            if not source_exits:
                raise ValueError(f"No exit path found from room {self.room_id} to {target_datacenter.room_id}")
            
            target_exits = target_datacenter.get_all_room_exits_to_target(self.room_id)
            if not target_exits:
                raise ValueError(f"No entry path found from room {target_datacenter.room_id} to {self.room_id}")
            
            # 2. 计算所有组合的完整路径长度
            best_path = None
            min_total_length = float('inf')
            
            for source_exit_id, target_exit_id in itertools.product(source_exits.keys(), target_exits.keys()):
                # 检查这两个出口之间是否有直接连接
                room_dist = None
                for exit_dist in self.exit_distances:
                    if (exit_dist.from_room == self.room_id and 
                        exit_dist.from_exit == source_exit_id and 
                        exit_dist.to_room == target_datacenter.room_id and 
                        exit_dist.to_exit == target_exit_id):
                        room_dist = exit_dist.distance
                        break
                
                if room_dist is None:
                    # 这两个出口之间没有直接连接
                    continue
                
                # 计算源设备到源出口的路径
                source_to_exit = self.calculate_path_to_exit(source_coords, source_exit_id)
                
                # 计算目标入口到目标设备的路径
                target_entry_coords = (
                    target_datacenter.room_exits[target_exit_id].x,
                    target_datacenter.room_exits[target_exit_id].y,
                    target_datacenter.config['total_u_height']
                )
                target_from_exit = target_datacenter.calculate_path_to_exit(
                    target_coords, target_exit_id
                )
                
                # 计算总路径长度
                total_length = (source_to_exit['total_distance'] + 
                               room_dist + 
                               target_from_exit['total_distance'])
                
                # 如果是最短路径，则保存
                if total_length < min_total_length:
                    min_total_length = total_length
                    
                    # 创建路径描述
                    path_desc = f"{self.room_id}:{source_exit_id} -> {target_datacenter.room_id}:{target_exit_id}"
                    
                    # 计算固定高度调整值
                    fixed_height_source = (self.config['cabinet_to_conduit_top'] + 
                                         self.config['fixed_height_adjustment']
                                         if self.config['is_top_routing'] 
                                         else self.config['cabinet_to_conduit_bottom'] + 
                                         self.config['fixed_height_adjustment'])
                    
                    fixed_height_target = (target_datacenter.config['cabinet_to_conduit_top'] + 
                                         target_datacenter.config['fixed_height_adjustment']
                                         if target_datacenter.config['is_top_routing'] 
                                         else target_datacenter.config['cabinet_to_conduit_bottom'] + 
                                         target_datacenter.config['fixed_height_adjustment'])
                    
                    # 创建最佳路径信息
                    best_path = CablePathInfo(
                        total_length=total_length,
                        path_type='cross_room',
                        source_device=source_device,
                        target_device=target_device,
                        source_room=self.room_id,
                        target_room=target_datacenter.room_id,
                        source_coords=source_coords,
                        target_coords=target_coords,
                        horizontal_distance=source_to_exit['horizontal_distance'] + room_dist + target_from_exit['horizontal_distance'],
                        source_distance=source_to_exit['horizontal_distance'],
                        target_distance=target_from_exit['horizontal_distance'],
                        vertical_distance1=source_to_exit['vertical_distance'],
                        vertical_distance2=target_from_exit['vertical_distance'],
                        room_distance=room_dist,
                        exit_path=path_desc,
                        floor_size=self.floor_size,
                        cabinet_to_conduit_top=self.config['cabinet_to_conduit_top'],
                        cabinet_to_conduit_bottom=self.config['cabinet_to_conduit_bottom'],
                        fixed_height_adjustment=self.config['fixed_height_adjustment'],
                        source_exit=source_exit_id,
                        target_exit=target_exit_id,
                        source_conduit_x=source_to_exit.get('conduit_x'),
                        target_conduit_x=target_from_exit.get('conduit_x')
                    )
            
            if best_path is None:
                raise ValueError(f"No valid path found between rooms {self.room_id} and {target_datacenter.room_id}")
            
            return best_path

class DataCenterNetwork:
    def __init__(self):
        self.datacenters: Dict[str, DataCenter] = {}
        self.exit_distances: List[ExitDistance] = []

    def add_datacenter(self, room_id: str, floor_size: float = 0.6) -> DataCenter:
        """添加新的数据中心"""
        dc = DataCenter(room_id, floor_size)
        self.datacenters[room_id] = dc
        return dc

    def add_exit_distance(self, from_room: str, from_exit: str, 
                         to_room: str, to_exit: str, distance: float):
        """添加机房出口间的距离"""
        self.exit_distances.append(ExitDistance(
            from_room=from_room,
            from_exit=from_exit,
            to_room=to_room,
            to_exit=to_exit,
            distance=distance
        ))
        # 添加反向距离
        self.exit_distances.append(ExitDistance(
            from_room=to_room,
            from_exit=to_exit,
            to_room=from_room,
            to_exit=from_exit,
            distance=distance
        ))

def format_conduit_info(path_info: CablePathInfo, source_dc: DataCenter, target_dc: Optional[DataCenter] = None) -> str:
    """格式化线槽使用信息"""
    if path_info.path_type == 'same_cabinet':
        return '不需要'
    
    if path_info.path_type == 'direct':
        return '直连'
    
    elif path_info.path_type == 'conduit':
        return f'纵向线槽({path_info.source_conduit_x}, -)'
    
    elif path_info.path_type == 'cross_room':
        # 使用路径信息中存储的线槽
        source_info = f'源机房纵向线槽({path_info.source_conduit_x}, -)' if path_info.source_conduit_x else '源机房直连'
        target_info = f'目标机房纵向线槽({path_info.target_conduit_x}, -)' if path_info.target_conduit_x else '目标机房直连'
        return f'{source_info} -> {target_info}'
    
    return '未知'

def process_cable_calculations(input_file: str, output_file: str, 
                             exits_config_file: str, conduits_file: str):
    """处理Excel输入文件的所有sheet并生成结果"""
    # 读取配置文件
    exits_df = pd.read_excel(exits_config_file)
    conduits_df = pd.read_excel(conduits_file)
    
    # 读取所有sheet
    excel_file = pd.ExcelFile(input_file)
    sheet_names = excel_file.sheet_names
    
    # 创建ExcelWriter对象来写入多个sheet
    with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
        # 处理每个sheet
        for sheet_name in sheet_names:
            print(f"Processing sheet: {sheet_name}")
            
            # 读取当前sheet
            df = pd.read_excel(input_file, sheet_name=sheet_name)
            
            # 创建映射后的DataFrame
            mapped_df = pd.DataFrame({
                '源机房': df['源机房'],
                '源设备': df['Source Device'],
                '源设备坐标X': df['源设备坐标X'],
                '源设备坐标Y': df['源设备坐标Y'],
                '源设备U位': df['Source U位'],
                '目标机房': df['目标机房'],
                '目标设备': df['Destination Device'],
                '目标设备坐标X': df['目标设备坐标X'],
                '目标设备坐标Y': df['目标设备坐标Y'],
                '目标设备U位': df['Destination U位']
            })
            
            # 创建数据中心网络
            network = DataCenterNetwork()
            
            # 获取所有可能的机房ID
            room_ids = pd.concat([
                mapped_df['源机房'], 
                mapped_df['目标机房'],
                exits_df['源机房'],
                exits_df['目标机房'],
                conduits_df['机房']
            ]).unique()
            
            # 为每个机房创建DataCenter实例
            for room_id in room_ids:
                if pd.notna(room_id):
                    network.add_datacenter(str(room_id))
            
            # 设置各机房的纵向线槽
            for _, row in conduits_df.iterrows():
                room_id = str(row['机房'])
                if room_id not in network.datacenters:
                    network.add_datacenter(room_id)
                network.datacenters[room_id].add_vertical_conduit(
                    int(row['纵向线槽坐标X'])
                )
            
            # 设置出口距离和出口位置
            for _, row in exits_df.iterrows():
                source_room = str(row['源机房'])
                target_room = str(row['目标机房'])
                
                if source_room not in network.datacenters:
                    network.add_datacenter(source_room)
                if target_room not in network.datacenters:
                    network.add_datacenter(target_room)
                
                network.add_exit_distance(
                    source_room,
                    str(row['源出口']),
                    target_room,
                    str(row['目标出口']),
                    float(row['距离(米)'])
                )
                
                # 确保坐标被转换为整数
                if pd.notna(row['源出口坐标X']) and pd.notna(row['源出口坐标Y']):
                    # 检查坐标是否为数字类型，如果不是则忽略
                    try:
                        source_x = int(row['源出口坐标X'])
                        source_y = int(row['源出口坐标Y'])
                        network.datacenters[source_room].add_room_exit(
                            source_x,
                            source_y,
                            str(row['源出口'])
                        )
                    except (ValueError, TypeError):
                        print(f"Warning: Invalid coordinates for exit {row['源出口']} in room {source_room}")
                
                if pd.notna(row['目标出口坐标X']) and pd.notna(row['目标出口坐标Y']):
                    # 检查坐标是否为数字类型，如果不是则忽略
                    try:
                        target_x = int(row['目标出口坐标X'])
                        target_y = int(row['目标出口坐标Y'])
                        network.datacenters[target_room].add_room_exit(
                            target_x,
                            target_y,
                            str(row['目标出口'])
                        )
                    except (ValueError, TypeError):
                        print(f"Warning: Invalid coordinates for exit {row['目标出口']} in room {target_room}")
            
            # 为每个数据中心实例分配exit_distances
            for dc in network.datacenters.values():
                dc.exit_distances = network.exit_distances
            
            # 从设备列表添加设备
            for _, row in mapped_df.iterrows():
                source_room = str(row['源机房'])
                target_room = str(row['目标机房'])
                
                if source_room not in network.datacenters:
                    network.add_datacenter(source_room)
                if target_room not in network.datacenters:
                    network.add_datacenter(target_room)
                
                # 确保坐标和U位是整数
                try:
                    network.datacenters[source_room].add_device(
                        str(row['源设备']),
                        int(row['源设备坐标X']),
                        int(row['源设备坐标Y']),
                        int(row['源设备U位'])
                    )
                except (ValueError, TypeError):
                    print(f"Warning: Invalid data for source device {row['源设备']}")
                    continue
                
                try:
                    network.datacenters[target_room].add_device(
                        str(row['目标设备']),
                        int(row['目标设备坐标X']),
                        int(row['目标设备坐标Y']),
                        int(row['目标设备U位'])
                    )
                except (ValueError, TypeError):
                    print(f"Warning: Invalid data for target device {row['目标设备']}")
                    continue
            
            # 处理每一行计算布线信息
            results = []
            for index, row in mapped_df.iterrows():
                source_room = str(row['源机房'])
                target_room = str(row['目标机房'])
                source_device = str(row['源设备'])
                target_device = str(row['目标设备'])
                
                try:
                    if source_room not in network.datacenters:
                        raise ValueError(f"Source room {source_room} not found in network")
                    if target_room not in network.datacenters:
                        raise ValueError(f"Target room {target_room} not found in network")
                    
                    target_dc = None if source_room == target_room else network.datacenters[target_room]
                    path_info = network.datacenters[source_room].calculate_cable_length(
                        source_device, target_device, target_dc)
                    
                    detailed_path = path_info.get_detailed_path(
                        network.datacenters[source_room].config['is_top_routing']
                    )
                    
                    conduit_info = format_conduit_info(
                        path_info, 
                        network.datacenters[source_room],
                        target_dc
                    )
                    
                    # 使用df.iloc[index]来获取原始数据
                    original_row = df.iloc[index]
                    
                    result_dict = {
                        'Source Device': row['源设备'],
                        'Source locations': original_row['Source locations'],
                        'Source U位': row['源设备U位'],
                        '源机房': source_room,
                        '源设备坐标X': path_info.source_coords[0],
                        '源设备坐标Y': path_info.source_coords[1],
                        'Source Port': original_row['Source Port'],
                        'Source Interface': original_row['Source Interface'],
                        'Destination Device': row['目标设备'],
                        'Destination locations': original_row['Destination locations'],
                        'Destination U位': row['目标设备U位'],
                        '目标机房': target_room,
                        '目标设备坐标X': path_info.target_coords[0],
                        '目标设备坐标Y': path_info.target_coords[1],
                        'Destination Port': original_row['Destination Port'],
                        'Destination Interface': original_row['Destination Interface'],
                        '总线缆长度(米)': round(path_info.total_length, 2),
                        '路径类型': path_info.path_type,
                        '使用的线槽': conduit_info,
                        '详细路径': detailed_path,
                        '水平距离(米)': round(path_info.horizontal_distance, 2),
                        '垂直距离1(米)': round(path_info.vertical_distance1, 2),
                        '垂直距离2(米)': round(path_info.vertical_distance2, 2),
                        '线槽垂直距离(米)': round(path_info.conduit_vertical_distance, 2),
                        '机房间距离(米)': round(path_info.room_distance, 2) if path_info.room_distance else 0
                    }
                    
                    # 添加跨机房时使用的出口信息
                    if path_info.path_type == 'cross_room':
                        result_dict['源机房出口'] = path_info.source_exit
                        result_dict['目标机房入口'] = path_info.target_exit
                    
                    results.append(result_dict)
                except Exception as e:
                    print(f"Error processing row in sheet {sheet_name}: Source={source_device}, Target={target_device}, Error={str(e)}")
                    results.append({
                        'Source Device': row['源设备'],
                        'Destination Device': row['目标设备'],
                        '源机房': source_room,
                        '目标机房': target_room,
                        '错误信息': str(e)
                    })
            
            # 将当前sheet的结果保存到对应的sheet中
            pd.DataFrame(results).to_excel(writer, sheet_name=sheet_name, index=False)
            print(f"Completed processing sheet: {sheet_name}")

if __name__ == "__main__":
    input_file = "topology_256_servers-updated.xlsx"
    exits_config_file = "exits_config.xlsx"
    conduits_file = "conduits_config.xlsx"
    output_file = "cable_length_results.xlsx"
    process_cable_calculations(input_file, output_file, exits_config_file, conduits_file)
			

