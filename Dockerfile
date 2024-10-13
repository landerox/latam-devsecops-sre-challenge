# Etapa de Construcción
FROM python:3.12-slim

# Crear directorio de trabajo
WORKDIR /app

# Instalar dependencias
COPY app/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar todo el código fuente de la carpeta `app`
COPY app /app

# Crear un usuario no root por seguridad
RUN useradd -m appuser
USER appuser

# Exponer el puerto 8080 para Cloud Run
EXPOSE 8080

# Comando de inicio para ejecutar la aplicación utilizando Uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
