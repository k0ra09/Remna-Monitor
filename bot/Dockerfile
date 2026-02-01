FROM python:3.11-slim

WORKDIR /bot

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app ./app

# ЭТА СТРОКА ЧИНИТ ОШИБКУ ИМПОРТА:
ENV PYTHONPATH=/bot

CMD ["python", "app/main.py"]
