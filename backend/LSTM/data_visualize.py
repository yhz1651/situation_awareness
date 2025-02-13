import numpy as np
from keras.layers.core import Dense, Activation, Dropout
from keras.layers import LSTM
from keras.models import Sequential, load_model
from keras.callbacks import Callback
import keras.backend as KTF
import tensorflow as tf
import pandas as pd
import os
import keras.callbacks
import matplotlib.pyplot as plt
import json
import matplotlib.pyplot as plt

print("========== Start ==========")

# JSON文件的路径
json_road = r"data/large_scale_enemy_advantage_1.json"
# json_road = r"data/large_scale_self_advantage_1.json"
# json_road = r"data/small_scale_self_advantage_1.json"

# 可视化的实体数量
num_use_enti = 200 # large
# num_use_enti = 50 # small


# 读取JSON文件
with open(json_road, 'r') as f:      
    data = json.load(f)
    
# 轨迹数据，例如一个包含经度和纬度的列表
longitude = []
latitude = []
for i in range(200): # 
    longitude.append([])
    latitude.append([])

# 打印读取的 JSON 数据
# 获取 'name' 字段的值
for i in range(len(data)):
    data_now = data[i]
    time0 = data_now['time']
    entities = data_now['entities']

    # for j in range(len(data_now)):
    for j in range(0, num_use_enti): # 
        policy = entities[j]['policy']
        ent0 = entities[j]
        ent0_loca = ent0['location']
        # print("ent0_loca:", ent0_loca) # 输出经度，纬度，高度
        
        longitude[j].append(ent0_loca['longitude'])
        latitude[j].append(ent0_loca['latitude'])
        # 高度暂时不用可视化
    

# 数据可视化
# 绘制轨迹数据
plt.figure(figsize=(8, 6))

for j in range(0, num_use_enti):
    plt.plot(longitude[j], latitude[j], marker='o', linestyle='-')

plt.xlabel('Longitude')
plt.ylabel('Latitude')
plt.title('Trajectory Visualization')
plt.grid(True)

# plt.show()
name = 'data_visual_enti' + str(num_use_enti) + '.png'
save_road = r'LSTM/result/data_visual/' + name
plt.savefig(save_road) # 保存结果的图片
print("saved successfully at " + save_road)


