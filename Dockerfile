#
FROM python:3.9

RUN mkdir code

WORKDIR /code

#
COPY ./requirements.txt /code/requirements.txt

#
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

# 將 back_end 內所有資料複製到 /code/backend
COPY ./back_end /code/backend

# 定義參數
ARG MYSQL_NAME
ARG MYSQL_USER
ARG MYSQL_PASSWORD

# 設置環境變量
ENV MYSQL_NAME=${MYSQL_NAME}
ENV MYSQL_USER=${MYSQL_USER}
ENV MYSQL_PASSWORD=${MYSQL_PASSWORD}

#
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8317"]