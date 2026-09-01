# Python 3.12 rasmiy image
FROM python:3.12-slim

# Ishchi papka
WORKDIR /app

# Kerakli kutubxonalarni o'rnatish
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Barcha fayllarni nusxalash
COPY . .

# Flask port
EXPOSE 8000

# Gunicorn orqali ishga tushirish
CMD ["gunicorn", "main:app", "-b", "0.0.0.0:8000"]