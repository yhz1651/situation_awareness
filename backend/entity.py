'''
entity.py
实体类
'''
from map import Map
import math

class BattlefieldEntity:
    def __init__(self, name, enemy, location, policy, temperature, environment, previous_location=None, strength=100, attack_range=50, max_move_distance=10, chaos_g=0, chaos_h=0):
        self.name = name # 名称
        self.enemy = enemy # 敌方/友方
        self.strength = strength # 战力
        self.attack_range = attack_range # 攻击范围
        self.temperature = temperature # 温度
        self.environment = environment # 环境
        if isinstance(location, dict):
            self.location = Map(location['longitude'], location['latitude'], location.get('altitude', 0))
        else:
            self.location = location # 坐标：经度、纬度、高度
        self.chaos_g = chaos_g # 全局混乱度
        self.chaos_h = chaos_h # 局部混乱度
        self.max_move_distance = max_move_distance # 最大移动距离
        self.policy = policy # 移动策略
        self.previous_location = previous_location # 上一个时间戳的坐标

    def get_name(self):
        return self.name

    def get_strength(self):
        return self.strength

    def get_attack_range(self):
        return self.attack_range

    def get_temperature(self):
        return self.temperature

    def get_environment(self):
        return self.environment

    def get_location(self):
        return self.location.get_coordinates()

    def set_location(self, longitude, latitude):
        self.previous_location = self.location
        self.location.set_coordinates(longitude, latitude)

    def get_altitude(self):
        return self.location.get_altitude()

    def set_altitude(self, altitude):
        self.location.set_altitude(altitude)

    def is_in_attack_range(self, target_entity):
        lat1, lon1 = self.get_location()
        lat2, lon2 = target_entity.get_location()
        
        # Haversine formula to calculate distance
        R = 6371.0  # Earth radius in kilometers

        dlat = math.radians(lat2 - lat1)
        dlon = math.radians(lon2 - lon1)
        a = math.sin(dlat / 2) ** 2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2) ** 2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        distance = R * c

        return distance <= self.attack_range

    def entities_in_attack_range(self, all_entities):
        entities_in_range = []
        for entity in all_entities:
            if entity != self and self.is_in_attack_range(entity):
                entities_in_range.append(entity)
        return entities_in_range

    def get_category(self):
        return "Unknown"

    def to_dict(self): # 转换成字典
        return {
            "category": self.get_category(),
            "name": self.name,
            "enemy": self.enemy,
            # "visible": self.visible,
            "location": {
                "longitude": self.location.longitude,
                "latitude": self.location.latitude,
                "altitude": self.location.altitude,
            },
            "policy": self.policy,
            "previous_location": {
                "longitude": self.previous_location.longitude,
                "latitude": self.previous_location.latitude,
                "altitude": self.previous_location.altitude,
            } if self.previous_location else None,
            "temperature": self.temperature,
            "environment": self.environment,
        }

# 坦克类
class Tank(BattlefieldEntity):
    def __init__(self, name, enemy, location, policy, temperature, environment, previous_location=None):
        super().__init__(name=name, enemy=enemy, strength=100, attack_range=3, location=location, policy=policy, max_move_distance=50, temperature=temperature, environment=environment, previous_location=previous_location)
    def get_category(self):
        return "Tank"

# 士兵类
class Soldier(BattlefieldEntity):
    def __init__(self, name, enemy, location, policy, temperature, environment, previous_location=None):
        super().__init__(name=name, enemy=enemy, strength=10, attack_range=0.5, location=location, policy=policy, max_move_distance=20, temperature=temperature, environment=environment, previous_location=previous_location)
    def get_category(self):
        return "Soldier"

# 直升机类
class Helicopter(BattlefieldEntity):
    def __init__(self, name, enemy, location, policy, temperature, environment, previous_location=None):
        super().__init__(name=name, enemy=enemy, strength=50, attack_range=8, location=location, policy=policy, max_move_distance=500, temperature=temperature, environment=environment, previous_location=previous_location)
    def get_category(self):
        return "Helicopter"

# 战斗机类
class FighterJet(BattlefieldEntity):
    def __init__(self, name, enemy, location, policy, temperature, environment, previous_location=None):
        super().__init__(name=name, enemy=enemy, strength=200, attack_range=50, location=location, policy=policy, max_move_distance=1500, temperature=temperature, environment=environment, previous_location=previous_location)
    def get_category(self):
        return "FighterJet"

# 炮兵类
class Artillery(BattlefieldEntity):
    def __init__(self, name, enemy, location, policy, temperature, environment, previous_location=None):
        super().__init__(name=name, enemy=enemy, strength=50, attack_range=30, location=location, policy=policy, max_move_distance=10, temperature=temperature, environment=environment, previous_location=previous_location)
    def get_category(self):
        return "Artillery"

# 步兵战车类
class InfantryFightingVehicle(BattlefieldEntity):
    def __init__(self, name, enemy, location, policy, temperature, environment, previous_location=None):
        super().__init__(name=name, enemy=enemy, strength=60, attack_range=2, location=location, policy=policy, max_move_distance=50, temperature=temperature, environment=environment, previous_location=previous_location)
    def get_category(self):
        return "InfantryFightingVehicle"

# 无人机类
class UAV(BattlefieldEntity):
    def __init__(self, name, enemy, location, policy, temperature, environment, previous_location=None):
        super().__init__(name=name, enemy=enemy, strength=40, attack_range=15, location=location, policy=policy, max_move_distance=1000, temperature=temperature, environment=environment, previous_location=previous_location)
    def get_category(self):
        return "UAV"

# 装甲车类
class ArmoredVehicles(BattlefieldEntity):
    def __init__(self, name, enemy, location, policy, temperature, environment, previous_location=None):
        super().__init__(name=name, enemy=enemy, strength=80, attack_range=4, location=location, policy=policy, max_move_distance=60, temperature=temperature, environment=environment, previous_location=previous_location)
    def get_category(self):
        return "ArmoredVehicles"

# 导弹运载器类
class MissileVehicle(BattlefieldEntity):
    def __init__(self, name, enemy, location, policy, temperature, environment, previous_location=None):
        super().__init__(name=name, enemy=enemy, strength=120, attack_range=40, location=location, policy=policy, max_move_distance=30, temperature=temperature, environment=environment, previous_location=previous_location)
    def get_category(self):
        return "MissileVehicle"

# 车辆类
class Vehicles(BattlefieldEntity):
    def __init__(self, name, enemy, location, policy, temperature, environment, previous_location=None):
        super().__init__(name=name, enemy=enemy, strength=20, attack_range=1, location=location, policy=policy, max_move_distance=80, temperature=temperature, environment=environment, previous_location=previous_location)
    def get_category(self):
        return "Vehicles"

# 飞机类
class Airplane(BattlefieldEntity):
    def __init__(self, name, enemy, location, policy, temperature, environment, previous_location=None):
        super().__init__(name=name, enemy=enemy, strength=150, attack_range=60, location=location, policy=policy, max_move_distance=2000, temperature=temperature, environment=environment, previous_location=previous_location)
    def get_category(self):
        return "Airplane"

# 伪装网类
class CamouflageNet(BattlefieldEntity):
    def __init__(self, name, enemy, location, policy, temperature, environment, previous_location=None):
        super().__init__(name=name, enemy=enemy, strength=150, attack_range=60, location=location, policy=policy, max_move_distance=2000, temperature=temperature, environment=environment, previous_location=previous_location)
    def get_category(self):
        return "CamouflageNet"
    
if __name__ == "__main__":
    # 测试用例
    tank = Tank(
        name="Tank A",
        enemy="Enemy A",
        location=Map(longitude=0, latitude=0, altitude=0),
        policy="aggressive",
        temperature=25,
        environment="desert"
    )

    soldier = Soldier(
        name="Soldier B",
        enemy="Enemy B",
        location=Map(longitude=1, latitude=1, altitude=0),
        policy="defensive",
        temperature=25,
        environment="desert"
    )

    helicopter = Helicopter(
        name="Helicopter C",
        enemy="Enemy C",
        location=Map(longitude=2, latitude=2, altitude=0),
        policy="neutral",
        temperature=25,
        environment="forest"
    )

    # 获取各实体的名称和类别
    print(f"{tank.get_name()} is a {tank.get_category()}")
    print(f"{soldier.get_name()} is a {soldier.get_category()}")
    print(f"{helicopter.get_name()} is a {helicopter.get_category()}")

    # 获取各实体的坐标
    print(f"Tank location: {tank.get_location()}")
    print(f"Soldier location: {soldier.get_location()}")
    print(f"Helicopter location: {helicopter.get_location()}")

    # 移动实体并打印新位置
    tank.set_location(5, 5)
    print(f"Tank new location: {tank.get_location()}")

    # 检查实体是否在攻击范围内
    print(f"Is soldier in tank's attack range? {tank.is_in_attack_range(soldier)}")
    print(f"Is helicopter in tank's attack range? {tank.is_in_attack_range(helicopter)}")

    # 获取在攻击范围内的所有实体
    all_entities = [tank, soldier, helicopter]
    print(f"Entities in tank's attack range: {[entity.get_name() for entity in tank.entities_in_attack_range(all_entities)]}")
