# 基础镜像：使用 Miniconda 基础镜像
FROM continuumio/miniconda3
# 设置工作目录
WORKDIR /app
# 复制整个项目到容器的 /app 目录
COPY backend /app
# 复制 Conda 环境文件到容器
COPY sa.tar.gz /opt/sa.tar.gz
# 解压 Conda 环境
RUN mkdir /opt/conda_env && \
    tar -xzf /opt/sa.tar.gz -C /opt/conda_env && \
    rm /opt/sa.tar.gz
# 设置 PATH 环境变量，使解压的 Conda 环境生效
ENV PATH="/opt/conda_env/bin:$PATH"
# 创建一个启动脚本
RUN echo -e "#!/bin/bash\npython LSTM/interface/traj-predict-app2.py &\npython app.py" > /app/start.sh && \
    chmod +x /app/start.sh
# 使用启动脚本启动容器
CMD ["/bin/bash", "/app/start.sh"]
