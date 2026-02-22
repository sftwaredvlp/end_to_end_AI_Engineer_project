FROM python:3.12-slim

# Çalışma klasörü
WORKDIR /app

# Sistem paketleri
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Python paketleri
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Proje kodu
COPY . .

# Statik dosyalar
RUN mkdir -p staticfiles

# Port expose
EXPOSE 8000

# Django migrations ve server
CMD ["sh", "-c", "python manage.py migrate && python manage.py runserver 0.0.0.0:8000"]
