# Django + OpenAI Function Calling — konteyner
FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1
WORKDIR /app

# Bağımlılıkları kur
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Uygulamayı kopyala
COPY . .

# Port
EXPOSE 8000

# Migrate (gerekirse) ve sunucuyu 0.0.0.0'da başlat (dışarıdan erişim için)
CMD ["sh", "-c", "python manage.py migrate --noinput 2>/dev/null || true && python manage.py runserver 0.0.0.0:8000"]
