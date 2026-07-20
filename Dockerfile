FROM python:3.10-slim

# FFmpeg für Audio/Video-Konvertierung installieren
RUN apt-get update && apt-get install -y ffmpeg && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Abhängigkeiten kopieren und installieren
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Bot-Code kopieren
COPY . .

# Bot starten
CMD ["python", "bot.py"]