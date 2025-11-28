import pytest
from kafka import KafkaConsumer


def test_kafka_message_arrives():
    consumer = KafkaConsumer('payments', bootstrap_servers='localhost:9092', auto_offset_reset='earliest', group_id='test-group')
    found = False
    for msg in consumer:
        if msg is not None:
            val = msg.value
            assert b'payment_id' in val or 'payment_id' in str(val)
            found = True
            break
    consumer.close()
    assert found