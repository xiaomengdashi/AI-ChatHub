# 使用官方 Python 运行时作为基础镜像
FROM python:3.9-slim

# 设置工作目录
WORKDIR /app

# 复制 requirements.txt 并安装依赖
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制应用代码
COPY . .

# 创建数据库目录
RUN mkdir -p /app/database

# 暴露端口
EXPOSE 5001

# 设置环境变量
ENV FLASK_APP=app.py
ENV FLASK_ENV=development

# 启动命令
CMD ["python", "app.py"]