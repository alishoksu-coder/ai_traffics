# Используем легкий образ Python
FROM python:3.10-slim

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем зависимости
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем весь код бэкенда
COPY . .

# Создаем папку для локальной БД (на случай, если она нужна)
RUN mkdir -p data

# Открываем порт 8000
EXPOSE 8000

# Запускаем и бэкенд и ИИ-воркер
# (В продакшене лучше использовать экран или фоновые процессы, 
#  но для начала запустим API)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
