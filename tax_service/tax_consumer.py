import os
import json
import time
from kafka import KafkaConsumer
import psycopg2
from logger import get_logger

logger = get_logger()
DATABASE_URL = os.getenv('DATABASE_URL')
KAFKA_BOOTSTRAP = os.getenv('KAFKA_BOOTSTRAP', 'localhost:9092')


def get_conn():
    return psycopg2.connect(DATABASE_URL)


def main():
    consumer = KafkaConsumer(
        'payments',
        bootstrap_servers=KAFKA_BOOTSTRAP,
        auto_offset_reset='earliest',
        enable_auto_commit=True,
        group_id='tax-service-group',
        value_deserializer=lambda m: json.loads(m.decode('utf-8'))
    )

    logger.info('tax_consumer_started')

    for msg in consumer:
        try:
            event = msg.value
            pid = event['payment_id']
            amount = event['amount']
            tax = int(amount * 0.13)

            with get_conn() as conn:
                with conn.cursor() as cur:
                    cur.execute('INSERT INTO taxes (payment_id, tax_amount) VALUES (%s, %s)', (pid, tax))
                    conn.commit()

            logger.info('tax_calculated', extra={'payment_id': pid, 'tax': tax})
        except Exception as exc:
            logger.error('tax_processing_failed', extra={'error': str(exc)})


if __name__ == '__main__':
    # slight delay to allow DB and Kafka to be ready
    time.sleep(2)
    main()