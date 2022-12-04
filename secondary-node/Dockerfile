FROM python:3.10
COPY requirements.txt /
# RUN apt-get update && apt-get -y install gcc
# RUN apk add --no-cache python3-dev libffi-dev gcc musl-dev make
RUN pip install -r /requirements.txt
COPY . /
WORKDIR .

ARG APP_PORT
ENV APP_PORT=${APP_PORT}
CMD gunicorn secondary:app -w 1 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:"$APP_PORT"
