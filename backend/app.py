'''
app.py
接口
'''
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from flask.views import MethodView
from extension import db
from models import Situation
from entity import BattlefieldEntity
from map import Map
import os, json, uuid
from entity import Tank, Soldier, Helicopter, FighterJet, Artillery, InfantryFightingVehicle, UAV, ArmoredVehicles, MissileVehicle, Vehicles, Airplane, CamouflageNet
from math import sqrt
from situation_evaluate import local_strength_advantage, local_terrain_advantage, unilateral_strength_advantage, unilateral_terrain_advantage, battlefield_chaos_degree
from anomaly_detection import generate_entities_with_updated_policy, read_first_n_json_files, monitor_entities2 
from data_generate import generate_json_data_for_entity, generate_json_data_from_initial, save_json_to_file, generate_json_data_from_initial2
from datetime import datetime, timedelta


app = Flask(__name__)
CORS().init_app(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:123456@127.0.0.1:3306/sa'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# db.init_app(app)

# 测试接口
@app.route('/')
def index():
    return 'Hello world!'

# 从json文件读取战场实体
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

            entity_class = category_map.get(category, BattlefieldEntity)
            entity = entity_class(name=name, enemy=enemy, location=location, policy=policy, temperature=temperature, environment=environment, previous_location=previous_location)
            
            entities_at_time.append(entity.to_dict())

        all_entities_by_time.append({"time": time, "entities": entities_at_time})

    return all_entities_by_time


# 保存态势信息到json
def save_json_to_file(json_data, file_path):
    current_dir = os.path.dirname(os.path.abspath(__file__))
    json_file_path = os.path.join(current_dir, 'upload', file_path)
    with open(json_file_path, "w") as file:
        json.dump(json_data, file)
        
        
# 上传态势文件接口
@app.route("/upload", methods=["POST"])
def upload_file():
    p_uuid = str(uuid.uuid1())
    file = request.files.get("file")
    file_name = file.filename
    sp = file_name.split(".")
    file_name = sp[0] + p_uuid + '.' + sp[1]
    current_dir = os.path.dirname(os.path.abspath(__file__))
    save_path = os.path.join(current_dir, 'upload', file_name)
    file.save(save_path)

    ret = {"file_name": file_name}
    return jsonify(ret)

# 读取态势文件接口
@app.route('/read_from_json_file', methods=['POST'])
def read_from_json_file():
    data = request.get_json()
    file_name = data.get('file_name')
    if not file_name:
        return jsonify({"error": "File name is required"}), 400

    current_dir = os.path.dirname(os.path.abspath(__file__))
    json_file_path = os.path.join(current_dir, 'upload', file_name)
    
    if not os.path.exists(json_file_path):
        return jsonify({"error": "File not found"}), 404

    all_entities_by_time = read_and_extract_entities(json_file_path)
    return jsonify(all_entities_by_time)

# 实体类别映射
category_map = {
    "Tank": Tank,
    "Soldier": Soldier,
    "Helicopter": Helicopter,
    "FighterJet": FighterJet,
    "Artillery": Artillery,
    "InfantryFightingVehicle": InfantryFightingVehicle,
    "UAV": UAV,
    "ArmoredVehicles": ArmoredVehicles,
    "MissileVehicle": MissileVehicle,
    "Vehicles": Vehicles,
    "Airplane": Airplane,
    "CamouflageNet": CamouflageNet
}

# 创建实体列表的辅助函数
def create_entities(entity_data_list):
    entities = []
    for entity_data in entity_data_list:
        category = entity_data.pop("category", None)
        entity_class = category_map.get(category, BattlefieldEntity)
        location_data = entity_data.get("location")
        location = Map(location_data["longitude"], location_data["latitude"], location_data["altitude"])
        previous_location_data = entity_data.get("previous_location")
        previous_location = Map(previous_location_data["longitude"], previous_location_data["latitude"], previous_location_data["altitude"]) if previous_location_data else None

        entity = entity_class(
            name=entity_data["name"],
            enemy=entity_data["enemy"],
            location=location,
            policy=entity_data["policy"],
            temperature=entity_data["temperature"],
            environment=entity_data["environment"],
            previous_location=previous_location
        )
        entities.append(entity)
    return entities


'''
态势评估
1.局部战力优势
2.局部地势优势
3.单方战力优势
4.单方地势优势
5.战场混乱程度
'''
# 局部战力优势接口
@app.route('/local_strength_advantage', methods=['POST'])
def local_strength_advantage_api():
    data = request.get_json()
    if not isinstance(data, list):
        return jsonify({'error': 'Invalid input. Expected a list.'}), 400
    
    results = []
    for entry in data:
        entities_data = entry.get("entities", [])
        timestamp = entry.get("time", "")

        if not entities_data or not timestamp:
            return jsonify({'error': 'Invalid input. Each entry must contain entities and time.'}), 400

        # 实例化所有实体列表
        all_entities = create_entities(entities_data)

        # 计算每个实体的局部战力优势
        advantages = []
        for current_entity in all_entities:
            advantage = local_strength_advantage(current_entity, all_entities)
            advantages.append({
                'entity_name': current_entity.get_name(),
                'local_strength_advantage': advantage
            })

        # 将结果加入列表
        results.append({
            'time': timestamp,
            'advantages': advantages
        })

    return jsonify(results)

# 局部地势优势接口
@app.route('/local_terrain_advantage', methods=['POST'])
def local_terrain_advantage_api():
    data = request.get_json()
    if not isinstance(data, list):
        return jsonify({'error': 'Invalid input. Expected a list.'}), 400
    
    results = []
    for entry in data:
        entities_data = entry.get("entities", [])
        timestamp = entry.get("time", "")

        if not entities_data or not timestamp:
            return jsonify({'error': 'Invalid input. Each entry must contain entities and time.'}), 400

        # 实例化所有实体列表
        all_entities = create_entities(entities_data)

        # 计算每个实体的局部地势优势
        advantages = []
        for current_entity in all_entities:
            advantage = local_terrain_advantage(current_entity, all_entities)
            advantages.append({
                'entity_name': current_entity.get_name(),
                'local_terrain_advantage': advantage
            })

        # 将结果加入列表
        results.append({
            'time': timestamp,
            'advantages': advantages
        })

    return jsonify(results)

# 单方战力优势接口
@app.route('/unilateral_strength_advantage', methods=['POST'])
def unilateral_strength_advantage_api():
    data = request.get_json()
    if not isinstance(data, list):
        return jsonify({'error': 'Invalid input. Expected a list.'}), 400
    
    results = []
    for entry in data:
        entities_data = entry.get("entities", [])
        timestamp = entry.get("time", "")

        if not entities_data or not timestamp:
            return jsonify({'error': 'Invalid input. Each entry must contain entities and time.'}), 400
        
        # 实例化所有实体列表
        all_entities = create_entities(entities_data)
        
        # 根据 enemy 字段筛选出友方和敌方实体
        our_entities = [entity for entity in all_entities if not entity.enemy]
        enemy_entities = [entity for entity in all_entities if entity.enemy]
        
        # 计算友方和敌方的战力优势
        our_advantage = unilateral_strength_advantage(our_entities, all_entities)
        enemy_advantage = unilateral_strength_advantage(enemy_entities, all_entities)
        
        # 将结果加入列表
        results.append({
            'time': timestamp,
            'our_strength_advantage': our_advantage,
            'enemy_strength_advantage': enemy_advantage
        })
        
    return jsonify(results)

# 单方地势优势接口
@app.route('/unilateral_terrain_advantage', methods=['POST'])
def unilateral_terrain_advantage_api():
    data = request.get_json()
    if not isinstance(data, list):
        return jsonify({'error': 'Invalid input. Expected a list.'}), 400
    
    results = []
    for entry in data:
        entities_data = entry.get("entities", [])
        timestamp = entry.get("time", "")

        if not entities_data or not timestamp:
            return jsonify({'error': 'Invalid input. Each entry must contain entities and time.'}), 400
        
        # 实例化所有实体列表
        all_entities = create_entities(entities_data)
        
        # 根据 enemy 字段筛选出友方和敌方实体
        our_entities = [entity for entity in all_entities if not entity.enemy]
        enemy_entities = [entity for entity in all_entities if entity.enemy]
        
        # 计算友方和敌方的地势优势
        our_advantage = unilateral_terrain_advantage(our_entities, all_entities)
        enemy_advantage = unilateral_terrain_advantage(enemy_entities, all_entities)
        
        # 将结果加入列表
        results.append({
            'time': timestamp,
            'our_terrain_advantage': our_advantage,
            'enemy_terrain_advantage': enemy_advantage
        })
        
    return jsonify(results)

# 战场混乱程度接口
@app.route('/battlefield_chaos_degree', methods=['POST'])
def battlefield_chaos_degree_api():
    data = request.get_json()
    if not isinstance(data, list):
        return jsonify({'error': 'Invalid input. Expected a list.'}), 400
    
    results = []
    for entry in data:
        entities_data = entry.get("entities", [])
        timestamp = entry.get("time", "")

        if not entities_data or not timestamp:
            return jsonify({'error': 'Invalid input. Each entry must contain entities and time.'}), 400

        # 实例化所有实体列表
        all_entities = create_entities(entities_data)

        # 根据 enemy 字段筛选出我方和敌方实体
        our_entities = [entity for entity in all_entities if not entity.enemy]
        enemy_entities = [entity for entity in all_entities if entity.enemy]

        # 调用计算战场混乱程度的函数
        chaos_degree = battlefield_chaos_degree(our_entities, enemy_entities, all_entities)

        # 将结果加入列表
        results.append({
            'time': timestamp,
            'battlefield_chaos_degree': chaos_degree
        })

    return jsonify(results)

'''
态势监管规则
1.位置监管
2.区域监管
3.实体环境监管
4.活动监管
5.属性监管
'''
# 位置监管接口
@app.route('/rule_location', methods=['POST'])
def return_rule_location():
    data = request.get_json()
    if not isinstance(data, dict):
        return jsonify({'error': 'Invalid input. Expected a dictionary.'}), 400

    entries = data.get('entries')
    regulation_center_data = data.get('regulation_center')
    radius = data.get('radius')

    if not entries or not isinstance(entries, list) \
            or not regulation_center_data or not isinstance(regulation_center_data, dict) \
            or not isinstance(radius, (int, float)):
        return jsonify({'error': 'Invalid input data.'}), 400

    reference_longitude = regulation_center_data.get('longitude')
    reference_latitude = regulation_center_data.get('latitude')

    if reference_longitude is None or reference_latitude is None:
        return jsonify({'error': 'Invalid regulation center coordinates.'}), 400

    results = []
    for entry in entries:
        entities_data = entry.get('entities')
        timestamp = entry.get('time')

        if not entities_data or not isinstance(entities_data, list) or not timestamp:
            return jsonify({'error': 'Invalid input data in entry.'}), 400

        out_of_range_entities = []

        # 检查每个实体是否在监管区域内
        for entity in entities_data:
            entity_name = entity.get('name')
            longitude = entity.get('location', {}).get('longitude')
            latitude = entity.get('location', {}).get('latitude')
            category = entity.get('category')

            if longitude is None or latitude is None:
                continue

            # 计算与指定坐标 (reference_longitude, reference_latitude) 的距离
            distance = sqrt((longitude - reference_longitude)**2 + (latitude - reference_latitude)**2)*100
            # print(entity_name, distance)
            if distance > radius:
                # out_of_range_entities.append(entity.get('name'))
                # 记录超出范围的实体，带上它的名称和坐标
                out_of_range_entities.append({
                    'name': entity_name,
                    'category': category,
                    'location': {
                        'longitude': longitude,
                        'latitude': latitude
                    }
                })

        # 将结果加入列表
        results.append({
            'time': timestamp,
            'abnormal-type': 0,
            'result': out_of_range_entities
        })

    return jsonify(results)

# 区域监管
@app.route('/rule_area', methods=['POST'])
def rule_area():
    data = request.get_json()
    if not isinstance(data, dict):
        return jsonify({'error': 'Invalid input. Expected a dictionary.'}), 400

    entries = data.get('entries')
    regulation_center = data.get('regulation_center')
    temperature_threshold = data.get('temperature_threshold')

    # 检查entries, regulation_center和temperature_threshold是否存在且类型正确
    if not entries or not isinstance(entries, list) or not regulation_center or not isinstance(regulation_center, dict) or temperature_threshold is None:
        return jsonify({'error': 'Missing or invalid entries, regulation_center, or temperature_threshold data.'}), 400

    # 提取监管区域的中心点坐标
    regulation_longitude = regulation_center.get('longitude')
    regulation_latitude = regulation_center.get('latitude')

    if regulation_longitude is None or regulation_latitude is None:
        return jsonify({'error': 'Invalid regulation_center location format.'}), 400

    results = []  # 用于存储每个时间戳的结果

    for entry in entries:
        entities = entry.get('entities')
        timestamp = entry.get('time')

        if not entities or not isinstance(entities, list) or not timestamp:
            return jsonify({'error': f'Invalid input data in entry with time {timestamp}.'}), 400

        anomalies_list = []  # 用于存储当前时间戳的异常实体的名称

        for entity in entities:
            if not isinstance(entity, dict):
                continue  # 如果实体数据不是字典，跳过当前实体

            entity_name = entity.get('name')
            entity_location = entity.get('location')
            entity_temperature = entity.get('temperature')
            longitude = entity.get('location', {}).get('longitude')
            latitude = entity.get('location', {}).get('latitude')
            category = entity.get('category')

            # 检查实体位置和温度数据是否存在
            if not entity_location or not isinstance(entity_location, dict) or entity_temperature is None:
                continue

            # 检查实体是否有异常温度
            if entity_temperature > temperature_threshold:
                # anomalies_list.append(entity_name)  # 添加异常实体名称到列表
                anomalies_list.append({
                    'name': entity_name,
                    'category': category,
                    'temperature': entity_temperature,
                    'location': {
                        'longitude': longitude,
                        'latitude': latitude
                    }
                })

        # 将当前时间戳的结果加入结果列表
        results.append({
            'time': timestamp,
            'abnormal-type': 1,
            'result': anomalies_list
        })

    return jsonify(results)

# 实体环境监管
@app.route('/rule_entity_environment', methods=['POST'])
def return_rule_entity_environment():
    data = request.get_json()
    if not isinstance(data, dict):
        return jsonify({'error': 'Invalid input. Expected a dictionary.'}), 400
    
    entries = data.get('entries')
    type_match = data.get('type_match')

    if not entries or not isinstance(entries, list) or not type_match or not isinstance(type_match, dict):
        return jsonify({'error': 'Invalid input data.'}), 400
    
    results = []  # 用于存储每个时间戳的结果

    for entry in entries:
        entities_data = entry.get('entities')
        timestamp = entry.get('time')

        if not entities_data or not isinstance(entities_data, list) or not timestamp:
            return jsonify({'error': f'Invalid input data in entry with time {timestamp}.'}), 400

        anomalies_list = []  # 用于存储当前时间戳的异常实体的名称

        # 检查每个实体是否在其对应环境中
        for entity in entities_data:
            entity_name = entity.get('name')
            entity_type = entity.get('category')
            entity_environment = entity.get('environment')
            longitude = entity.get('location', {}).get('longitude')
            latitude = entity.get('location', {}).get('latitude')
            category = entity.get('category')

            # 如果实体不在对应环境中，添加到异常列表
            if type_match.get(entity_type) != entity_environment:
                anomalies_list.append({
                    'name': entity_name,
                    'category': category,
                    'location': {
                        'longitude': longitude,
                        'latitude': latitude
                    }
                })

        # 将当前时间戳的结果加入结果列表
        results.append({
            'time': timestamp,
            'abnormal-type': 2,
            'result': anomalies_list
        })

    return jsonify(results)

# 活动监管
@app.route('/rule_activity', methods=['POST'])
def rule_activity():
    data = request.get_json()
    if not isinstance(data, dict):
        return jsonify({'error': 'Invalid input. Expected a dictionary.'}), 400

    entries = data.get('entries')
    inactivity_threshold = data.get('inactivity_threshold')

    if not entries or not isinstance(entries, list) or not isinstance(inactivity_threshold, int):
        return jsonify({'error': 'Invalid input data.'}), 400

    results = []  # 用于存储每个时间戳的结果

    for entry in entries:
        entities_data = entry.get('entities')
        timestamp = entry.get('time')

        if not entities_data or not isinstance(entities_data, list) or not timestamp:
            return jsonify({'error': f'Invalid input data in entry with time {timestamp}.'}), 400

        anomalies_list = []  # 用于存储当前时间戳的异常实体的名称

        # 检查每个实体的活动情况
        for entity in entities_data:
            entity_name = entity.get('name')
            current_location = entity.get('location')
            previous_location = entity.get('previous_location')
            longitude = entity.get('location', {}).get('longitude')
            latitude = entity.get('location', {}).get('latitude')
            category = entity.get('category')

            # 检查是否有足够的历史位置数据来判断静默行为
            if previous_location and category != "CamouflageNet" and current_location == previous_location:
                # 如果实体显示异常的不活动，添加到异常列表
                # anomalies_list.append(entity_name)
                anomalies_list.append({
                    'name': entity_name,
                    'category': category,
                    'location': {
                        'longitude': longitude,
                        'latitude': latitude
                    }
                })

        # 将当前时间戳的结果加入结果列表
        results.append({
            'time': timestamp,
            'abnormal-type': 3,
            'result': anomalies_list
        })

    return jsonify(results)

# 属性监管
@app.route('/rule_attributes', methods=['POST'])
def return_rule_attributes():
    data = request.get_json()
    if not isinstance(data, dict):
        return jsonify({'error': 'Invalid input. Expected a dictionary.'}), 400

    entries = data.get('entries')
    entity_threshold = data.get('entity_threshold')

    if not entries or not isinstance(entries, list) or not isinstance(entity_threshold, int):
        return jsonify({'error': 'Invalid input data.'}), 400

    results = []  # 用于存储每个时间戳的结果
    name_list = [] # 用于存储当前时间戳的伪装网实体的名称
    pre_name_list = []  # 用于存储前一个时间戳的伪装网实体的名称
    pre_num = 0

    for entry in entries:
        entities_data = entry.get('entities')
        timestamp = entry.get('time')

        if not entities_data or not isinstance(entities_data, list) or not timestamp:
            return jsonify({'error': f'Invalid input data in entry with time {timestamp}.'}), 400

        anomalies_list = []  # 用于存储当前时间戳的异常实体的名称
        cnt = 0
        
        for entity in entities_data:
            category = entity.get('category')
            name = entity.get('name')
            if category == 'CamouflageNet':
                cnt += 1
                name_list.append(name)
                
        # print(cnt,pre_num)
               
        if pre_num and abs(cnt - pre_num) >= entity_threshold:
            for entity in entities_data:
                name = entity.get('name')
                enemy = entity.get('enemy')
                if name in pre_name_list and enemy:                 
                    entity_name = entity.get('name')
                    longitude = entity.get('location', {}).get('longitude')
                    latitude = entity.get('location', {}).get('latitude')
                    category = entity.get('category')
                    anomalies_list.append({
                        'name': entity_name,
                        'category': category,
                        'location': {
                            'longitude': longitude,
                            'latitude': latitude
                        }
                    })
        pre_num = cnt
        pre_name_list = name_list
        # 将当前时间戳的结果加入结果列表
        results.append({
            'time': timestamp,
            'abnormal-type': 4,
            'result': anomalies_list
        })

    return jsonify(results)

'''
模拟数据生成
根据当前态势文件的最新时间戳数据，生成后续32个时间戳的态势数据，并写到新的json文件中
'''
# 模拟数据生成接口
@app.route('/generate_future_data', methods=['POST'])
def generate_future_data_api():
    data = request.get_json()

    # 验证输入是否为正确格式
    if not data or not isinstance(data, dict):
        return jsonify({'error': 'Invalid input. Expected a dictionary with file_name and num_time_steps.'}), 400

    file_name = data.get("file_name", "")
    num_time_steps = data.get("num_time_steps", 32)

    # 验证是否提供了文件名和时间步数
    if not file_name or num_time_steps <= 0:
        return jsonify({'error': 'Invalid input. "file_name" and "num_time_steps" are required and num_time_steps should be greater than 0.'}), 400

    current_dir = os.path.dirname(os.path.abspath(__file__))
    json_file_path = os.path.join(current_dir, 'upload', file_name)

    # 读取文件中的实体数据
    try:
        all_entities_by_time = read_and_extract_entities(json_file_path)
    except FileNotFoundError:
        return jsonify({'error': f'File {file_name} not found.'}), 400
    except json.JSONDecodeError:
        return jsonify({'error': f'File {file_name} is not a valid JSON file.'}), 400

    # 提取最新时间点的实体数据作为初始实体，并获取对应的时间戳
    if not all_entities_by_time:
        return jsonify({'error': 'The file does not contain valid entities data.'}), 400

    # 提取最新时间戳和对应的实体数据
    latest_entry = all_entities_by_time[-1]
    initial_entities_data = latest_entry["entities"]
    start_time_str = latest_entry["time"]

    # 将时间戳字符串转换为 datetime 对象
    try:
        start_time = datetime.strptime(start_time_str, "%Y-%m-%d %H:%M:%S")
    except ValueError:
        return jsonify({'error': 'Invalid time format in the input data. Expected format: "YYYY-MM-DD HH:MM:SS".'}), 400
    
    # 生成后续时间步的数据，传入初始时间戳
    if len(initial_entities_data) > 10:
        json_data = generate_json_data_from_initial(initial_entities_data, start_time, num_time_steps)
    else:
        json_data = generate_json_data_from_initial2(initial_entities_data, start_time, num_time_steps)
    # 确定新的文件名以保存生成的数据
    new_file_name = f"generated_data_{file_name}"  # 你可以根据需要自定义文件名
    new_json_file_path = os.path.join(current_dir, 'upload', new_file_name)

    # 将生成的数据写入新的文件中
    try:
        save_json_to_file(json_data, new_json_file_path)
    except IOError as e:
        return jsonify({'error': 'Failed to write to new file'}), 500

    return jsonify({
        'message': 'Data successfully generated and saved',
        'file_name': new_file_name  # 返回新的文件名
    }), 200


    
@app.route('/generate_future_data_for_entity', methods=['POST'])
def generate_future_data_for_entity_api():
    data = request.get_json()

    # 验证输入是否为正确格式
    if not data or not isinstance(data, dict):
        return jsonify({'error': 'Invalid input. Expected a dictionary with file_name, num_time_steps, and optional target_entity_name.'}), 400

    file_name = data.get("file_name", "")
    num_time_steps = data.get("num_time_steps", 10)  # 默认生成10个时间步
    target_entity_name = data.get("target_entity_name", None)  # 默认为 None，表示返回所有实体

    # 验证是否提供了文件名和时间步数
    if not file_name or num_time_steps <= 0:
        return jsonify({'error': 'Invalid input. "file_name" and "num_time_steps" are required and num_time_steps should be greater than 0.'}), 400

    current_dir = os.path.dirname(os.path.abspath(__file__))
    json_file_path = os.path.join(current_dir, 'upload', file_name)

    # 读取文件中的实体数据
    try:
        with open(json_file_path, 'r') as json_file:
            all_entities_by_time = json.load(json_file)  # 读取JSON文件
    except FileNotFoundError:
        return jsonify({'error': f'File {file_name} not found.'}), 400
    except json.JSONDecodeError:
        return jsonify({'error': f'File {file_name} is not a valid JSON file.'}), 400

    # 提取最新时间点的实体数据作为初始实体，并获取对应的时间戳
    if not all_entities_by_time:
        return jsonify({'error': 'The file does not contain valid entities data.'}), 400
    

    # 调用 generate_entities_with_updated_policy 更新策略
    updated_entities, final_time = generate_entities_with_updated_policy(all_entities_by_time)
    
    print(final_time)

    # 处理 updated_entities 和 final_time
    # 你可能想要对 final_time 进行一些处理，如果需要的话
    # 例如，将 final_time 转换为 datetime 对象
    start_time = final_time  # 使用 final_time 作为开始时间
    # start_time = datetime.strptime(final_time, "%Y-%m-%d %H:%M:%S")
    
    # formatted_data = [{
    #     "time": start_time,  # 可以使用实际时间
    #     "entities": updated_entities
    # }]
    
    # # print(formatted_data)

    # # 调用 read_and_extract_entities 处理 formatted_data
    # processed_entities_data = read_and_extract_entities(formatted_data)
    
    # print(f"processed_entities_data:{processed_entities_data}")

    # 调用 generate_json_data_for_entity，传入指定的实体名称和初始时间戳
    json_data = generate_json_data_for_entity(updated_entities, start_time, num_time_steps, target_entity_name)

    # 返回生成的 JSON 数据
    return jsonify({
        'message': 'Data successfully generated',
        'data': json_data  # 返回生成的 JSON 数据
    }), 200




@app.route('/anomaly_detection', methods=['POST'])
def detect_abnormalities():
    # 从请求中获取 JSON 数据
    data = request.get_json()
    if not isinstance(data, list):
        return jsonify({'error': 'Invalid input. Expected a list.'}), 400

    json_data = data  # 直接使用 data，因为它已经是一个列表

    try:
        # 执行异常检测
        anomalous_entities = monitor_entities2(json_data)

        # 准备返回结果
        results = {
            'abnormal_entities': anomalous_entities,
        }

        return jsonify(results)

    except json.JSONDecodeError as e:
        return jsonify({'error': 'Invalid JSON format.'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


'''
态势管理
1.新增态势
2.删除态势
3.修改态势
4.查询态势
5.多条件模糊分页查询
'''
# 态势多条件模糊分页查询接口
@app.route('/situations_page')
def get_situations_page():
    page = request.args.get('page', default=1, type=int) # 获取当前页码参数（默认为第一页）
    per_page = request.args.get('per_page', default=20, type=int) # 每页显示的记录条数（默认为20条）
    name_query = request.args.get('name', '')
    category_query = request.args.get('category', '')

    # 构建多条件模糊查询
    situations = Situation.query.filter(
        (Situation.name.like(f"%{name_query}%")) &
        (Situation.category.like(f"%{category_query}%"))
    ).order_by(Situation.id).paginate(page=page, per_page=per_page)
    
    return jsonify({
        'total': situations.total, # 返回总共有多少条记录
        'current_page': situations.page, # 返回当前页码
        'items_per_page': situations.per_page, # 返回每页显示的记录条数
        'data': [situation.to_dict() for situation in situations.items] # 将查询结果转换成JSON格式并返回
    })

# 态势CRUD接口
# class SituationApi(MethodView):
#     def get(self, situation_id):
#         if not situation_id:
#             situations: [Situation] = Situation.query.all() # type: ignore
#             results = [
#                 {
#                     'id': situation.id,
#                     'name': situation.name,
#                     'category': situation.category,
#                     'description': situation.description,
#                     'import_time': situation.import_time,
#                     'url': situation.url,
#                 } for situation in situations
#             ]
#             return {
#                 'status': 'success',
#                 'message': '数据查询成功',
#                 'results': results
#             }
#         situation: Situation = Situation.query.get(situation_id)
#         return {
#             'status': 'success',
#             'message': '数据查询成功',
#             'result': {
#                 'id': situation.id,
#                 'name': situation.name,
#                 'category': situation.category,
#                 'description': situation.description,
#                 'import_time': situation.import_time,
#                 'url': situation.url,
#             }
#         }

#     def post(self):
#         form = request.json
#         situation = Situation()
#         situation.name = form.get('name')
#         situation.category = form.get('category')
#         situation.description = form.get('description')
#         situation.import_time = form.get('import_time')
#         situation.url = form.get('url')
#         db.session.add(situation)
#         db.session.commit()

#         return {
#             'status': 'success',
#             'message': '数据添加成功'
#         }

#     def delete(self, situation_id):
#         situation = Situation.query.get(situation_id)
#         db.session.delete(situation)
#         db.session.commit()
#         return {
#             'status': 'success',
#             'message': '数据删除成功'
#         }

#     def put(self, situation_id):
#         situation: Situation = Situation.query.get(situation_id)
#         situation.name = request.json.get('name')
#         situation.category = request.json.get('category')
#         situation.description = request.json.get('description')
#         situation.import_time = request.json.get('import_time')
#         situation.url = request.json.get('url')
#         db.session.commit()
#         return {
#             'status': 'success',
#             'message': '数据修改成功'
#         }

# situation_api = SituationApi.as_view('situation_api')
# app.add_url_rule('/situations', view_func=situation_api, methods=['GET', ], defaults={'situation_id': None})
# app.add_url_rule('/situations', view_func=situation_api, methods=['POST', ])
# app.add_url_rule('/situations/<int:situation_id>', view_func=situation_api, methods=['GET', 'PUT', 'DELETE'])

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8091, debug=True)
    # app.run(host='0.0.0.0', port=8090, debug=True)
