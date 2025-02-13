import subprocess

# 设置需要执行的文件名
file1 = "/root/yhz/code/situation_awareness/backend/data_generate_test.py"
file2 = "/root/yhz/code/situation_awareness/backend/anomaly_detection.py"
count = 0
# 循环1000次

# 定义要清空的文件列表
files_to_clear = ["/root/yhz/code/situation_awareness/backend/policy_precision_output.txt", "/root/yhz/code/situation_awareness/backend/precision_output.txt", "/root/yhz/code/situation_awareness/backend/recall_output.txt", "/root/yhz/code/situation_awareness/backend/accuracy_output.txt"]

# 遍历文件列表，并以写入模式打开每个文件来清空内容
for file_name in files_to_clear:
    open(file_name, "w").close()

for _ in range(2000):
    count += 1
    # 执行第一个文件
    subprocess.run(["python", file1])
    # 执行第二个文件
    subprocess.run(["python", file2])
    print(count)

# 读取文件
with open("policy_precision_output.txt", "r") as file:
    values = [float(line.strip()) for line in file.readlines()]
    
# 计算平均值
average_policy_precision = sum(values) / len(values)
print(f"The average policy precision is: {average_policy_precision}")
