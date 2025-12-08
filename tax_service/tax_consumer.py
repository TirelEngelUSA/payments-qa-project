import os
import json
import time
import threading
from flask import Flask, request, jsonify
from kafka import KafkaConsumer
import psycopg2
from logger import get_logger

logger = get_logger()
DATABASE_URL = os.getenv('DATABASE_URL')
KAFKA_BOOTSTRAP = os.getenv('KAFKA_BOOTSTRAP', 'localhost:9092')
# HTTP port for tax endpoint (can be set via env TAX_SERVICE_PORT)
HTTP_PORT = int(os.getenv('TAX_SERVICE_PORT', '5001'))

app = Flask(__name__)


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


@app.route('/tax')
def get_tax():
    """
    HTTP endpoint to fetch tax by payment_id:
    GET /tax?id=<payment_id>
    """
    pid = request.args.get('id')
    if not pid:
        return jsonify({'error': 'id required'}), 400
    try:
        pid_int = int(pid)
    except ValueError:
        return jsonify({'error': 'id must be int'}), 400

    try:
        with get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute('SELECT tax_amount FROM taxes WHERE payment_id=%s', (pid_int,))
                row = cur.fetchone()
                if not row:
                    return jsonify({'error': 'not found'}), 404
                return jsonify({'payment_id': pid_int, 'tax_amount': row[0]})
    except Exception as exc:
        logger.error('tax_query_failed', extra={'payment_id': pid_int, 'error': str(exc)})
        return jsonify({'error': 'internal error'}), 500


def consumer_loop():
    """
    Run Kafka consumer in this function. Intended to be started in a background thread.
    """
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

            # Вычисляем налог по переданной формуле
            try:
                tax = calc_tax(amount)
            except ValueError as ve:
                logger.error('invalid_amount', extra={'payment_id': pid, 'amount': amount, 'error': str(ve)})
                continue

            try:
                with get_conn() as conn:
                    with conn.cursor() as cur:
                        cur.execute('INSERT INTO taxes (payment_id, tax_amount) VALUES (%s, %s)', (pid, tax))
                        conn.commit()
                logger.info('tax_calculated', extra={'payment_id': pid, 'tax': tax})
            except Exception as exc:
                logger.error('db_insert_failed', extra={'payment_id': pid, 'error': str(exc)})
        except Exception as exc:
            logger.error('tax_processing_failed', extra={'error': str(exc)})


def start_consumer_in_background():
    t = threading.Thread(target=consumer_loop, daemon=True)
    t.start()
    return t


if __name__ == '__main__':
    # slight delay to allow DB and Kafka to be ready
    time.sleep(2)
    # start consumer in background thread
    start_consumer_in_background()
    # run HTTP app to expose /tax endpoint
    app.run(host='0.0.0.0', port=HTTP_PORT)