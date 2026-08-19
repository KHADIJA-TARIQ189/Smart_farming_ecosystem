"""
MQTT ingestion service.

Not wired into main.py yet (MQTT_ENABLED=false by default) — the REST endpoint
POST /sensors/ingest is enough to develop and test the whole backend + frontend
without a broker or hardware.

Turn this on later (Month 3 of the roadmap) once you add Mosquitto via
docker-compose and want real ESP32 nodes (or a simulator) publishing over MQTT
instead of / in addition to REST.

Expected topic convention:
    farm/{farm_id}/device/{device_id}/reading
    payload (JSON): {"sensor_type": "moisture", "value": 42.5, "unit": "%"}
"""

import json
import threading

import paho.mqtt.client as mqtt

from app.config import settings
from app.database import SessionLocal
from app.models.device import Device
from app.models.sensor_reading import SensorReading
from app.services.irrigation_logic import evaluate_reading_for_alerts


def _on_connect(client, userdata, flags, rc):
    print(f"[mqtt] connected with result code {rc}")
    client.subscribe("farm/+/device/+/reading")


def _on_message(client, userdata, msg):
    try:
        parts = msg.topic.split("/")  # farm, {farm_id}, device, {device_id}, reading
        device_id = int(parts[3])
        data = json.loads(msg.payload.decode())

        db = SessionLocal()
        try:
            device = db.query(Device).filter(Device.id == device_id).first()
            if not device:
                return
            reading = SensorReading(
                device_id=device.id,
                sensor_type=data["sensor_type"],
                value=data["value"],
                unit=data.get("unit"),
            )
            db.add(reading)
            db.commit()
            db.refresh(reading)
            evaluate_reading_for_alerts(db, device, reading)
        finally:
            db.close()
    except Exception as e:
        print(f"[mqtt] failed to process message: {e}")


def start_mqtt_client():
    if not settings.mqtt_enabled:
        return

    client = mqtt.Client()
    client.on_connect = _on_connect
    client.on_message = _on_message
    client.connect(settings.mqtt_broker_host, settings.mqtt_broker_port, 60)

    thread = threading.Thread(target=client.loop_forever, daemon=True)
    thread.start()
    print("[mqtt] client thread started")
