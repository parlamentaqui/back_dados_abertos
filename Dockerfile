FROM python:3.8.0-alpine

WORKDIR /usr/src/etl_camara

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . /usr/src/etl_camara

CMD ["python", "src/app.py"]

