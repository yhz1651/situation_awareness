from map import Map
from entity import Tank, Soldier, Helicopter, FighterJet, Artillery, InfantryFightingVehicle, UAV
import json, random, math
import datetime
from datetime import timedelta
from dateutil.relativedelta import relativedelta


# 阈值，相邻两个时间步之间同一个实体的经纬度差值不超过该值
max_lat_lon_difference = 2.0
# 相邻两个时间步之间的时间差不超过该值（以分钟为单位）
max_time_difference_minutes = 60
# 高度的最大变化值
max_altitude_difference = 10.0

#全局字典初始化
random_moves_per_entity = {}

# 全局变量存储日志条目
log_entries = []

# 日志条目数量
log_count = 0

# 定义乌克兰的经纬度和海拔范围
LONGITUDE_MIN = 22.0
LONGITUDE_MAX = 40.0
LATITUDE_MIN = 44.0
LATITUDE_MAX = 52.0
ALTITUDE_MIN = 0
ALTITUDE_MAX = 500  # 假设乌克兰的海拔范围为 0 到 500 米

# 定义高斯分布的均值和标准差
LONGITUDE_MEAN = (LONGITUDE_MIN + LONGITUDE_MAX) / 2
LONGITUDE_STDDEV = (LONGITUDE_MAX - LONGITUDE_MIN) / 6
LATITUDE_MEAN = (LATITUDE_MIN + LATITUDE_MAX) / 2
LATITUDE_STDDEV = (LATITUDE_MAX - LATITUDE_MIN) / 6

# Policy的种类
POLICIES = ["near_friend", "far_from_friend", "near_enemy", "far_from_enemy"]

# 环境的种类
ENVIRONMENTS = ["desert", "forest", "urban", "mountain"]

# 生成随机温度
def generate_random_temperature():
    return random.uniform(-20, 50)  # 温度范围从 -20 到 50 摄氏度

def to_dict(entity):
    return {
        "category": entity.get_category(),
        "name": entity.name,
        "enemy": entity.enemy,
        "location": {
            "longitude": entity.location.longitude,
            "latitude": entity.location.latitude,
            "altitude": entity.location.altitude,
        },
        "policy": entity.policy,
        "temperature": entity.temperature,
        "environment": entity.environment,
        "previous_location": {
            "longitude": entity.previous_location.longitude,
            "latitude": entity.previous_location.latitude,
            "altitude": entity.previous_location.altitude,
        } if entity.previous_location else None
    }

# 计算两个实体之间的实际距离
def calculate_distance(entity1, entity2):
    lat1, lon1 = entity1.location.latitude, entity1.location.longitude
    lat2, lon2 = entity2.location.latitude, entity2.location.longitude
    # Using Haversine formula to calculate distance between two points on Earth
    R = 6371.0  # Earth radius in kilometers
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat / 2) ** 2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    distance = R * c
    return distance

def find_nearest_entity(entity, entities, is_enemy=True):
    # 使用列表推导式，同时根据是否敌对和是否为当前实体来过滤实体列表
    if is_enemy:
        filtered_entities = [e for e in entities if e.enemy != entity.enemy and e.name != entity.name]
    else:
        filtered_entities = [e for e in entities if e.enemy == entity.enemy and e.name != entity.name]

    if not filtered_entities:
        return None  # 如果没有找到符合条件的其他实体，则返回 None

    # 使用计算距离的 lambda 函数作为 key，找到最近的实体
    nearest_entity = min(filtered_entities, key=lambda e: calculate_distance(entity, e))
    return nearest_entity

# 决定移动的方向
def determine_direction(entity, target_entity):
    lat_diff = target_entity.location.latitude - entity.location.latitude
    lon_diff = target_entity.location.longitude - entity.location.longitude
    angle = math.atan2(lon_diff, lat_diff)  # Calculate angle in radians
    return angle

# 移动平均平滑
def moving_average(location_history, window_size=3):
    if len(location_history) < window_size:
        return location_history[-1]  # 如果历史记录不足窗口大小，返回最后一个位置
    
    avg_lat = sum([loc.latitude for loc in location_history[-window_size:]]) / window_size
    avg_lon = sum([loc.longitude for loc in location_history[-window_size:]]) / window_size
    avg_alt = sum([loc.altitude for loc in location_history[-window_size:]]) / window_size
    
    return Map(avg_lon, avg_lat, avg_alt)

# 找到最近的实体（敌方或友方），确定方向，按策略移动 
def move_entity(entity, direction, policy, entities_data, current_time, location_history, random_move_probability=0.1):
    global random_moves_per_entity
    global log_count
    scale_num = 1000.0 # 
    ran_scale = 0.01 # 随机扰动项的大小 (0.0 ~ 2.0)
    max_move_distance = min(entity.max_move_distance / scale_num, 0.1)
    # 随机决定是否进行随机移动
    # 1%的概率反向移动（为了使异常显现明显）
    if random.random() < random_move_probability:
        # 随机移动，经纬度1度约等于110km，时间戳间隔是1天
        # max_move_distance = entity.max_move_distance / scale_num
        
        if entity.name in random_moves_per_entity:
            random_moves_per_entity[entity.name] += 1
        else:
            random_moves_per_entity[entity.name] = 1
            
        # print(f"entity_name: {entity.name}, current_time:{current_time}")
        
        # 将实体的基本信息存储到日志字典
        log_entry = {
            "entity": entity.name,
            "current_time": current_time.strftime("%Y-%m-%d %H:%M:%S"),  # 格式化时间
            "policy": entity.policy,
            "original_location": {
                "longitude": entity.location.longitude,
                "latitude": entity.location.latitude
            }
        }
        log_entries.append(log_entry)
        log_count += 1
        
        if policy == "near_friend":
            # 远离最近友方实体移动
            nearest_friend = find_nearest_entity(entity, entities_data, is_enemy=False)
            if nearest_friend:
                direction = determine_direction(entity, nearest_friend) + math.pi  # 反向移动
        elif policy == "far_from_friend":
            # 向最近友方实体移动
            nearest_friend = find_nearest_entity(entity, entities_data, is_enemy=False)
            if nearest_friend:
                direction = determine_direction(entity, nearest_friend)
        elif policy == "near_enemy":
            # 远离最近敌方实体移动
            nearest_enemy = find_nearest_entity(entity, entities_data, is_enemy=True)
            if nearest_enemy:
                direction = determine_direction(entity, nearest_enemy) + math.pi  # 反向移动
        elif policy == "far_from_enemy":
            # 向最近敌方实体移动
            nearest_enemy = find_nearest_entity(entity, entities_data, is_enemy=True)
            if nearest_enemy:
                direction = determine_direction(entity, nearest_enemy)
        
        lat_diff = math.cos(direction) * random.uniform(0, max_move_distance)
        lon_diff = math.sin(direction) * random.uniform(0, max_move_distance)
        lon_diff += random.uniform(-ran_scale, ran_scale) # 增加随机扰动项，避免出现直线
        altitude_diff = random.uniform(-max_altitude_difference, max_altitude_difference)
        
        # 计算新位置
        new_longitude = entity.location.longitude + lon_diff
        new_latitude = entity.location.latitude + lat_diff 
        new_altitude = entity.location.altitude + altitude_diff

        # 限制经纬度范围在乌克兰
        new_longitude = max(LONGITUDE_MIN, min(LONGITUDE_MAX, new_longitude)) # 限制经度范围
        new_latitude = max(LATITUDE_MIN, min(LATITUDE_MAX, new_latitude)) # 限制纬度范围

        # 限制海拔高度
        new_altitude = max(ALTITUDE_MIN, min(ALTITUDE_MAX, new_altitude))

        new_location = Map(new_longitude, new_latitude, new_altitude)
        entity.previous_location = entity.location  # 更新 previous_location 属性
        entity.location = new_location
    else: # 正向移动
        # 根据策略实现不同的移动方式
        if policy == "near_friend":
            # 向最近友方实体移动
            nearest_friend = find_nearest_entity(entity, entities_data, is_enemy=False)
            if nearest_friend:
                direction = determine_direction(entity, nearest_friend)
        elif policy == "far_from_friend":
            # 远离最近友方实体移动
            nearest_friend = find_nearest_entity(entity, entities_data, is_enemy=False)
            if nearest_friend:
                direction = determine_direction(entity, nearest_friend) + math.pi  # 反向移动
        elif policy == "near_enemy":
            # 向最近敌方实体移动
            nearest_enemy = find_nearest_entity(entity, entities_data, is_enemy=True)
            if nearest_enemy:
                direction = determine_direction(entity, nearest_enemy)
        elif policy == "far_from_enemy":
            # 远离最近敌方实体移动
            nearest_enemy = find_nearest_entity(entity, entities_data, is_enemy=True)
            if nearest_enemy:
                direction = determine_direction(entity, nearest_enemy) + math.pi  # 反向移动

        
        
        # Move the entity in the specified direction by a random amount
        lat_diff = math.cos(direction) * random.uniform(0, max_move_distance)
        lon_diff = math.sin(direction) * random.uniform(0, max_move_distance)
        lon_diff += random.uniform(-ran_scale, ran_scale) # 增加随机扰动项，避免出现直线
        altitude_diff = random.uniform(-max_altitude_difference, max_altitude_difference)
        
        # 计算并限制新位置在乌克兰
        new_longitude = max(LONGITUDE_MIN, min(LONGITUDE_MAX, entity.location.longitude + lon_diff))
        new_latitude = max(LATITUDE_MIN, min(LATITUDE_MAX, entity.location.latitude + lat_diff))
        new_altitude = max(ALTITUDE_MIN, min(ALTITUDE_MAX, entity.location.altitude + altitude_diff))

        new_location = Map(new_longitude, new_latitude, new_altitude)
        entity.previous_location = entity.location  # 更新 previous_location 属性
        entity.location = new_location

    # location_history.append(entity.location)
    # entity.location = moving_average(location_history)
    

def generate_entities(scale, advantage, current_time, prev_entities_data=None, location_histories=None):
    if location_histories is None:
        location_histories = {}
    
    entities_data = []
    entity_types = [Tank, Soldier, Helicopter, FighterJet, Artillery, InfantryFightingVehicle, UAV] # 实体类型
    scale_large = scale == "large_scale"

    if advantage == "enemy_advantage":
        enemy_ratio = 0.7
        self_ratio = 0.3
    else:
        enemy_ratio = 0.3
        self_ratio = 0.7
    
    if prev_entities_data is None:
        # 第一次生成实体，随机生成初始位置
        num_entities = 200 if scale_large else 50
        num_enemy = int(num_entities * enemy_ratio)
        num_self = num_entities - num_enemy

        # 定义东北和西南的经纬度范围
        NE_LONGITUDE_MIN = 32.0  # 东北方向的最小经度
        NE_LONGITUDE_MAX = 40.0  # 东北方向的最大经度
        NE_LATITUDE_MIN = 48.0  # 东北方向的最小纬度
        NE_LATITUDE_MAX = 52.0  # 东北方向的最大纬度
        
        SW_LONGITUDE_MIN = 22.0  # 西南方向的最小经度
        SW_LONGITUDE_MAX = 31.0  # 西南方向的最大经度
        SW_LATITUDE_MIN = 44.0  # 西南方向的最小纬度
        SW_LATITUDE_MAX = 48.0  # 西南方向的最大纬度

        BUFFER_DISTANCE = 100.0  # 中间缓冲区的距离（以公里为单位）  
        
        for i in range(num_entities):
            name = f"Entity{i}"
            enemy = i < num_enemy  # 根据敌方和我方实体数量确定是否为敌方
            policy = random.choice(POLICIES)  # 随机选择策略
            temperature = generate_random_temperature()  # 生成随机温度
            environment = random.choice(ENVIRONMENTS)  # 随机选择环境
            
            # 生成实体         
            entity_type = random.choices(entity_types, k=1, weights=[3, 1, 2, 3, 2, 2, 3])[0]
            
            if enemy:
                # 敌军从西南方向生成
                longitude = random.uniform(SW_LONGITUDE_MIN, SW_LONGITUDE_MAX)
                latitude = random.uniform(SW_LATITUDE_MIN, SW_LATITUDE_MAX)
            else:
                # 我军从东北方向生成
                longitude = random.uniform(NE_LONGITUDE_MIN, NE_LONGITUDE_MAX)
                latitude = random.uniform(NE_LATITUDE_MIN, NE_LATITUDE_MAX)
                
            # # 生成符合实际的经纬度和海拔高度，使用高斯分布
            # longitude = min(max(random.gauss(LONGITUDE_MEAN, LONGITUDE_STDDEV), LONGITUDE_MIN - 5), LONGITUDE_MAX + 5)
            # latitude = min(max(random.gauss(LATITUDE_MEAN, LATITUDE_STDDEV), LATITUDE_MIN - 5), LATITUDE_MAX + 5)
            altitude = random.uniform(ALTITUDE_MIN, ALTITUDE_MAX)  # 海拔高度限制在0到500米
            
            location = Map(longitude, latitude, altitude)
            entity = entity_type(name=name, enemy=enemy, location=location, policy=policy, temperature=temperature, environment=environment)
            entities_data.append(entity)
            location_histories[entity.name] = [location]

    else:
        # 直接使用前一次生成的位置信息
        entities_data = prev_entities_data
        for entity in entities_data:
            direction = random.uniform(0, 2 * math.pi)  # 随机方向
            move_entity(entity, direction, entity.policy, entities_data, current_time, location_histories[entity.name])
            entity.temperature = generate_random_temperature()  # 每个时间步改变温度
            entity.environment = random.choice(ENVIRONMENTS)  # 每个时间步改变环境

    return entities_data, location_histories

def generate_json_data_multiple_time_steps(num_time_steps, conditions):
    json_data_list = []
    
    # 初始化上一个时间戳为当前时间
    last_time = datetime.datetime.now() - timedelta(days=365, hours=random.randint(0, 23), minutes=random.randint(0, 59)) # 前一年开始

    for scale, advantage in conditions:
        # 初始化实体数据
        entities_data = None
        location_histories = {}
        for _ in range(num_time_steps):
            # Generate next time step
            days_later = 1 # 每隔1天采样1次
            
            current_time = last_time + relativedelta(days=days_later)
            time_str = current_time.strftime("%Y-%m-%d %H:%M:%S")
            
            # Update last_time to the current time for the next iteration
            last_time = current_time
            
            # Generate entities for the current time step
            current_entities_data, location_histories = generate_entities(scale, advantage, current_time, entities_data, location_histories)
            entities_data = current_entities_data
            
            # Prepare json data for the current time step
            json_data = {
                "time": time_str,
                "entities": [to_dict(entity) for entity in current_entities_data]
            }
            json_data_list.append(json_data)
    
    return json_data_list

def save_json_to_file(json_data, file_path):
    with open(file_path, "w") as file:
        json.dump(json_data, file)

def read_and_extract_entities(file_path):
    with open(file_path, "r") as file:
        json_data = json.load(file)

    all_entities_by_time = []

    for time_data in json_data:
        time = time_data["time"]
        entities_at_time = []
        for entity_data in time_data["entities"]:
            category = entity_data["category"]
            name = entity_data["name"]
            enemy = entity_data["enemy"]
            location_data = entity_data["location"]
            location = Map(location_data["longitude"], location_data["latitude"], location_data["altitude"])
            previous_location_data = entity_data.get("previous_location")
            previous_location = Map(previous_location_data["longitude"], previous_location_data["latitude"], previous_location_data["altitude"]) if previous_location_data else None
            policy = entity_data.get("policy")
            temperature = entity_data.get("temperature")
            environment = entity_data.get("environment")

            if category == "Tank":
                entity = Tank(name=name, enemy=enemy, location=location, policy=policy, temperature=temperature, environment=environment, previous_location=previous_location)
            elif category == "Soldier":
                entity = Soldier(name=name, enemy=enemy, location=location, policy=policy, temperature=temperature, environment=environment, previous_location=previous_location)
            elif category == "Helicopter":
                entity = Helicopter(name=name, enemy=enemy, location=location, policy=policy, temperature=temperature, environment=environment, previous_location=previous_location)
            elif category == "FighterJet":
                entity = FighterJet(name=name, enemy=enemy, location=location, policy=policy, temperature=temperature, environment=environment, previous_location=previous_location)
            elif category == "Artillery":
                entity = Artillery(name=name, enemy=enemy, location=location, policy=policy, temperature=temperature, environment=environment, previous_location=previous_location)
            elif category == "InfantryFightingVehicle":
                entity = InfantryFightingVehicle(name=name, enemy=enemy, location=location, policy=policy, temperature=temperature, environment=environment, previous_location=previous_location)
            elif category == "UAV":
                entity = UAV(name=name, enemy=enemy, location=location, policy=policy, temperature=temperature, environment=environment, previous_location=previous_location)
            else:
                continue

            entities_at_time.append(entity)

        all_entities_by_time.append({"time": time, "entities": entities_at_time})

    return all_entities_by_time

# 在适当的时刻调用这个函数来将日志写入文件
def save_log_entries_to_file():
    # 按照 entity 排序日志条目
    sorted_log_entries = sorted(log_entries, key=lambda x: x["entity"])  
    with open('entity_movements_log.json', 'w') as file:
        json.dump(sorted_log_entries, file, indent=4)

if __name__ == "__main__":
    # 设置特定的条件和文件名
    scale = "small_scale"
    advantage = "enemy_advantage"
    num_time_steps = 32  # 时间步数
    file_path = "data_test/small_scale_enemy_advantage_1.json"  # 目标文件路径

    # 生成数据
    json_data_list = generate_json_data_multiple_time_steps(num_time_steps, [(scale, advantage)])
    
    save_log_entries_to_file()

    # 保存数据到文件
    save_json_to_file(json_data_list, file_path)
    # print(f"Data with multiple time steps has been written to {file_path}")
    
    # 最后打印每个实体的随机移动次数
    # for entity_name, count in random_moves_per_entity.items():
    #     print(f"{entity_name} triggered random moves {count} times")
        
    # print(f"异常条目数：{log_count}")
    # 定义要存储的数据
    data_to_save = {
        "log_count": log_count
    }
    
    # 指定要写入的文件路径
    file_path = 'log_data.json'

    # 写入数据到 JSON 文件
    with open(file_path, 'w') as file:
        json.dump(data_to_save, file, indent=4)
