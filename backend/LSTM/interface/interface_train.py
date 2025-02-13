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
# import change_to_txt # 初始化数据集成txt格式
# change_to_txt.work() # 初始化数据集成txt格式

def work(num_epochs = 10): # 迭代次数num_epochs,范围[10,200]
    # 设置模型参数
    # 设定为自增长
    os.environ['CUDA_VISIBLE_DEVICES'] = '0'
    config=tf.compat.v1.ConfigProto()
    config.gpu_options.allow_growth = True
    session=tf.compat.v1.Session(config=config)
    tf.compat.v1.keras.backend.set_session(session)


    # 设置模型架构
    def trainModel(train_X, train_Y):
        '''
        trainX, trainY: 训练LSTM模型所需要的数据
        '''
        model = Sequential()
        model.add(LSTM(
            120,
            input_shape=(train_X.shape[1], train_X.shape[2]),
            return_sequences=True))
        model.add(Dropout(0.3))
    
        model.add(LSTM(
            120,
            return_sequences=False))
        model.add(Dropout(0.3))
    
        model.add(Dense(
            train_Y.shape[1]))
        model.add(Activation("relu"))
    
        model.compile(loss='mse', optimizer='adam', metrics=['acc'])
        model.fit(train_X, train_Y, epochs=num_epochs, batch_size=64, verbose=1)
        model.summary()
    
        return model


    def NormalizeMult(data, set_range):
        '''
        返回归一化后的数据和最大最小值
        '''
        normalize = np.arange(2 * data.shape[1], dtype='float64')
        normalize = normalize.reshape(data.shape[1], 2)
    
        for i in range(0, data.shape[1]):
            if set_range == True:
                column_data = data.iloc[:, i]
                listlow, listhigh = np.percentile(column_data, [0, 100])
            else:
                if i == 0:
                    listlow = -90
                    listhigh = 90
                else:
                    listlow = -180
                    listhigh = 180

            normalize[i, 0] = listlow
            normalize[i, 1] = listhigh

            delta = listhigh - listlow
            if delta != 0:
                for j in range(0, data.shape[0]):
                    data.iloc[j, i] = (data.iloc[j, i] - listlow) / delta

        return data, normalize


    def create_dataset(data, n_predictions, n_next):
        '''
        对数据进行处理
        '''
        dim = data.shape[1]
        train_X, train_Y = [], []
        for i in range(data.shape[0] - n_predictions - n_next - 1):
            a = data.iloc[i:(i + n_predictions), :]

            train_X.append(a)
            tempb = data.iloc[(i + n_predictions):(i + n_predictions + n_next), :]
            b = []
            for j in range(len(tempb)):
                for k in range(dim):
                    b.append(tempb.iloc[j, k])
            train_Y.append(b)
        train_X = np.array(train_X, dtype='float64')
        train_Y = np.array(train_Y, dtype='float64')
    
        test_X, test_Y = [], []
        i = data.shape[0] - n_predictions - n_next - 1
        a = data.iloc[i:(i + n_predictions), :]
        test_X.append(a)
        tempb = data.iloc[(i + n_predictions):(i + n_predictions + n_next), :]
        b = []
        for j in range(len(tempb)):
            for k in range(dim):
                b.append(tempb.iloc[j, k])
        test_Y.append(b)
        test_X = np.array(test_X, dtype='float64')
        test_Y = np.array(test_Y, dtype='float64')
    
        return train_X, train_Y, test_X, test_Y

    # 训练模型
    def main():
        print("main start") #
        train_num = 6 # 
        per_num = 1 
        set_range = True
        
        # 读入数据
        plt_road = r'LSTM/interface/input-data.txt' # 输入数据所在的路径
        data = pd.read_csv(plt_road, sep=',', skiprows=2, usecols=[0,1]) 
        # skiprows : 跳过前几行
        # usecols : 只读取特定行
        
        # 归一化
        data, normalize = NormalizeMult(data, set_range)
    
        # 生成训练数据
        train_X, train_Y, test_X, test_Y = create_dataset(data, train_num, per_num)
        
        # 训练模型
        model = trainModel(train_X, train_Y)
        loss, acc = model.evaluate(train_X, train_Y, verbose=2)
    
        # 保存模型
        model_road1 = r"./LSTM/interface/model/traj_model_trueNorm_v2.npy"
        model_road2 = r"./LSTM/interface/model/traj_model_120_v2.h5"
        np.save(model_road1, normalize)
        model.save(model_road2)
        
    main() # 进入主函数
        