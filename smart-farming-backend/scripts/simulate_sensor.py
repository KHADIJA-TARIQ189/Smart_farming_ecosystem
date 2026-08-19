"""
Simulates a real ESP32 sensor node by POSTing fake readings to /sensors/ingest
every few seconds. Use this to test the backend (and later, the frontend) before
any hardware exists.

Usage:
    python scripts/simulate_sensor.py --api-key <device_api_key>

Get a device api_key by:
    1. Register + login a user (see README "Verify it works" section)
    2. Create a farm, then create a device under that farm
    3. Copy the "api_key" field from the device creation response
"""

import argparse
import random
import time

import requests

BASE_URL = "http://localhost:8000"


def send_reading(api_key: str, sensor_type: str, value: float, unit: str):
    resp = requests.post(
        f"{BASE_URL}/sensors/ingest",
        json={"api_key": api_key, "sensor_type": sensor_type, "value": value, "unit": unit},
    )
    print(f"  {sensor_type}={value}{unit} -> {resp.status_code}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--api-key", required=True, help="Device api_key from POST /farms/{id}/devices")
    parser.add_argument("--interval", type=float, default=3.0, help="Seconds between reading batches")
    parser.add_argument("--count", type=int, default=10, help="How many batches to send (0 = forever)")
    args = parser.parse_args()

    sent = 0
    while args.count == 0 or sent < args.count:
        print(f"Batch {sent + 1}:")
        send_reading(args.api_key, "moisture", round(random.uniform(15, 60), 1), "%")
        send_reading(args.api_key, "temperature", round(random.uniform(18, 42), 1), "C")
        send_reading(args.api_key, "humidity", round(random.uniform(20, 90), 1), "%")
        sent += 1
        time.sleep(args.interval)


if __name__ == "__main__":
    main()
