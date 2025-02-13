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
import change_to_txt
file_id = change_to_txt.file_id
entity_id = change_to_txt.entity_id

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

    road_test = r'LSTM/input-data-test.txt' # 读取测试数据
    yuanshi=pd.read_csv(road_test, sep=',',skiprows=6, usecols=[0, 1]) # 
    # test1.plt为空时，会有以下报错：
    # pandas.errors.EmptyDataError: No columns to parse from file，文件中没有列名或者数据为空
    
    
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
    

    def calculate_fde(real_trajectory, predicted_trajectory):
        """  
        计算真实轨迹和预测轨迹之间的终点位置误差（FDE）。  
        
        参数:  
        real_trajectory (np.ndarray): 真实轨迹的numpy数组，形状为(N, 2)，其中N是时间步数，2是x和y坐标。  
        predicted_trajectory (np.ndarray): 预测轨迹的numpy数组，形状与real_trajectory相同。  
        
        返回:  
        fde (float): 终点位置误差。  
        """  
        # 确保两个轨迹都有相同的长度
        assert real_trajectory.shape == predicted_trajectory.shape, "轨迹长度必须相同"  
        
        # 终点位置误差只需要关注最后一个点。提取真实轨迹和预测轨迹的最后一个点  
        real_last_point = real_trajectory[-1]  
        predicted_last_point = predicted_trajectory[-1]  
        
        # 计算两个点之间的欧几里得距离
        fde = np.linalg.norm(real_last_point - predicted_last_point)  
        
        return fde  
    

    def calculate_ade(real_trajectory, predicted_trajectory):  
        """  
        计算真实轨迹和预测轨迹之间的平均位置误差（ADE）。  
        
        参数:  
        real_trajectory (np.ndarray): 真实轨迹的numpy数组，形状为(N, 2)，其中N是时间步数，2是x和y坐标。  
        predicted_trajectory (np.ndarray): 预测轨迹的numpy数组，形状与real_trajectory相同。  
        
        返回:  
        ade (float): 平均位置误差。  
        """  
        # 确保两个轨迹都有相同的长度  
        assert real_trajectory.shape == predicted_trajectory.shape, "轨迹长度必须相同"  
        
        # 计算每个时间步的误差  
        errors = np.linalg.norm(real_trajectory - predicted_trajectory, axis=1)  
        
        # 计算平均误差  
        ade = np.mean(errors)  
        
        return ade  
    
    def calculate_acc(real_trajectory, predicted_trajectory):  
        """  
        计算真实轨迹和预测轨迹之间的准确率(Accuracy) 
        
        参数:  
        real_trajectory (np.ndarray): 真实轨迹的numpy数组，形状为(N, 2)，其中N是时间步数，2是x和y坐标。  
        predicted_trajectory (np.ndarray): 预测轨迹的numpy数组，形状与real_trajectory相同。  
        
        返回:  
        acc (float): 准确率
        """  
        # 确保两个轨迹都有相同的长度  
        assert real_trajectory.shape == predicted_trajectory.shape, "轨迹长度必须相同"  
        
        # 计算每个时间步的误差  
        errors = np.linalg.norm(real_trajectory - predicted_trajectory, axis=1)  
        # print("errors: ", errors) # 输出误差
        
        # 阈值, 误差小于等于阈值视为预测成功
        # threshold = 0.5
        threshold = 0.2
        # threshold = 0.1
        
        # threshold 0.040, ACC = 0.952
        # threshold 0.035, ACC = 0.904
        # threshold 0.020, ACC = 0.571
        
        # 计算准确率
        num = 0
        len1 = len(errors)
        for i in errors:
            if i<threshold: 
                num+=1
        
        acc = 1.0*num/len1
        
        return acc
    
    
    # 画测试样本数据库
    plt.figure(figsize=(8, 6))
    p1 = plt.plot(yuanshi.values[:, 1], yuanshi.values[:, 0], marker='o', linestyle='-')
    p2 = plt.plot(y_hat[:, 1], y_hat[:, 0], marker='o', linestyle='-')
    plt.xlabel('Longitude')
    plt.ylabel('Latitude')
    plt.title('Trajectory Visualization')
    plt.grid(True)
    plt.legend(loc='upper left')
    plt.grid()
    save_road = r'LSTM/result/predict_v2-file'+str(file_id)+'-ent'+str(entity_id)+'.png'
    plt.savefig(save_road) # 保存结果的图片
    print("saved successfully at " + save_road)
    
    ade = 0.0
    fde = 0.0
    gt = yuanshi.values[7:]
    # print("len(yuanshi.values) =",len(yuanshi.values)) # 28
    # print("len(gt) =",len(gt)) # 21
    # print("len(y_hat) =",len(y_hat)) # 21
    
    ade = calculate_ade(np.array(gt), np.array(y_hat)) 
    fde = calculate_fde(np.array(gt), np.array(y_hat)) 
    acc = calculate_acc(np.array(gt), np.array(y_hat)) 
    
    print("ADE =",ade,", FDE =",fde,"ACC =",acc) # output the result
    print("%.5f %.5f %.5f" % (ade,fde,acc))
    