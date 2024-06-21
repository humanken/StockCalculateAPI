#
FROM python:3.9

# 安裝 mysql client 依賴
RUN apt-get update && \
    apt-get install -y python3-dev default-libmysqlclient-dev build-essential && \
    apt-get clean \

RUN mkdir code

WORKDIR /code

COPY ./requirements.txt /code/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

# 將 back_end 內所有資料複製到 /code/back_end
COPY ./back_end /code/back_end

# 定義參數 - no use when deploy docker compose
ARG MYSQL_NAME
ARG MYSQL_USER
ARG MYSQL_PASSWORD

# display print message on docker logs
ENV PYTHONUNBUFFERED=1

# 設置環境變量 - no use when deploy docker compose
ENV MYSQL_NAME=${MYSQL_NAME}
ENV MYSQL_USER=${MYSQL_USER}
ENV MYSQL_PASSWORD=${MYSQL_PASSWORD}

CMD ["uvicorn", "back_end.main:app", "--host", "0.0.0.0", "--port", "9317"]