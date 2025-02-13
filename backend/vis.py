import json
import matplotlib.pyplot as plt
import pandas as pd

def read_json(file_path):
    with open(file_path, "r") as file:
        return json.load(file)

def extract_lat_lon_by_entity(json_data):
    entity_dict = {}
    for time_data in json_data:
        for entity in time_data["entities"]:
            entity_id = entity["name"]
            latitude = entity["location"]["latitude"]
            longitude = entity["location"]["longitude"]
            enemy = entity["enemy"]
            if entity_id not in entity_dict:
                entity_dict[entity_id] = {"latitudes": [], "longitudes": [], "enemy": enemy}
            entity_dict[entity_id]["latitudes"].append(latitude)
            entity_dict[entity_id]["longitudes"].append(longitude)
    return entity_dict

def visualize_lat_lon(entity_dict):
    plt.figure(figsize=(18, 12))
    for entity_id, coords in entity_dict.items():
        color = 'red' if coords["enemy"] else 'green'
        plt.plot(coords["longitudes"], coords["latitudes"], marker='o', markersize=3, linestyle='-', linewidth=1, label=entity_id, color=color)
    plt.title("Entity Locations and Trajectories")
    plt.xlabel("Longitude")
    plt.ylabel("Latitude")
    # plt.xlim(22, 40)  # 限制经度范围
    # plt.ylim(44, 52)   # 限制纬度范围
    plt.grid(True)
    # plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left', fontsize='small')
    plt.savefig("entity_locations.png", bbox_inches='tight')  # 保存图片
    plt.show()

if __name__ == "__main__":
    # file_path = "backend/data/large_scale_self_advantage_1.json"  # 修改为你的文件路径
    file_path = "backend/data/small_scale_self_advantage_1.json"  # 修改为你的文件路径
    json_data = read_json(file_path)
    entity_dict = extract_lat_lon_by_entity(json_data)
    visualize_lat_lon(entity_dict)
