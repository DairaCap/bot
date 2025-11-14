# Usa una imagen base oficial de Python
FROM python:3.11-slim

# Establece el directorio de trabajo dentro del contenedor
WORKDIR /app

# Copia el código de la aplicación al contenedor
COPY main.py /app/

# Define el comando que se ejecuta al iniciar el contenedor
CMD ["python", "main.py"]