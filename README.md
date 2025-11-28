# Payments QA Project (Payments + Kafka + Postgres)

## Запуск локально

1. Установи Docker & Docker Compose.
2. Клонируй репозиторий и перейди в директорию проекта.
3. Запусти:

```bash
docker-compose up --build
```

Сервисы:
- API: http://localhost:8000
- Postgres: localhost:5432
- Kafka: localhost:9092

## Запуск тестов

Убедись, что сервисы подняты, затем в корне проекта запусти:

```bash
pip install -r app/requirements.txt
pip install pytest requests kafka-python psycopg2-binary
pytest -q