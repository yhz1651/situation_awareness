import os
import json
from datetime import datetime

def read_json_data(file_path):
    with open(file_path, 'r') as file:
        data = json.load(file)
    return data

def format_data_to_csv(json_data, output_folder):
    # 检查输出文件夹是否存在，如果不存在则创建
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    for record in json_data:
        time_str = record['time']
        entities = record['entities']
        date_time_obj = datetime.strptime(time_str, "%Y-%m-%d %H:%M:%S")
        date_time = date_time_obj.strftime("%Y-%m-%d %H:%M:%S")

        for entity in entities:
            entity_id = entity['name']
            longitude = entity['location']['longitude']
            latitude = entity['location']['latitude']

            # 构建一行数据格式：ID, 时间, 经度, 纬度
            line = f"{entity_id},{date_time},{longitude},{latitude}\n"

            # 保存数据到相应的文件（每个实体一个文件）
            with open(f"{output_folder}/{entity_id}.csv", 'a') as file:
                file.write(line)

# 示例使用
json_data = read_json_data('data_test/small_scale_enemy_advantage_1.json')
format_data_to_csv(json_data, 'output_folder')
