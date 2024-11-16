FROM python:3.11.2

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# 更新和安装必要的系统依赖
RUN apt update && apt install -y ffmpeg libsm6 libxext6 libgl1 libgomp1 && rm -rf /var/lib/apt/lists/*

# 复制 requirements.txt 并安装依赖
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# 复制项目的其余代码
COPY . .

CMD ["python", "run.py"]
