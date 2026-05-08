# ─── Stage 1: base image ───────────────────────────────────────
FROM python:3.12-slim

# Evita que Python genere archivos .pyc y activa logs sin buffer
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Carpeta de trabajo dentro del container
WORKDIR /app

# ─── Stage 2: instalar dependencias ───────────────────────────
# Copiamos solo requirements primero — Docker cachea este layer
# si requirements.txt no cambió, no reinstala todo
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# ─── Stage 3: copiar código fuente ────────────────────────────
COPY app/ ./app/

# ─── Stage 4: comando de arranque ─────────────────────────────
# 0.0.0.0 para que sea accesible desde fuera del container
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]