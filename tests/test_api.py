from conftest import wait_until


def test_create_and_check_db(api_client, db_conn):
    payload = {'user_id': 7, 'amount': 100}
    r = api_client.post('/create', json=payload)
    assert r.status_code == 200
    pid = r.json()['payment_id']

    # check payments record exists
    def check_payments():
        with db_conn.cursor() as cur:
            cur.execute('SELECT amount FROM payments WHERE id=%s', (pid,))
            row = cur.fetchone()
            return row is not None and row[0] == 100

    assert wait_until(check_payments, timeout=5)


def test_status_endpoint(api_client):
    payload = {'user_id': 8, 'amount': 50}
    r = api_client.post('/create', json=payload)
    pid = r.json()['payment_id']

    r2 = api_client.get(f'/status?id={pid}')
    assert r2.status_code == 200
    assert r2.json()['status'] in ('PROCESSING', 'DONE')