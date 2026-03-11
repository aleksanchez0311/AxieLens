# ============================================
# Axie Lens - Hugging Spaces Dockerfile
# ============================================

FROM python:3.11-slim

# Instalar Node.js y npm
RUN apt-get update && apt-get install -y \
    nodejs \
    npm \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Establecer directorio de trabajo
WORKDIR /app

# Copiar archivos de requirements primero para caché de Docker
COPY requirements.txt .

# Instalar dependencias Python
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el resto de la aplicación
COPY . .

# Crear directorio para variables de entorno
RUN mkdir -p /app

# Exponer puerto (Hugging Spaces usa 7860 por defecto)
EXPOSE 7860

# Variable de entorno para modo producción
ENV PYTHONUNBUFFERED=1


# Comando por defecto
CMD ["python", "run_cloud.py"]
