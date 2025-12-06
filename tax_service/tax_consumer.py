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


def calc_tax(income):
    """
    Формула расчёта налога:
    - минимальный налог = 150
    - если income < 1000 -> вернуть min_tax
    - если 1000 <= income <= 10000 -> для каждой сотни (начиная с 1000) +10 к min_tax
    - если income > 10000 -> percent = round(income * 0.05); вернуть min_tax + percent
    """
    min_tax = 150

    try:
        income_int = int(income)
    except Exception:
        raise ValueError("income must be numeric")

    if income_int < 1000:
        return min_tax
    elif income_int <= 10000:
        hundreds = ((income_int - 999) + 99) // 100
        return min_tax + 10 * hundreds
    else:
        percent = round(income_int * 0.05)
        return min_tax + percent


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
            pid = event.get('payment_id')
            amount = event.get('amount')

            if pid is None or amount is None:
                logger.error('invalid_event', extra={'event': event})
                continue


            try:
                tax = calc_tax(amount)
            except ValueError as ve:
                logger.error('invalid_amount', extra={'payment_id': pid, 'amount': amount, 'error': str(ve)})
                continue

            with get_conn() as conn:
                with conn.cursor() as cur:
                    cur.execute('INSERT INTO taxes (payment_id, tax_amount) VALUES (%s, %s)', (pid, tax))
                    conn.commit()

            logger.info('tax_calculated', extra={'payment_id': pid, 'tax': tax})
        except Exception as exc:
            logger.error('tax_processing_failed', extra={'error': str(exc)})


if __name__ == '__main__':
    time.sleep(2)
    main()