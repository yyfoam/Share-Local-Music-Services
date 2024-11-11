
# 使用指定版本的 Python 镜像
FROM python:3.9.18-slim

# 更新包列表并安装 ffmpeg
RUN apt-get update && \
    apt-get install -y ffmpeg && \
    apt-get clean

# 设置工作目录
WORKDIR /app

# 复制项目代码到容器中
COPY . /app

# 安装 Python 依赖
RUN pip install --no-cache-dir -r requirements.txt

# 设置 Flask 应用的入口点
ENV FLASK_APP=app.py


# 暴露应用端口 7890
EXPOSE 7890

# 设置默认命令启动 Flask 应用
CMD ["flask", "run", "--host=0.0.0.0", "--port=7890"]
