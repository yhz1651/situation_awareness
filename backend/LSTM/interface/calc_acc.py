import numpy as np
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
    threshold = 0.035 # 阈值, 误差小于等于阈值视为预测成功
    # 计算准确率
    num = 0
    len1 = len(errors)
    for i in errors:
        if i<threshold: 
            num+=1
    acc = 1.0*num/len1
    return acc