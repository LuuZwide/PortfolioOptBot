FROM python:3.10

COPY . /app

WORKDIR /app

RUN pip install -r requirements.txt

CMD ["python", "main.py", "--user", "demo", "--start_from", "R"]