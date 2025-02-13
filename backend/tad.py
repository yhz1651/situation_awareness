import numpy as np
import json
import matplotlib.pyplot as plt
import pandas as pd

import json
import matplotlib.pyplot as plt
import pandas as pd

# 假设你的JSON数据存储在名为'trajectory_data.json'的文件中
# 首先，我们读取这个JSON文件
with open('data/small_scale_enemy_advantage_1.json', 'r') as file:
    data = json.load(file)

# 正确地从顶层JSON对象中提取时间戳
timestamp = data['time']

# 初始化一个空列表来存储所有实体的数据
entities_data = []

# 遍历每个实体，提取位置信息，并添加到列表中
for entity in data['entities']:
    if entity['enemy']:  # 假设我们只对敌方实体的轨迹感兴趣
        # 将实体的数据添加到列表中
        entities_data.append({
            'name': entity['name'],
            'longitude': entity['location']['longitude'],
            'latitude': entity['location']['latitude'],
            'altitude': entity['location']['altitude'],
            'time': timestamp
        })

# 将列表转换为DataFrame
trajectory_df = pd.DataFrame(entities_data)

# 为了可视化，我们绘制经度和纬度
# 这里我们创建一个图表，每个敌方实体的轨迹用不同的颜色表示
for name, group in trajectory_df.groupby('name'):
    group.plot(x='longitude', y='latitude', kind='line', style='o-', figsize=(10, 6), label=name)

# 设置图表标题和坐标轴标签
plt.title('Trajectory Visualization')
plt.xlabel('Longitude')
plt.ylabel('Latitude')

# 显示图例
plt.legend()

# 显示图表
plt.show()


# 假设的距离阈值，用于判断是否违反策略
# 这些阈值可以根据实际情况进行调整
FRIEND_THRESHOLD = 20  # 与友方的距离阈值
ENEMY_THRESHOLD = 10   # 与敌方的距离阈值

# 模拟的友方和敌方位置
# 假设友方在(0,0,0)，敌方在(100,100,100)
friend_location = np.array([0, 0, 0])
enemy_location = np.array([100, 100, 100])

# 定义一个函数来计算两点之间的欧氏距离
def calculate_distance(point1, point2):
    return np.sqrt(np.sum((point1 - point2) ** 2))

# 定义一个函数来检测异常
def detect_anomalies(entities, friend_location, enemy_location, friend_threshold, enemy_threshold):
    anomalies = []
    for entity in entities:
        # 计算实体与友方和敌方的距离
        distance_to_friend = calculate_distance(entity['location'], friend_location)
        distance_to_enemy = calculate_distance(entity['location'], enemy_location)
        
        # 根据策略判断是否异常
        if entity['policy'] == 'near_friend' and distance_to_friend > friend_threshold:
            anomalies.append((entity['name'], 'Too far from friend'))
        elif entity['policy'] == 'far_from_enemy' and distance_to_enemy < enemy_threshold:
            anomalies.append((entity['name'], 'Too close to enemy'))
        elif entity['policy'] == 'far_from_friend' and distance_to_friend < friend_threshold:
            anomalies.append((entity['name'], 'Too close to friend'))
        elif entity['policy'] == 'near_enemy' and distance_to_enemy > enemy_threshold:
            anomalies.append((entity['name'], 'Too far from enemy'))
    return anomalies

# # 假设JSON数据存储在'data.json'文件中
# with open('data/small_scale_enemy_advantage_1.json', 'r') as file:
#     data = json.load(file)

# # 现在data变量包含了JSON文件中的数据，可以像之前一样访问
# print("Time:", data["time"])

# # 检测异常
# anomalies = detect_anomalies(data['entities'], friend_location, enemy_location, FRIEND_THRESHOLD, ENEMY_THRESHOLD)

# # 打印异常结果
# for anomaly in anomalies:
#     print(f"Anomaly detected: {anomaly[0]} - {anomaly[1]}")