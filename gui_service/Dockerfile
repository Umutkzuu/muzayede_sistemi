FROM python:3.10-slim

WORKDIR /app

# Bağımlılıkları kopyala ve kur
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Kodları kopyala
COPY . .

# Streamlit için portu aç
EXPOSE 8501

# Streamlit'i çalıştır
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]