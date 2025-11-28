import pytest
import os
import time
import psycopg2
from urllib.parse import urljoin

BASE = os.getenv('BASE_URL', 'http://localhost:8000')

@pytest.fixture(scope='session')
def base_url():
    return BASE

@pytest.fixture
def api_client(base_url):
    import requests
    class Client:
        def post(self, path, json=None, headers=None):
            return requests.post(urljoin(base_url, path), json=json, headers=headers)
        def get(self, path, headers=None):
            return requests.get(urljoin(base_url, path), headers=headers)
    return Client()

@pytest.fixture(scope='session')
def db_conn():
    dsn = os.getenv('DATABASE_URL', 'postgres://postgres:postgres@localhost:5432/payments')
    conn = psycopg2.connect(dsn)
    yield conn
    conn.close()

# simple wait_until helper
import time

def wait_until(condition, timeout=10, interval=0.5):
    start = time.time()
    while time.time() - start < timeout:
        try:
            if condition():
                return True
        except Exception:
            pass
        time.sleep(interval)
    return False