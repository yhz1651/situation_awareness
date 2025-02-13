import os
import csv
from anomaly_detection import find_nearest_entity, calculate_distance, read_json_files

def calculate_relative_distances(entity, entities):
    # 找到最近的友方实体
    nearest_friend = find_nearest_entity(entity, entities, is_enemy=False)
    # 找到最近的敌方实体
    nearest_enemy = find_nearest_entity(entity, entities, is_enemy=True)

    # 如果存在最近的友方实体，计算距离，否则返回None
    distance_to_nearest_friend = calculate_distance(entity, nearest_friend) if nearest_friend else None
    # 如果存在最近的敌方实体，计算距离，否则返回None
    distance_to_nearest_enemy = calculate_distance(entity, nearest_enemy) if nearest_enemy else None

    # 返回两个距离的差异，如果没有找到相应的实体，则可能返回None
    return (distance_to_nearest_friend, distance_to_nearest_enemy)


def organize_data_by_entity(json_data_list):
    entity_data_dict = {}
    for time_step_data in json_data_list:
        time = time_step_data['time']  # 获取时间信息
        for entity in time_step_data["entities"]:
            # 计算与最近友方和敌方的距离差
            distances = calculate_relative_distances(entity, time_step_data["entities"])
            # 创建一个字典来保存所有需要的信息
            entity_data = {
                "time": time,
                "distance_to_nearest_friend": distances[0],
                "distance_to_nearest_enemy": distances[1]
            }
            # 根据实体名字组织数据
            if entity["name"] not in entity_data_dict:
                entity_data_dict[entity["name"]] = []
            entity_data_dict[entity["name"]].append(entity_data)
    return entity_data_dict


def write_individual_entity_files(entity_data_dict, directory):
    # 确保目标文件夹存在，如果不存在则创建
    if not os.path.exists(directory):
        os.makedirs(directory)
    
    # 为每个实体生成CSV文件
    for entity_name, data in entity_data_dict.items():
        file_name = os.path.join(directory, f"{entity_name}.csv")
        with open(file_name, mode='w', newline='') as file:
            fieldnames = ['time', 'distance_to_nearest_friend', 'distance_to_nearest_enemy']
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()  # 写入头部
            for row in data:
                writer.writerow(row)  # 写入每一行数据


def add_relative_distance_features(json_data_list):
    data_for_csv = []
    for time_step_data in json_data_list:
        time = time_step_data['time']  # 获取时间信息
        for entity in time_step_data["entities"]:
            # 计算与最近友方和敌方的距离差
            distances = calculate_relative_distances(entity, time_step_data["entities"])
            # 创建一个字典来保存所有需要的信息
            entity_data = {
                "entity_name": entity["name"],
                "time": time,
                "distance_to_nearest_friend": distances[0],
                "distance_to_nearest_enemy": distances[1]
            }
            data_for_csv.append(entity_data)
    return data_for_csv


def write_data_to_csv(data, file_name):
    # 指定CSV文件的头部
    fieldnames = ['entity_name', 'time', 'distance_to_nearest_friend', 'distance_to_nearest_enemy']
    # 打开文件，准备写入
    with open(file_name, mode='w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()  # 写入头部
        for row in data:
            writer.writerow(row)  # 写入每一行数据

# 使用你的JSON数据
data_directory = "data_test/"
all_json_data = read_json_files(data_directory)

# distance_features = add_relative_distance_features(all_json_data)
# # 写入CSV文件
# write_data_to_csv(distance_features, "relative_distances.csv")


organized_data = organize_data_by_entity(all_json_data)
# 指定存放CSV文件的目录
output_directory = "output_entities_csv"
write_individual_entity_files(organized_data, output_directory)



