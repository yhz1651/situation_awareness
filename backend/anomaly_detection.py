from map import Map
from entity import Tank, Soldier, Helicopter, FighterJet, Artillery, InfantryFightingVehicle, UAV
import json, random, math
import datetime
from datetime import timedelta, datetime
from dateutil.relativedelta import relativedelta
import json
import os
from data_generate import generate_json_data_for_entity, generate_json_data_from_initial, read_entities_from_data

# 阈值，相邻两个时间步之间同一个实体的经纬度差值不超过该值
max_lat_lon_difference = 2.0
# 相邻两个时间步之间的时间差不超过该值（以分钟为单位）
max_time_difference_minutes = 60
# 高度的最大变化值
max_altitude_difference = 10.0
# 策略不一致的情况
count_diff = 0
# 总策略数
total_num = 0
# 时间片范围内策略不一致的数量
time_count_diff = 0
# 和生成时一致的数量
count_same = 0
# 总运行次数
count_run = 0

# Policy的种类
POLICIES = ["near_friend", "far_from_friend", "near_enemy", "far_from_enemy"]

def read_json_files(directory):
    data = []
    # 遍历指定目录下的所有文件
    for filename in os.listdir(directory):
        if filename.endswith(".json"):
            filepath = os.path.join(directory, filename)
            with open(filepath, 'r') as file:
                file_data = json.load(file)
                data.extend(file_data)
    return data

def read_first_n_json_files(directory, num_files=1):
    all_files = [f for f in os.listdir(directory) if f.endswith(".json")]
    sorted_files = sorted(all_files)  # 按文件名排序
    selected_files = sorted_files[:min(num_files, len(sorted_files))]  # 选取前n个文件，防止文件数量少于n
    data = []
    for filename in selected_files:
        filepath = os.path.join(directory, filename)
        with open(filepath, 'r') as file:
            file_data = json.load(file)
            data.extend(file_data)
    return data

def read_specific_json_file(filepath):
    with open(filepath, 'r') as file:
        data = json.load(file)
    return data

def find_nearest_entity(entity, entities, is_enemy=True):
    # 使用列表推导式，同时根据是否敌对和是否为当前实体来过滤实体列表
    if is_enemy:
        filtered_entities = [e for e in entities if e['enemy'] != entity['enemy'] and e['name'] != entity['name']]
    else:
        filtered_entities = [e for e in entities if e['enemy'] == entity['enemy'] and e['name'] != entity['name']]

    if not filtered_entities:
        print("*NONE, entity:{}, entities:{}".format(entity, entities))
        return None  # 如果没有找到符合条件的其他实体，则返回 None

    # 使用计算距离的 lambda 函数作为 key，找到最近的实体
    nearest_entity = min(filtered_entities, key=lambda e: calculate_distance(entity, e))
    return nearest_entity

def calculate_distance(entity1, entity2):
    lat1, lon1 = entity1['location']['latitude'], entity1['location']['longitude']
    lat2, lon2 = entity2['location']['latitude'], entity2['location']['longitude']
    R = 6371.0  # 地球半径，单位为千米
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat / 2) ** 2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    distance = R * c
    return distance

def determine_direction(entity, target_entity):
    lat_diff = target_entity['location']['latitude'] - entity['location']['latitude']
    lon_diff = target_entity['location']['longitude'] - entity['location']['longitude']
    angle = math.atan2(lon_diff, lat_diff)
    return angle

def organize_data_by_entity(json_data_list):
    entity_track = {}  # 字典，键为实体名，值为该实体在各个时间步的数据列表

    for time_step_data in json_data_list:
        time = time_step_data['time']  # 获取时间信息
        for entity in time_step_data["entities"]:
            if entity['name'] not in entity_track:
                entity_track[entity['name']] = []
            # 将时间信息加入到实体字典中
            enhanced_entity = dict(entity, time=time)  
            entity_track[entity['name']].append(enhanced_entity)

    return entity_track

# def deduce_policy_from_movements(entity, movements, entities_data):
#     # policy_counts = {policy: 0 for policy in POLICIES}  # 初始化策略计数器
    
#     current = movements[0][0]
#     next = movements[0][1]
#     actual_direction = calculate_actual_direction(current, next)  # 计算实际方向D1
#     friend_entity = find_nearest_entity(current, entities_data, is_enemy=False) #E3
#     enemy_entity = find_nearest_entity(current, entities_data, is_enemy=True) #E2
#     friend_direction_to_target = determine_direction(current, friend_entity) #E1E3
#     enemy_direction_to_target = determine_direction(current, enemy_entity) #E1E2
    
#     policy = "undefined"
    
#     # 打印方向差的绝对值
#     print(f"友方方向差的绝对值: {abs(friend_direction_to_target - actual_direction)}")
#     print(f"敌方方向差的绝对值: {abs(enemy_direction_to_target - actual_direction)}")
#     print(f"math.pi的值：{math.pi}")
    
#     if(abs(friend_direction_to_target - actual_direction) == 0):
#         policy = "near_friend"
#     elif(abs(friend_direction_to_target - actual_direction) == math.pi):
#         policy = "far_from_friend"
#     elif(abs(enemy_direction_to_target - actual_direction) == 0):
#         policy = "near_enemy"
#     elif(abs(enemy_direction_to_target - actual_direction) == math.pi):
#         policy = "far_from_enemy"
        
#     return policy

#     # for i in range(len(movements[0]) - 1):
#     #     current = movements[0][i]
#     #     next = movements[0][i+1]
#     #     for policy in POLICIES:  # 正确迭代所有策略
#     #         expected_direction = calculate_expected_direction(current, entities_data, policy)  # 计算预期方向
#     #         actual_direction = calculate_actual_direction(current, next)  # 计算实际方向

#     #         if actual_direction is not None and expected_direction is not None and abs(expected_direction - actual_direction) <= math.pi / 4:
#     #             policy_counts[policy] += 1  # 对符合预期的策略进行计数

#     # # 过滤没有任何符合次数的策略
#     # effective_policy_counts = {policy: count for policy, count in policy_counts.items() if count > 0}

#     # # 如果没有任何有效的策略计数，返回 None
#     # if not effective_policy_counts:
#     #     return None

#     # # 返回计数最高的策略
#     # return max(effective_policy_counts, key=effective_policy_counts.get)

def deduce_policy_from_movements(entity, movements, entities_data):
    current = movements[0][0]
    next = movements[0][1]
    actual_direction = calculate_actual_direction(current, next)  # 计算实际方向D1
    friend_entity = find_nearest_entity(current, entities_data, is_enemy=False)  # 查找最近的友方E3
    enemy_entity = find_nearest_entity(current, entities_data, is_enemy=True)  # 查找最近的敌方E2
    # print("friend_entity:", friend_entity)
    friend_direction_to_target = determine_direction(current, friend_entity)  # 计算目标方向到友方E1E3
    enemy_direction_to_target = determine_direction(current, enemy_entity)  # 计算目标方向到敌方E1E2
    
    # 计算四种方向之间的偏差
    diff_near_friend = abs(friend_direction_to_target - actual_direction)
    diff_far_friend = abs(diff_near_friend - math.pi)
    diff_near_enemy = abs(enemy_direction_to_target - actual_direction)
    diff_far_enemy = abs(diff_near_enemy - math.pi)

    # 对应成字典
    differences = {
        "near_friend": diff_near_friend,
        "far_from_friend": diff_far_friend,
        "near_enemy": diff_near_enemy,
        "far_from_enemy": diff_far_enemy
    }

    # # 偏差最小的就说明符合这个策略
    # policy = min(differences, key=differences.get)
    # return policy
    
    # 对字典按值进行排序并取前两个策略
    sorted_policies = sorted(differences, key=differences.get)[:2]
    return sorted_policies

def deduce_policy_from_movements2(entity, movements, entities_data):
    current = movements[0][0]
    next = movements[0][1]
    actual_direction = calculate_actual_direction(current, next)  # 计算实际方向D1
    friend_entity = find_nearest_entity(current, entities_data, is_enemy=False)  # 查找最近的友方E3
    enemy_entity = find_nearest_entity(current, entities_data, is_enemy=True)  # 查找最近的敌方E2
    
    friend_direction_to_target = determine_direction(current, friend_entity)  # 计算目标方向到友方E1E3
    enemy_direction_to_target = determine_direction(current, enemy_entity)  # 计算目标方向到敌方E1E2
    
    # 计算四种方向之间的偏差
    diff_near_friend = abs(friend_direction_to_target - actual_direction)
    diff_far_friend = abs(diff_near_friend - math.pi)
    diff_near_enemy = abs(enemy_direction_to_target - actual_direction)
    diff_far_enemy = abs(diff_near_enemy - math.pi)

    # 对应成字典
    differences = {
        "near_friend": diff_near_friend,
        "far_from_friend": diff_far_friend,
        "near_enemy": diff_near_enemy,
        "far_from_enemy": diff_far_enemy
    }

    # # 偏差最小的就说明符合这个策略
    # policy = min(differences, key=differences.get)
    # return policy
    
    # 对字典按值进行排序并取前两个策略
    sorted_policies = sorted(differences, key=differences.get)[:2]
    return sorted_policies

# def monitor_entities(json_data_list):
#     global count_diff  # 引用全局变量 count_diff
#     global total_num   # 引用全局变量 total_num
    
#     anomalous_entities = []
#     entity_track = organize_data_by_entity(json_data_list)  # 组织数据

#     for name, movements in entity_track.items():
#         if len(movements) < 2:  # 至少需要两个时间点来比较
#             continue

#         deduced_policies = []
#         for i in range(len(movements) - 1):
#             current = movements[i]
#             next = movements[i + 1]

#             current_time_step_data = [time_step for time_step in json_data_list if time_step['time'] == current['time']][0]
#             entities_data = current_time_step_data['entities']

#             deduced_policy = deduce_policy_from_movements(name, [(current, next)], entities_data)
#             if deduced_policy:
#                 deduced_policies.append(deduced_policy)

#         # 处理可能为空的 deduced_policies
#         if deduced_policies:
#             final_policy = max(set(deduced_policies), key=deduced_policies.count)
#             actual_policy = movements[0]['policy']
#             total_num += 1

#             if final_policy != actual_policy:
#                 count_diff += 1
#                 anomalous_entities.append({
#                     'entity': name,
#                     'final_policy': final_policy,
#                     'actual_policy': actual_policy
#                 })

#     return anomalous_entities

def monitor_entities(json_data_list, log_entries):
    global count_diff  # 引用全局变量 count_diff
    global total_num   # 引用全局变量 total_num
    global time_count_diff
    global count_same
    global count_run
    
    anomalous_entities = []
    entity_track = organize_data_by_entity(json_data_list)  # 组织数据
    
    for name, movements in entity_track.items():
        if len(movements) < 2:  # 至少需要两个时间点来比较
            continue
        deduced_policies = []
        actual_policy = movements[0]['policy']
        for i in range(len(movements) - 1):
            count_run = count_run + 1
            current = movements[i]
            next_movement = movements[i + 1]        
            current_time_step_data = [time_step for time_step in json_data_list if time_step['time'] == current['time']][0]
            entities_data = current_time_step_data['entities']
            # print("time:{},entities:{}".format(current['time'], entities_data))
            # deduced_policy = deduce_policy_from_movements(name, [(current, next_movement)], entities_data)
            deduced_policy = deduce_policy_from_movements(name, [(current, next_movement)], entities_data)
            if actual_policy not in deduced_policy:
            # if deduced_policy != actual_policy:
                # 打印不一致的信息
                time_count_diff += 1
                # print(f"实体: {name}, 时间片: {movements[i]['time']}, 推断策略: {deduced_policy}, 实际策略: {actual_policy}")
                # 检查日志中是否有与实体名称和时间片同时匹配的记录
                log_record = next((entry for entry in log_entries if entry['entity'] == name and entry['current_time'] == current['time']), None)
                if log_record:
                    count_same += 1  # 如果存在记录，则增加计数器
            if deduced_policy[0]:
                deduced_policies.append(deduced_policy[0])
        # 处理可能为空的 deduced_policies
        if deduced_policies:
            final_policy = max(set(deduced_policies), key=deduced_policies.count)
            total_num += 1
            if final_policy != actual_policy:
                count_diff += 1
                anomalous_entities.append({
                    'entity': name,
                    'final_policy': final_policy,
                    'actual_policy': actual_policy
                })
    return anomalous_entities

def monitor_entities2(json_data_list):
    global count_diff  # 引用全局变量 count_diff
    global total_num   # 引用全局变量 total_num
    global time_count_diff
    anomalous_entities = []
    entity_track = organize_data_by_entity(json_data_list)  # 组织数据
    for name, movements in entity_track.items():
        if len(movements) < 2:  # 至少需要两个时间点来比较
            continue
        for i in range(len(movements) - 1):
            current = movements[i]
            next_movement = movements[i + 1]           
            current_time_step_data = [time_step for time_step in json_data_list if time_step['time'] == current['time']][0]
            entities_data = current_time_step_data['entities']
            deduced_policy = deduce_policy_from_movements2(name, [(current, next_movement)], entities_data)
            actual_policy = current['policy']          
            # if deduced_policy != actual_policy:
            if actual_policy not in deduced_policy:
                # 更新不一致计数
                time_count_diff += 1
                print(f"Entity: {name}, Time slice: {current['time']}, Location: (Longitude: {current['location']['longitude']}, Latitude: {current['location']['latitude']}, Altitude: {current['location']['altitude']}), Deduced policy: {deduced_policy}, Actual policy: {actual_policy}")
                
                # 添加不一致的实体信息到列表
                anomalous_entities.append({
                    'entity': name,
                    'category': current['category'],
                    'time_slice': current['time'],
                    'location': current['location'],
                    'deduced_policy': deduced_policy,
                    'actual_policy': actual_policy
                })
    return anomalous_entities

def calculate_expected_direction(entity, entities_data, policy):
    # 找到最近的友方或敌方实体
    if policy == "near_friend" or policy == "far_from_friend":
        target_entity = find_nearest_entity(entity, entities_data, is_enemy=False)
    elif policy == "near_enemy" or policy == "far_from_enemy":
        target_entity = find_nearest_entity(entity, entities_data, is_enemy=True)
    
    # 如果没有找到目标实体，返回 None 或者其他表示没有目标的值
    if not target_entity:
        return None

    # 计算朝向目标实体的方向
    direction_to_target = determine_direction(entity, target_entity)
    
    # 根据策略调整方向
    if policy == "far_from_friend" or policy == "far_from_enemy":
        # 如果策略是远离，将方向逆反
        direction_to_target += math.pi
    
    return direction_to_target

def calculate_actual_direction(current, next):
    # 获取两个时间步中的位置数据
    previous_location = current['location']
    current_location = next['location']
    
    # 提取经纬度
    lat1, lon1 = math.radians(previous_location['latitude']), math.radians(previous_location['longitude'])
    lat2, lon2 = math.radians(current_location['latitude']), math.radians(current_location['longitude'])

    # 计算两点之间的经度和纬度差值
    dlat = lat2 - lat1
    dlon = lon2 - lon1

    # 计算实际的移动方向，角度从 -π 到 π
    actual_direction = math.atan2(dlon, dlat)
    return actual_direction


def generate_entities_with_updated_policy(json_data_list):
    # print(json_data_list)
    updated_entities = []
    entity_track = organize_data_by_entity(json_data_list)  # 组织数据
    # print(entity_track)

    for name, movements in entity_track.items():
        if len(movements) < 2:  # 至少需要两个时间点来比较
            continue
        deduced_policies = []
        actual_policy = movements[-1]['policy']
        entity_info = movements[-1]  # 使用最后一个记录作为基础信息

        for i in range(len(movements) - 1):
            current = movements[i]
            next_movement = movements[i + 1]
            current_time_step_data = [time_step for time_step in json_data_list if time_step['time'] == current['time']][0]
            entities_data = current_time_step_data['entities']
            # print("time:{},entities:{}".format(current['time'], entities_data))

            deduced_policy = deduce_policy_from_movements(name, [(current, next_movement)], entities_data)

            if deduced_policy[0]:
                deduced_policies.append(deduced_policy[0])

        if deduced_policies:
            final_policy = max(set(deduced_policies), key=deduced_policies.count)
            entity_info['policy'] = final_policy  # 直接更新policy字段
        else:
            entity_info['policy'] = actual_policy  # 如果没有推断出新策略，保持原策略

        # 添加完整的实体信息到列表
        updated_entities.append(entity_info)
    
    # 过滤掉时间
    # 过滤掉每个实体字典中的 'time' 键
    # print(updated_entities)
    # final_time = updated_entities[-1]['time']
    # print(final_time)
    final_time = ""
    for entity in updated_entities:
        if 'time' in entity:
            final_time = entity['time']
            del entity['time']
            
    # print(f"final time: {final_time}")
            
    # 使用 strptime 将字符串转换为 datetime 对象
    time_obj = datetime.strptime(final_time, "%Y-%m-%d %H:%M:%S")
    
    # print(updated_entities)
    
    return updated_entities, time_obj


if __name__ == "__main__":
    # 指定数据文件存放的目录
    # data_directory = "data_test/"
    # data_directory = "/root/yhz/code/situation_awareness/backend/data_test/"
    data_directory = "/root/yhz/code/situation_awareness/backend/upload/generated_data_camp3f2b3af0-9278-11ef-9019-d0946653d4f6.json"
    with open(data_directory, 'r') as file:
        all_json_data = json.load(file)
    
    # # 读取所有JSON文件中的数据
    # all_json_data = read_json_files(data_directory)
    # 读取前5个JSON文件
    # all_json_data = read_first_n_json_files(data_directory, num_files=1)
    
    # # 一次性加载日志文件
    # # backend/
    # with open('entity_movements_log.json', 'r') as file:
    #     log_entries = json.load(file)
    
    # 第二个接口测试
    updated_entities, time_obj = generate_entities_with_updated_policy(all_json_data)
    print(updated_entities)
    # motified_data = read_entities_from_data(updated_entities)
    # print(motified_data)
    # json_data_list = generate_json_data_from_initial(updated_entities, time_obj, 10)
    # print(json_data_list)
    
    json_data_list_entity0 = generate_json_data_for_entity(updated_entities, time_obj, 10, "Entity0")
    # json_data_list_entity0 = generate_json_data_for_entity(updated_entities, time_obj, 10)
    print(json_data_list_entity0)
    
        
    # # 执行异常检测
    # anomalous_entities = monitor_entities(all_json_data, log_entries)
    # # anomalous_entities = monitor_entities2(all_json_data)
    # # if anomalous_entities:
    # #     print("Abnormal entities found:", anomalous_entities)
    # # else:
    # #     print("No abnormal entities found.")              
        
    # # # 输出不一致数量和处理过的总策略数
    # # print(f"总不一致数: {count_diff}")
    # # print(f"总处理策略数: {total_num}")
    # # print(f"时间片里策略不一致的数量：{time_count_diff}")
    # # print(f"和生成数据中相同的异常：{count_same}")
    # # print(f"总运行次数：{count_run}")
    
    # # 假设正例是正常，负例是异常
    # # count_same是真负例，TN
    # # time_count_diff是预测出的负例
    # # log_count_read是实际上的负例
    # # TN = count_same
    # # FN = time_count_diff - count_same
    # # FP = log_count_read - count_same
    # # TP = count_run - TN - FN - FP
    
    
    
    # # 指定要读取的文件路径
    # file_path = 'log_data.json'

    # # 从 JSON 文件读取数据
    # with open(file_path, 'r') as file:
    #     data_loaded = json.load(file)

    # # 访问读取的数据
    # log_count_read = data_loaded["log_count"]
    # # print(f"从文件读取的异常条目数：{log_count_read}")
    # # recall = count_same / log_count_read
    # # accuracy = (1600 - time_count_diff) / 1600
    # policy_precision = (total_num - count_diff) / total_num
    # # print(f"recall = {recall}")
    # # print(f"accuracy = {accuracy}")
    # # print(f"policy的预测准确率 = {policy_precision}")
    
    # # 指定输出文件
    # output_file = "policy_precision_output.txt"

    # # 将结果追加到文件中
    # with open(output_file, "a") as file:
    #     file.write(f"{policy_precision}\n")
    
    # TN = count_same
    # FN = time_count_diff - count_same
    # FP = log_count_read - count_same
    # TP = count_run - TN - FN - FP
    # precision = TP / (TP + FP)
    # recall = TP / (TP + FN)
    # accuracy = (TP + TN) / (TP + TN + FP + FN)
    # # print(f"precision = {precision}")
    # # print(f"recall = {recall}")
    # # print(f"accuracy = {accuracy}")
    
    # # 指定输出文件
    # output_file2 = "precision_output.txt"
    # output_file3 = "recall_output.txt"
    # output_file4 = "accuracy_output.txt"

    # # 将结果追加到文件中
    # with open(output_file2, "a") as file:
    #     file.write(f"{precision}\n")
        
    # with open(output_file3, "a") as file:
    #     file.write(f"{recall}\n") 
        
    # with open(output_file4, "a") as file:
    #     file.write(f"{accuracy}\n")
