FROM python:3.13-slim

# Evita ficheiros .pyc e ativa output sem buffer (útil para logs em containers)
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /code

# Nota: psycopg2-binary já vem pré-compilado, não precisamos de gcc/libpq-dev

# Instala dependências Python primeiro (aproveita cache do Docker)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia o resto do código
COPY . .

EXPOSE 8000

# Ajusta "app.main:app" se o teu ficheiro/objeto FastAPI tiver outro nome
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]