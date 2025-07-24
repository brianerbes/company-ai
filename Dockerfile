# Dockerfile
FROM python:3.11-slim

# --- NUEVO: Establecer el idioma del sistema operativo ---
ENV LANG C.UTF-8
ENV LANGUAGE C.UTF-8

RUN apt-get update && apt-get install -y build-essential curl

WORKDIR /app

# ... (el resto del archivo sigue igual) ...
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY entrypoint.sh .
RUN chmod +x ./entrypoint.sh
COPY . .
EXPOSE 7861
ENTRYPOINT ["./entrypoint.sh"]