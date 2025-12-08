#!/usr/bin/env python3
"""
Простой интеграционный тест по таблице ожидаемых значений (без дублирования формулы).

- Для набора сумм (таблица EXPECTED) делает POST /create,
  ждёт появления /tax?id=<payment_id> и сравнивает tax_amount с ожидаемым из таблицы.

Usage:
  pip install requests
  python3 tests/simple_test_table.py --app http://localhost:8000 --tax http://localhost:5001

Exit code:
  0 - все проверки успешны
  1 - хотя бы одна проверка упала
"""
import argparse
import json
import sys
import time
from typing import Dict, Optional

import requests

# Таблица ожидаемых значений по конкретным amount (избегаем повторения формулы в тестах)
EXPECTED: Dict[int, int] = {
    500: 150,         # smoke (income < 1000)
    999: 150,         # boundary
    1000: 160,        # first hundred step
    1001: 160,        # rounding check
    1099: 160,        # still +10
    1100: 170,        # 2 hundreds
    2500: 310,        # example used earlier
    10000: 1060,      # upper bound of hundred-branch
    10001: 650,       # percent branch: 150 + round(10001*0.05) = 150 + 500 = 650
    2000000: 100150,  # big number: 150 + round(2000000*0.05) = 150 + 100000
}


def post_create(app_url: str, user_id: int, amount: int) -> Optional[str]:
    url = f"{app_url.rstrip('/')}/create"
    headers = {"Content-Type": "application/json"}
    try:
        r = requests.post(url, headers=headers, data=json.dumps({"user_id": user_id, "amount": amount}), timeout=10)
        r.raise_for_status()
        data = r.json()
        return str(data.get("payment_id", "")) or None
    except Exception as e:
        print(f"[ERROR] create failed amount={amount}: {e}")
        return None


def get_tax(tax_url: str, payment_id: str) -> Optional[Dict]:
    url = f"{tax_url.rstrip('/')}/tax?id={payment_id}"
    try:
        r = requests.get(url, timeout=5)
        if r.status_code == 200:
            return r.json()
        return None
    except Exception:
        return None


def poll_tax(tax_url: str, payment_id: str, timeout: int = 10) -> Optional[Dict]:
    deadline = time.time() + timeout
    while time.time() < deadline:
        data = get_tax(tax_url, payment_id)
        if data and "tax_amount" in data:
            return data
        time.sleep(1)
    return None


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--app", default="http://localhost:8000")
    p.add_argument("--tax", default="http://localhost:5001")
    p.add_argument("--timeout", type=int, default=15, help="seconds to wait for tax")
    args = p.parse_args()

    # порядок проверки (можно изменить)
    amounts = [500, 999, 1000, 1001, 1099, 1100, 2500, 10000, 10001, 2000000]

    all_ok = True
    for amt in amounts:
        expected = EXPECTED.get(amt)
        if expected is None:
            print(f"[SKIP] amount={amt} — нет ожидаемого значения в таблице")
            all_ok = False
            continue

        pid = post_create(args.app, user_id=1, amount=amt)
        if not pid:
            print(f"[FAIL] create failed for amount={amt}")
            all_ok = False
            continue

        tax_resp = poll_tax(args.tax, pid, timeout=args.timeout)
        if not tax_resp:
            print(f"[FAIL] id={pid} amount={amt} — tax not found within {args.timeout}s")
            all_ok = False
            continue

        got = tax_resp.get("tax_amount")
        if str(got) == str(expected):
            print(f"[OK] id={pid} amount={amt} tax={got}")
        else:
            print(f"[FAIL] id={pid} amount={amt} got={got} expected={expected}")
            all_ok = False

    sys.exit(0 if all_ok else 1)


if __name__ == "__main__":
    main()