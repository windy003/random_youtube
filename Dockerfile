# 使用 Python 3.12 的官方精简镜像作为基础
FROM python:3.12-slim

# 设置工作目录
WORKDIR /app

# 将依赖文件复制到工作目录
COPY requirements.txt .

# 安装依赖
RUN pip install --no-cache-dir -r requirements.txt

# 复制项目文件到工作目录
COPY . .

# 设置环境变量，Flask 在容器中运行时不会使用调试模式
ENV FLASK_ENV=production

# 暴露Flask默认的端口5000
EXPOSE 5000

# 启动Flask应用
CMD ["flask", "run", "--host=0.0.0.0"]
