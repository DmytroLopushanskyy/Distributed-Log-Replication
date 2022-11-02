FROM python:3.10
COPY requirements.txt /
# RUN apt-get update && apt-get -y install gcc
# RUN apk add --no-cache python3-dev libffi-dev gcc musl-dev make
RUN pip install -r /requirements.txt
COPY . /
WORKDIR .
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "3000"]
# CMD ["python", "main.py"]
# CMD ["gunicorn", "api:app", "--worker-class uvicorn.workers.UvicornWorker",  "--worker-connections 1000", "--workers 3", "--timeout 90", "--log-level debug", "-b 0.0.0.0:3000"]
