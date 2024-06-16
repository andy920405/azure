FROM python:3

RUN mkdir /app
WORKDIR /app

COPY web_final.py .
COPY requirements.txt .

RUN pip install -r requirements.txt

ENTRYPOINT ["python", "web_final.py"]
