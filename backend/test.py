# import os

# # 获取当前工作目录
# current_directory = os.getcwd()
# print(f"Current Directory: {current_directory}")

# # 定义文件路径
# file_path = "backend/data/small_scale_self_advantage_1.json"

# # 构建绝对路径
# absolute_file_path = os.path.join(current_directory, file_path)

# # 确认文件存在
# if os.path.exists(absolute_file_path):
#     print(f"File found: {absolute_file_path}")
# else:
#     print(f"File not found: {absolute_file_path}")

import matplotlib.pyplot as plt

# 测试代码：绘制一个简单的图形
x = [1, 2, 3]
y = [4, 5, 6]

plt.plot(x, y)
plt.title('Test Plot')
plt.xlabel('X Axis')
plt.ylabel('Y Axis')

# 显示图形
plt.show()
