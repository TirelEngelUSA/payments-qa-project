import os
import json
import time
import uuid
from flask import Flask, request, jsonify
import psycopg2
from logger import get_logger
from kafka import KafkaProducer

logger = get_logger()
DATABASE_URL = os.getenv('DATABASE_URL')
KAFKA_BOOTSTRAP = os.getenv('KAFKA_BOOTSTRAP', 'localhost:9092')

app = Flask(__name__)

producer = KafkaProducer(bootstrap_servers=KAFKA_BOOTSTRAP,
                         value_serializer=lambda v: json.dumps(v).encode('utf-8'))


def get_conn():
    return psycopg2.connect(DATABASE_URL)


@app.route('/create', methods=['POST'])
def create_payment():
    payload = request.get_json()
    user_id = payload.get('user_id')
    amount = payload.get('amount')
    if user_id is None or amount is None:
        return jsonify({'error': 'user_id and amount required'}), 400

    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("INSERT INTO payments (user_id, amount) VALUES (%s, %s) RETURNING id",
                        (user_id, amount))
            pid = cur.fetchone()[0]
            conn.commit()

    logger.info('created_payment', extra={'payment_id': pid, 'user_id': user_id, 'amount': amount})

    # send event to Kafka
    event = {'payment_id': pid, 'user_id': user_id, 'amount': amount}
    try:
        producer.send('payments', value=event)
        producer.flush(timeout=5)
        logger.info('sent_event', extra={'payment_id': pid})
    except Exception as exc:
        logger.error('kafka_send_failed', extra={'payment_id': pid, 'error': str(exc)})

    return jsonify({'payment_id': pid, 'status': 'PROCESSING'})


@app.route('/status')
def status():
    pid = request.args.get('id')
    if pid is None:
        return jsonify({'error': 'id required'}), 400
    try:
        pid_int = int(pid)
    except ValueError:
        return jsonify({'error': 'id must be int'}), 400

    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute('SELECT id, user_id, amount, status FROM payments WHERE id=%s', (pid_int,))
            row = cur.fetchone()
            if not row:
                return jsonify({'error': 'not found'}), 404
            res = {'id': row[0], 'user_id': row[1], 'amount': row[2], 'status': row[3]}
    return jsonify(res)


if __name__ == '__main__':
    time.sleep(1)
    app.run(host='0.0.0.0', port=8000)