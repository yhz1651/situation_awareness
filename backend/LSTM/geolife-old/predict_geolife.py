from math import sin, asin, cos, radians, fabs, sqrt 
from keras.layers.core import Dense, Activation, Dropout
from keras.layers import LSTM
from keras.models import Sequential, load_model
from keras.callbacks import Callback
import keras.backend as KTF
import keras.callbacks
import numpy as np
import tensorflow as tf
import pandas as pd
import os
import matplotlib.pyplot as plt
import copy
import json


def rmse(predictions, targets):
    return np.sqrt(((predictions - targets) ** 2).mean())
 

def mse(predictions, targets):
    return ((predictions - targets) ** 2).mean()
 
 
def reshape_y_hat(y_hat, dim):
    re_y = []
    i = 0
    while i < len(y_hat):
        tmp = []
        for j in range(dim):
            tmp.append(y_hat[i + j])
        i = i + dim
        re_y.append(tmp)
    re_y = np.array(re_y, dtype='float64')
    return re_y
 
# 数据切分
def data_set(dataset,test_num):# 创建时间序列数据样本
  dataX,dataY=[],[]
  for i in range(len(dataset)-test_num-1):
        a=dataset.iloc[i:(i+test_num)]
        dataX.append(a)
        dataY.append(dataset.iloc[i+test_num])
  return np.array(dataX),np.array(dataY)
 
 
# 多维反归一化
def FNormalizeMult(data, normalize):
    data = np.array(data, dtype='float64')
    # 列
    for i in range(0, data.shape[1]):
        listlow = normalize[i, 0]
        listhigh = normalize[i, 1]
        delta = listhigh - listlow
        print("listlow, listhigh, delta", listlow, listhigh, delta)
        # 行
        if delta != 0:
            for j in range(0, data.shape[0]):
                data[j, i] = data[j, i] * delta + listlow
 
    return data
 
 
# 使用训练数据的归一化
def NormalizeMultUseData(data, normalize):
    for i in range(0, data.shape[1]):
 
        listlow = normalize[i, 0]
        listhigh = normalize[i, 1]
        delta = listhigh - listlow
 
        if delta != 0:
            for j in range(0, data.shape[0]):
                data[j, i] = (data[j, i] - listlow) / delta
 
    return data
 


# 计算两个经纬度之间的直线距离
def hav(theta):
    s = sin(theta / 2)
    return s * s
 

def get_distance_hav(lat0, lng0, lat1, lng1):
    # "用haversine公式计算球面两点间的距离。"
    # 经纬度转换成弧度
    lat0 = radians(lat0)
    lat1 = radians(lat1)
    lng0 = radians(lng0)
    lng1 = radians(lng1)
 
    dlng = fabs(lng0 - lng1)
    dlat = fabs(lat0 - lat1)
    h = hav(dlat) + cos(lat0) * cos(lat1) * hav(dlng)
    distance = 2 * EARTH_RADIUS * asin(sqrt(h))
    return distance
 


# 设定为自增长
config=tf.compat.v1.ConfigProto()
config.gpu_options.allow_growth = True
session=tf.compat.v1.Session(config=config)
KTF.tf.compat.v1.keras.backend.set_session(session)
 
EARTH_RADIUS = 6371  # 地球平均半径，6371km

if __name__ == '__main__':
    test_num = 6 # 
    per_num = 1
    #
    # road_test = r'LSTM/Geolife-data-test.plt' 
    road_test = r'LSTM/input-data-test.txt' # 读取测试数据
    yuanshi=pd.read_csv(road_test, sep=',',skiprows=6, usecols=[0, 1]) # 
    # test1.plt为空时，会有以下报错：
    # pandas.errors.EmptyDataError: No columns to parse from file，文件中没有列名或者数据为空
    
    #
    print("yuanshi.shape =", yuanshi.shape)
    
    ex_data = pd.read_csv(road_test, sep=',',skiprows=6, usecols=[0, 1]) # 原始数据
    data, dataY = data_set(ex_data, test_num)
    data.dtype = 'float64'
    y = dataY
    
    # 归一化参数的路径
    normalize_road = r"./LSTM/model/traj_model_trueNorm_v2.npy" 
    # normalize_road = r"./LSTM/model/traj_model_trueNorm.npy"
    
    # 模型的路径
    model_road = r"./LSTM/model/traj_model_120_v2.h5" 
    # model_road = r"./LSTM/model/traj_model_120.h5" 
    
    # 归一化
    normalize = np.load(normalize_road)
    data_guiyi=[]
    for i in range (len(data)):
        data[i]=list(NormalizeMultUseData(data[i], normalize))
        data_guiyi.append(data[i])
    
    # 加载模型
    model = load_model(model_road)
    
    y_hat=[]
    for i in range(len(data)):
        test_X = data_guiyi[i].reshape(1, data_guiyi[i].shape[0], data_guiyi[i].shape[1])
        dd = model.predict(test_X) # 
        dd = dd.reshape(dd.shape[1])
        dd = reshape_y_hat(dd, 2)
        dd = FNormalizeMult(dd, normalize)
        dd=dd.tolist()
        y_hat.append(dd[0])
    y_hat=np.array(y_hat)
    
    def generate_geojson(y_hat,savePath):
        coordinates = [[float(coord[1]), float(coord[0])] for coord in y_hat]
        coordinates1 = [[float(coord[1]), float(coord[0])] for coord in yuanshi.values]
        
        coordinates.insert(0, coordinates1[-1])
        # 创建 Feature 对象
        feature = {
            'type': 'Feature',
        #     'properties': {
        #     'stroke': '#FFFFFF',  # 线条颜色为蓝色
        #     'stroke-width': 3,  # 线条宽度为 3
        #     'stroke-opacity': 0.5,  # 线条透明度为 0.5
        #     'stroke-dasharray': '5,10'  # 虚线样式为每 10 个像素实线，5 个像素空白
        # },
            'geometry': {
                'type': 'LineString',
                # 'type': 'MultiPoint',
                'coordinates': coordinates
            }
        }

        save_path = savePath

        geojson = {
                'type': 'FeatureCollection',
                'features': [feature]
            }

        # 检查文件是否存在
        if os.path.exists(save_path):
            # 如果文件已存在，则删除文件
            os.remove(save_path)

        # 保存为 GeoJSON 文件
        with open(save_path, 'w') as outfile:
            # print('ok')
            json.dump(geojson, outfile)

    def generate_geojson1(y_hat,savePath):
        coordinates = [[float(coord[1]), float(coord[0])] for coord in y_hat]

        # 创建 Feature 对象
        feature = {
            'type': 'Feature',
            'properties': {
            'stroke': '#0000FF',  # 线条颜色为蓝色
            'stroke-width': 3,  # 线条宽度为 3
            'stroke-opacity': 0.5,  # 线条透明度为 0.5
            'stroke-dasharray': '5,10'  # 虚线样式为每 10 个像素实线，5 个像素空白
        },
            'geometry': {
                'type': 'LineString',
                'coordinates': coordinates
            }
        }

        save_path = savePath

        geojson = {
                'type': 'FeatureCollection',
                'features': [feature]
            }

        # 检查文件是否存在
        if os.path.exists(save_path):
            # 如果文件已存在，则删除文件
            os.remove(save_path)

        # 保存为 GeoJSON 文件
        with open(save_path, 'w') as outfile:
            # print('ok')
            json.dump(geojson, outfile)
            
    # print(y_hat)
    # print(yuanshi)
    # 将 y_hat 传入 generate_geojson 函数生成 GeoJSON 文件
    path_road0 = r'LSTM/path.geojson' # r'path.geojson'
    path_road1 = r'LSTM/path1.geojson' # r'path1.geojson'
    generate_geojson(y_hat, path_road0)
    generate_geojson1(yuanshi.values, path_road1)


    # 画测试样本数据库
    # plt.rcParams['font.sans-serif'] = ['simhei']  # 用来正常显示中文标签
    print("len(y_hat) =", len(y_hat))

    
    # p1 = plt.scatter(yuanshi.values[:, 1], yuanshi.values[:, 0], c='r', marker='o', label='Identification results') # 原始轨迹
    # p2 = plt.scatter(y_hat[:, 1], y_hat[:, 0], c='b', marker='o', label='Forcast results') # 预测的轨迹
    
    plt.figure(figsize=(8, 6))
    # plt.plot(data['longitude'], data['latitude'], marker='o', linestyle='-')
    p1 = plt.plot(yuanshi.values[:, 1], yuanshi.values[:, 0], marker='o', linestyle='-')
    p2 = plt.plot(y_hat[:, 1], y_hat[:, 0], marker='o', linestyle='-')
    plt.xlabel('Longitude')
    plt.ylabel('Latitude')
    plt.title('Trajectory Visualization')
    plt.grid(True)
    
    
    plt.legend(loc='upper left')
    plt.grid()
    # plt.show()
    # save_road = r'result/predict.png'
    save_road = r'LSTM/result/predict_v2.png'
    plt.savefig(save_road) # 保存结果的图片
    print("saved successfully at " + save_road)
