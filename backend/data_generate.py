'''
data_generate.py
生成数据
'''
from map import Map
from entity import Tank, Soldier, Helicopter, FighterJet, Artillery, InfantryFightingVehicle, UAV, ArmoredVehicles, MissileVehicle, Vehicles, Airplane, CamouflageNet
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

# 定义经纬度和海拔范围
LONGITUDE_MIN = 120.21
LONGITUDE_MAX = 120.38
LATITUDE_MIN = 29.096
LATITUDE_MAX = 29.1006
ALTITUDE_MIN = 0
ALTITUDE_MAX = 500  # 假设海拔范围为 0 到 500 米

# Policy的种类
POLICIES = ["near_friend", "far_from_friend", "near_enemy", "far_from_enemy"]

# 环境的种类
ENVIRONMENTS = ["land", "ocean", "air"]

# 实体种类
ENTITY_TYPES = [Tank, Soldier, Helicopter, FighterJet, Artillery, InfantryFightingVehicle, UAV, ArmoredVehicles, MissileVehicle, Vehicles, Airplane, CamouflageNet]

# 实体权重，越大表示越多
WEIGHTS=[5, 1, 2, 3, 2, 2, 3, 3, 3, 3, 2, 3]

# 类型和环境的匹配关系
TYPE_MATCH = {
    "Tank": "land",
    "Soldier": "land",
    "Helicopter": "air",
    "FighterJet": "air",
    "Artillery": "land",
    "InfantryFightingVehicle": "land",
    "UAV": "air",
    "ArmoredVehicles": "land",
    "MissileVehicle": "land",
    "Vehicles": "land",
    "Airplane": "air",
    "CamouflageNet": "land"
}

# 大小规模的实体数
LARGE_SCALE = 200
SMALL_SCALE = 50

# 字典转换成对象
def dicts_to_objects(dict_list):
    """
    将字典列表转换为适当的 BattlefieldEntity 子类对象列表
    :param dict_list: 字典列表
    :return: 对象列表
    """
    objects = []
    for entity_dict in dict_list:
        category = entity_dict.get('category')
        
        # 过滤掉不需要的字段，比如 'category'
        filtered_dict = {key: value for key, value in entity_dict.items() if key != 'category'}
        
        # 根据 category 决定实例化哪个子类
        if category == 'Tank':
            obj = Tank(**filtered_dict)
        elif category == 'Soldier':
            obj = Soldier(**filtered_dict)
        elif category == 'Helicopter':
            obj = Helicopter(**filtered_dict)
        elif category == 'FighterJet':
            obj = FighterJet(**filtered_dict)
        elif category == 'Artillery':
            obj = Artillery(**filtered_dict)
        elif category == 'InfantryFightingVehicle':
            obj = InfantryFightingVehicle(**filtered_dict)
        elif category == 'UAV':
            obj = UAV(**filtered_dict)
        elif category == 'ArmoredVehicles':
            obj = ArmoredVehicles(**filtered_dict)
        elif category == 'MissileVehicle':
            obj = MissileVehicle(**filtered_dict)
        elif category == 'Vehicles':
            obj = Vehicles(**filtered_dict)
        elif category == 'Airplane':
            obj = Airplane(**filtered_dict)
        elif category == 'CamouflageNet':
            obj = CamouflageNet(**filtered_dict)    
        else:
            raise ValueError(f"Unknown entity category: {category}")
        
        objects.append(obj)
    
    return objects

# 生成随机温度
def generate_random_temperature():
    return random.uniform(0, 120)  # 温度范围

# 生成环境
def generate_environment(entity_type):
    return TYPE_MATCH[entity_type.__name__]  # 从 TYPE_MATCH 获取对应的环境类型


# 实体转换成对象
def to_dict(entity):
    if isinstance(entity, dict):
        # 如果实体已经是字典，直接返回
        return entity
    else:
        return {
            "category": entity.get_category(),
            "name": entity.name,
            "enemy": entity.enemy,
            "location": {
                "longitude": entity.location['longitude'] if isinstance(entity.location, dict) else entity.location.longitude,
                "latitude": entity.location['latitude'] if isinstance(entity.location, dict) else entity.location.latitude,
                "altitude": entity.location['altitude'] if isinstance(entity.location, dict) else entity.location.altitude,
            },
            "policy": entity.policy,
            "temperature": entity.temperature,
            "environment": entity.environment,
            "previous_location": {
                "longitude": entity.previous_location['longitude'] if isinstance(entity.previous_location, dict) else entity.previous_location.longitude,
                "latitude": entity.previous_location['latitude'] if isinstance(entity.previous_location, dict) else entity.previous_location.latitude,
                "altitude": entity.previous_location['altitude'] if isinstance(entity.previous_location, dict) else entity.previous_location.altitude,
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

# 寻找最近的实体
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

# 移动实体 
def move_entity(entity, direction, policy, entities_data, location_history, random_move_probability=0.2):
    # 如果实体类型是伪装网 CamouflageNet，不进行移动
    if entity.get_category() == 'CamouflageNet':
        entity.previous_location = entity.location  
        return
    
    scale_num = 1000.0 # 
    ran_scale = 0.01 # 随机扰动项的大小 (0.0 ~ 2.0)
    max_move_distance = min(entity.max_move_distance / scale_num, 0.001)
    # 随机决定是否进行随机移动
    # 10%的概率反向移动（为了使异常显现明显）
    if random.random() < random_move_probability:
        # 随机移动，经纬度1度约等于110km，时间戳间隔是1天
        # max_move_distance = entity.max_move_distance / scale_num
        
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
        
        # 计算并限制新位置
        new_longitude = max(LONGITUDE_MIN, min(LONGITUDE_MAX, entity.location.longitude + lon_diff))
        new_latitude = max(LATITUDE_MIN, min(LATITUDE_MAX, entity.location.latitude + lat_diff))
        new_altitude = max(ALTITUDE_MIN, min(ALTITUDE_MAX, entity.location.altitude + altitude_diff))

        new_location = Map(new_longitude, new_latitude, new_altitude)
        entity.previous_location = entity.location  # 更新 previous_location 属性
        entity.location = new_location

    
# 根据指定策略生成实体
def generate_entity_by_policy(name, enemy, entity_type, longitude, latitude, altitude, policy):
    """根据指定策略生成实体"""
    temperature = generate_random_temperature()  # 生成随机温度
    environment = generate_environment(entity_type)
    location = Map(longitude, latitude, altitude)
    
    # 生成实体
    entity = entity_type(
        name=name,
        enemy=enemy,
        location=location,
        policy=policy,
        temperature=temperature,
        environment=environment
    )
    
    return entity

# 生成一个时间戳的实体
def generate_entities(scale, advantage, prev_entities_data=None, location_histories=None):
    if location_histories is None:
        location_histories = {}
    
    entities_data = []
    entity_types = ENTITY_TYPES
    scale_large = scale == "large_scale"

    if advantage == "enemy_advantage":
        enemy_ratio = 0.7
    else:
        enemy_ratio = 0.3
    
    # 设置中间缓冲区（不生成实体）
    buffer_ratio = 0.05  # 中间区域占地图比例
    offset_range = 0.001  # 偏移值范围，用于微调实体位置
    
    # 根据经纬度范围计算缓冲区边界
    longitude_buffer_min = LONGITUDE_MIN + (LONGITUDE_MAX - LONGITUDE_MIN) * (1 - buffer_ratio) / 2
    longitude_buffer_max = LONGITUDE_MIN + (LONGITUDE_MAX - LONGITUDE_MIN) * (1 + buffer_ratio) / 2
    latitude_buffer_min = LATITUDE_MIN + (LATITUDE_MAX - LATITUDE_MIN) * (1 - buffer_ratio) / 2
    latitude_buffer_max = LATITUDE_MIN + (LATITUDE_MAX - LATITUDE_MIN) * (1 + buffer_ratio) / 2

    if prev_entities_data is None:
        # 第一次生成实体，随机生成初始位置
        num_entities = LARGE_SCALE if scale_large else SMALL_SCALE
        num_enemy = int(num_entities * enemy_ratio)
        num_self = num_entities - num_enemy

        for i in range(num_entities):
            name = f"Entity{i}"
            enemy = i < num_enemy  # 根据敌方和我方实体数量确定是否为敌方
            policy = random.choice(POLICIES)  # 随机选择策略
            
            # 生成实体         
            entity_type = random.choices(entity_types, k=1, weights=WEIGHTS)[0]
            
            if enemy:
                # 敌方实体生成在右上方向，排除缓冲区
                longitude = random.uniform(longitude_buffer_max, LONGITUDE_MAX)
                latitude = random.uniform(latitude_buffer_max, LATITUDE_MAX)
            else:
                # 我方实体生成在左下方向，排除缓冲区
                longitude = random.uniform(LONGITUDE_MIN, longitude_buffer_min)
                latitude = random.uniform(LATITUDE_MIN, latitude_buffer_min)
                
            altitude = random.uniform(ALTITUDE_MIN, ALTITUDE_MAX)  # 海拔高度限制在0到500米
            
            # 生成实体
            entity = generate_entity_by_policy(name, enemy, entity_type, longitude, latitude, altitude, policy)
            entities_data.append(entity)
            location_histories[entity.name] = [entity.location]

    else:
        # 直接使用前一次生成的位置信息
        entities_data = prev_entities_data
        for entity in entities_data:
            direction = random.uniform(0, 2 * math.pi)  # 随机方向
            move_entity(entity, direction, entity.policy, entities_data, location_histories[entity.name])
            entity.temperature = generate_random_temperature()  # 每个时间步改变温度

            if entity.get_category() != 'CamouflageNet':
                # 确保实体在指定的区域内（即使在移动后），并加上偏移
                if entity.enemy:
                    # 限制敌方实体在右上区域内，并加上一个小的偏移量
                    entity.location.longitude = max(longitude_buffer_max, min(LONGITUDE_MAX, entity.location.longitude)) + random.uniform(-offset_range, offset_range)
                    entity.location.latitude = max(latitude_buffer_max, min(LATITUDE_MAX, entity.location.latitude)) + random.uniform(-offset_range, offset_range)
                else:
                    # 限制我方实体在左下区域内，并加上一个小的偏移量
                    entity.location.longitude = max(LONGITUDE_MIN, min(longitude_buffer_min, entity.location.longitude)) + random.uniform(-offset_range, offset_range)
                    entity.location.latitude = max(LATITUDE_MIN, min(latitude_buffer_min, entity.location.latitude)) + random.uniform(-offset_range, offset_range)
                
                # 限制海拔高度，并加上一个小的偏移量
                entity.location.altitude = max(ALTITUDE_MIN, min(ALTITUDE_MAX, entity.location.altitude)) + random.uniform(-offset_range, offset_range)
            
            # 更新历史位置
            location_histories[entity.name].append(entity.location)

    return entities_data, location_histories

# 生成多个时间戳的实体
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
            current_entities_data, location_histories = generate_entities(scale, advantage, entities_data, location_histories)
            entities_data = current_entities_data
            
            # Prepare json data for the current time step
            json_data = {
                "time": time_str,
                "entities": [to_dict(entity) for entity in current_entities_data]
            }
            json_data_list.append(json_data)
    
    return json_data_list

# 根据已知的第一个时间戳实体信息，生成后续时间步的实体信息
def generate_json_data_from_initial(initial_entities_data, start_time, num_time_steps, location_histories=None):
    """
    根据已知的第一个时间戳实体信息，生成后续时间步的实体信息。
    
    参数:
    - initial_entities_data: 第一个时间戳的实体数据 (已知实体)
    - start_time: 第一个时间戳，格式为 datetime 类型
    - num_time_steps: 需要生成的时间步数
    - location_histories: 每个实体的位置信息历史（可选）
    
    返回值:
    - json_data_list: 包含每个时间步实体信息的 JSON 数据列表
    """
    if isinstance(initial_entities_data[0], dict):
        initial_entities_data = dicts_to_objects(initial_entities_data)
    elif isinstance(initial_entities_data[0], list):
        initial_entities_data = [entity for sublist in initial_entities_data for entity in sublist]
        
    # 检查当前实体数量，并根据需要生成更多实体
    if len(initial_entities_data) < 50:
        num_needed = 50 - len(initial_entities_data)
        num_friends = num_needed // 2
        num_enemies = num_needed - num_friends
        num_friends_id = len(initial_entities_data) + 1
        num_enemies_id = num_friends_id + num_friends
        # 生成我方和敌方实体
        
        initial_entities_data.extend(create_entity(num_friends, num_friends_id, enemy=False))
        initial_entities_data.extend(create_entity(num_enemies, num_enemies_id, enemy=True))

    # print(type(initial_entities_data), initial_entities_data)
    json_data_list = []

    # 初始化上一个时间戳为传入的起始时间
    last_time = start_time

    # 如果没有提供历史位置数据，则初始化一个空字典
    if location_histories is None:
        location_histories = {entity.name: [entity.location] for entity in initial_entities_data}

    # 设置中间缓冲区（不生成实体）
    buffer_ratio = 0.2  # 中间区域占地图比例 (20%)
    
    # 根据经纬度范围计算缓冲区边界
    longitude_buffer_min = LONGITUDE_MIN + (LONGITUDE_MAX - LONGITUDE_MIN) * (1 - buffer_ratio) / 2
    longitude_buffer_max = LONGITUDE_MIN + (LONGITUDE_MAX - LONGITUDE_MIN) * (1 + buffer_ratio) / 2
    latitude_buffer_min = LATITUDE_MIN + (LATITUDE_MAX - LATITUDE_MIN) * (1 - buffer_ratio) / 2
    latitude_buffer_max = LATITUDE_MIN + (LATITUDE_MAX - LATITUDE_MIN) * (1 + buffer_ratio) / 2

    # 将第一个时间步的数据加入到 JSON 数据中
    time_str = last_time.strftime("%Y-%m-%d %H:%M:%S")
    json_data_list.append({
        "time": time_str,
        "entities": [to_dict(entity) for entity in initial_entities_data]  # 使用 to_dict 方法来转换实体
    })

    # 当前的实体数据初始化为已知的初始数据
    entities_data = initial_entities_data

    # 生成后续时间步数据
    for _ in range(1, num_time_steps):
        days_later = 1  # 每隔1天采样1次
        current_time = last_time + relativedelta(days=days_later)
        time_str = current_time.strftime("%Y-%m-%d %H:%M:%S")

        # 更新实体位置信息和状态
        updated_entities_data = []
        for entity in entities_data:
            direction = random.uniform(0, 2 * math.pi)  # 随机方向
            
            # 确保敌方和我方实体在指定的区域内移动
            if entity.enemy:
                # 敌方实体只能在右上区域移动
                move_entity_in_region(
                    entity, direction, entity.policy, entities_data, location_histories[entity.name],
                    longitude_buffer_max, LONGITUDE_MAX, latitude_buffer_max, LATITUDE_MAX
                )
            else:
                # 我方实体只能在左下区域移动
                move_entity_in_region(
                    entity, direction, entity.policy, entities_data, location_histories[entity.name],
                    LONGITUDE_MIN, longitude_buffer_min, LATITUDE_MIN, latitude_buffer_min
                )
            
            entity.temperature = generate_random_temperature()  # 每个时间步改变温度

            # 更新历史位置
            # location_histories[entity.name].append(entity.location)
            updated_entities_data.append(entity)

        # 更新上一个时间戳
        last_time = current_time

        # 将当前时间步的实体数据加入到 JSON 数据中
        json_data = {
            "time": time_str,
            "entities": [to_dict(entity) for entity in updated_entities_data]  # 使用 to_dict 方法来转换实体
        }
        json_data_list.append(json_data)

        # 更新实体数据为当前时间步的实体数据
        entities_data = updated_entities_data

    return json_data_list

# 生成实体
def create_entity(num, id, enemy):
    entities_data = []
    
    for i in range(num):
        name = f"Entity{i+id}"
        policy = random.choice(POLICIES)  # 随机选择策略
        
        entity_types = ENTITY_TYPES
        # 生成实体         
        entity_type = random.choices(entity_types, k=1, weights=WEIGHTS)[0]
        
        longitude = random.uniform(LONGITUDE_MIN, LONGITUDE_MAX)
        latitude = random.uniform(LATITUDE_MIN, LATITUDE_MAX)
        altitude = random.uniform(ALTITUDE_MIN, ALTITUDE_MAX)  # 海拔高度限制在0到500米
        
        # 生成实体
        entity = generate_entity_by_policy(name, enemy, entity_type, longitude, latitude, altitude, policy)
        entities_data.append(entity)
        
    return entities_data

# 针对湖南大学数据，根据已知的第一个时间戳实体信息，生成后续时间步的实体信息
def generate_json_data_from_initial2(initial_entities_data, start_time, num_time_steps, location_histories=None):
    """
    湖南大学数据，生成与我方实体个数相同的敌方实体
    """
    if isinstance(initial_entities_data[0], dict):
        initial_entities_data = dicts_to_objects(initial_entities_data)
    elif isinstance(initial_entities_data[0], list):
        initial_entities_data = [entity for sublist in initial_entities_data for entity in sublist]

    entity_types = ENTITY_TYPES
    if len(initial_entities_data) < 50:
        num_needed = 50 - len(initial_entities_data)
        num_friends = num_needed // 2
        num_enemies = num_needed - num_friends

        # 生成我方实体
        for i in range(len(initial_entities_data)):
            name = "Virtual{}".format(i)
            policy = random.choice(POLICIES)  # 随机选择策略
            enemy = True
            entity_type = random.choices(entity_types, k=1, weights=WEIGHTS)[0]

            # longitude = random.uniform(130.0, 135.0)
            # latitude = random.uniform(55.0, 60.0)
            longitude = random.uniform(LONGITUDE_MIN, LONGITUDE_MAX)
            latitude = random.uniform(LATITUDE_MIN, LATITUDE_MAX)
            altitude = random.uniform(ALTITUDE_MIN, ALTITUDE_MAX)
            
            # 生成敌方实体
            entity = generate_entity_by_policy(name, enemy, entity_type, longitude, latitude, altitude, policy)
            initial_entities_data.append(entity)
            
    json_data_list = []

    # 初始化上一个时间戳为传入的起始时间
    last_time = start_time

    # 如果没有提供历史位置数据，则初始化一个空字典
    if location_histories is None:
        location_histories = {entity.name: [entity.location] for entity in initial_entities_data}

    # 设置中间缓冲区（不生成实体）
    buffer_ratio = 0.2  # 中间区域占地图比例 (20%)
    
    # 根据经纬度范围计算缓冲区边界
    longitude_buffer_min = LONGITUDE_MIN + (LONGITUDE_MAX - LONGITUDE_MIN) * (1 - buffer_ratio) / 2
    longitude_buffer_max = LONGITUDE_MIN + (LONGITUDE_MAX - LONGITUDE_MIN) * (1 + buffer_ratio) / 2
    latitude_buffer_min = LATITUDE_MIN + (LATITUDE_MAX - LATITUDE_MIN) * (1 - buffer_ratio) / 2
    latitude_buffer_max = LATITUDE_MIN + (LATITUDE_MAX - LATITUDE_MIN) * (1 + buffer_ratio) / 2

    # 将第一个时间步的数据加入到 JSON 数据中
    time_str = last_time.strftime("%Y-%m-%d %H:%M:%S")
    json_data_list.append({
        "time": time_str,
        "entities": [to_dict(entity) for entity in initial_entities_data]  # 使用 to_dict 方法来转换实体
    })

    # 当前的实体数据初始化为已知的初始数据
    entities_data = initial_entities_data

    # 生成后续时间步数据
    for _ in range(1, num_time_steps):
        days_later = 1  # 每隔1天采样1次
        current_time = last_time + relativedelta(days=days_later)
        time_str = current_time.strftime("%Y-%m-%d %H:%M:%S")

        # 更新实体位置信息和状态
        updated_entities_data = []
        for entity in entities_data:
            direction = random.uniform(0, 2 * math.pi)  # 随机方向
            
            # 确保敌方和我方实体在指定的区域内移动
            if entity.enemy:
                # 敌方实体只能在右上区域移动
                move_entity_in_region(
                    entity, direction, entity.policy, entities_data, location_histories[entity.name],
                    longitude_buffer_max, LONGITUDE_MAX, latitude_buffer_max, LATITUDE_MAX
                )
            else:
                # 我方实体只能在左下区域移动
                move_entity_in_region(
                    entity, direction, entity.policy, entities_data, location_histories[entity.name],
                    LONGITUDE_MIN, longitude_buffer_min, LATITUDE_MIN, latitude_buffer_min
                )
            
            entity.temperature = generate_random_temperature()  # 每个时间步改变温度

            # 更新历史位置
            # location_histories[entity.name].append(entity.location)
            updated_entities_data.append(entity)

        # 更新上一个时间戳
        last_time = current_time

        # 将当前时间步的实体数据加入到 JSON 数据中
        json_data = {
            "time": time_str,
            "entities": [to_dict(entity) for entity in updated_entities_data]  # 使用 to_dict 方法来转换实体
        }
        json_data_list.append(json_data)

        # 更新实体数据为当前时间步的实体数据
        entities_data = updated_entities_data

    return json_data_list

# 移动实体并确保其在给定的经纬度范围内（用于敌方和我方区域）
def move_entity_in_region(entity, direction, policy, entities_data, location_history, lon_min, lon_max, lat_min, lat_max):
    """
    移动实体并确保其在给定的经纬度范围内（用于敌方和我方区域）。
    
    参数:
    - entity: 需要移动的实体对象
    - direction: 移动的方向
    - policy: 移动策略
    - entities_data: 其他实体的列表
    - location_history: 实体的历史位置
    - lon_min, lon_max: 经度的最小和最大值
    - lat_min, lat_max: 纬度的最小和最大值
    """
    # 调用 move_entity 函数更新位置
    move_entity(entity, direction, policy, entities_data, location_history)

    # 强制约束实体位置在指定区域内
    entity.location.longitude = max(lon_min, min(lon_max, entity.location.longitude))
    entity.location.latitude = max(lat_min, min(lat_max, entity.location.latitude))
    entity.location.altitude = max(ALTITUDE_MIN, min(ALTITUDE_MAX, entity.location.altitude))  # 保持海拔在范围内


def generate_json_data_for_entity(initial_entities_data, start_time, num_time_steps, target_entity_name=None, location_histories=None):
    """
    根据已知的第一个时间戳实体信息，生成后续时间步的信息。
    当 target_entity_name 为 None 时，调用 generate_json_data_from_initial 生成所有实体的信息；
    否则，生成指定实体的后续时间步信息。

    参数:
    - initial_entities_data: 第一个时间戳的实体数据 (已知实体)
    - start_time: 第一个时间戳，格式为 datetime 类型
    - num_time_steps: 需要生成的时间步数
    - target_entity_name: 需要提取的目标实体名称，None 表示生成所有实体的信息
    - location_histories: 每个实体的位置信息历史（可选）

    返回值:
    - json_data_list: 包含每个时间步实体信息的 JSON 数据列表
    """
    # 如果 target_entity_name 为 None，直接调用 generate_json_data_from_initial 生成所有实体的数据
    if target_entity_name is None:
        return generate_json_data_from_initial(initial_entities_data, start_time, num_time_steps, location_histories)
    
    # 否则，只生成目标实体的数据
    # 如果 initial_entities_data 是字典列表，则将其转换为实体对象
    if isinstance(initial_entities_data[0], dict):
        initial_entities_data = dicts_to_objects(initial_entities_data)

    json_data_list = []

    # 初始化上一个时间戳为传入的起始时间
    last_time = start_time

    # 查找目标实体
    target_entity = next((entity for entity in initial_entities_data if entity.name == target_entity_name), None)
    
    if target_entity is None:
        raise ValueError(f"实体 '{target_entity_name}' 不存在于初始数据中。")

    # 如果没有提供历史位置数据，则初始化一个空字典
    if location_histories is None:
        location_histories = {target_entity.name: [target_entity.location]}

    # 第一个时间步数据
    time_str = last_time.strftime("%Y-%m-%d %H:%M:%S")
    json_data_list.append({
        "time": time_str,
        "entity": to_dict(target_entity)  # 使用 to_dict 方法来转换目标实体
    })

    # 当前的实体数据初始化为目标实体数据
    entity_data = target_entity

    # 生成后续时间步数据
    for _ in range(1, num_time_steps):
        days_later = 1  # 每隔1天采样1次
        current_time = last_time + relativedelta(days=days_later)
        time_str = current_time.strftime("%Y-%m-%d %H:%M:%S")

        # 更新目标实体位置信息和状态
        direction = random.uniform(0, 2 * math.pi)  # 随机方向
        move_entity(entity_data, direction, entity_data.policy, [entity_data], location_histories[entity_data.name])
        entity_data.temperature = generate_random_temperature()  # 每个时间步改变温度

        # 更新历史位置
        location_histories[entity_data.name].append(entity_data.location)

        # 更新上一个时间戳
        last_time = current_time

        # 将当前时间步的目标实体数据加入到 JSON 数据中
        json_data = {
            "time": time_str,
            "entity": to_dict(entity_data)  # 使用 to_dict 方法来转换目标实体
        }
        json_data_list.append(json_data)

    return json_data_list

# 保存态势到文件（json）
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
            elif category == "ArmoredVehicles":
                entity = ArmoredVehicles(name=name, enemy=enemy, location=location, policy=policy, temperature=temperature, environment=environment, previous_location=previous_location)
            elif category == "MissileVehicle":
                entity = MissileVehicle(name=name, enemy=enemy, location=location, policy=policy, temperature=temperature, environment=environment, previous_location=previous_location)
            elif category == "Vehicles":
                entity = Vehicles(name=name, enemy=enemy, location=location, policy=policy, temperature=temperature, environment=environment, previous_location=previous_location)
            elif category == "Airplane":
                entity = Airplane(name=name, enemy=enemy, location=location, policy=policy, temperature=temperature, environment=environment, previous_location=previous_location)
            else:
                continue

            entities_at_time.append(entity)

        all_entities_by_time.append({"time": time, "entities": entities_at_time})

    return all_entities_by_time

def read_entities_from_data(json_data):
    entities = []
    for entity_data in json_data:
        time = entity_data["time"]
        
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

        # 根据类别创建相应实体
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

        entities.append(entity)

    return {"entities": entities}




if __name__ == "__main__":
    conditions = [
        ("small_scale", "self_advantage"),
        ("large_scale", "self_advantage"),
        ("small_scale", "enemy_advantage"),
        ("large_scale", "enemy_advantage"),
    ]
    num_time_steps = 5 # 每个条件组合下的时间步数
    num_files_per_condition = 10  # 每个条件组合下生成的文件数量
    
    # num_time_steps = 6000 # 每个条件组合下的时间步数
    # num_files_per_condition = 1  # 每个条件组合下生成的文件数量

    file_directory = "/root/yhz/code/situation_awareness/backend/data/"
    # file_directory = "/root/yhz/code/situation_awareness/backend/data_anomaly_use/"

    for i, (scale, advantage) in enumerate(conditions):
        for file_index in range(1, num_files_per_condition + 1):
            # Generate data with multiple time steps for each condition
            json_data_list = generate_json_data_multiple_time_steps(num_time_steps, [(scale, advantage)])

            # Save the data to a file
            filename = f"{file_directory}{scale}_{advantage}_{file_index}.json"
            save_json_to_file(json_data_list, filename)
            print(f"Data with multiple time steps has been written to {filename}")