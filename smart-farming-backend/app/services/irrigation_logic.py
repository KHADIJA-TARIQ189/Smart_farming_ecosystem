"""
Baseline threshold-based logic (Section 2 of the proposal).
This is intentionally simple "if-then" logic — Phase 3+ replaces/augments this
with predictive, weather+crop-profile-aware irrigation decisions.
"""

from sqlalchemy.orm import Session

from app.models.alert import Alert
from app.models.device import Device
from app.models.sensor_reading import SensorReading

# Simple fixed thresholds for now. Later: pull from CropProfile per-farm/zone.
THRESHOLDS = {
    "moisture": {"min": 30.0, "message": "Soil moisture below 30% — irrigation recommended"},
    "temperature": {"max": 40.0, "message": "Temperature above 40°C — heat stress risk"},
    "humidity": {"min": 20.0, "message": "Humidity critically low"},
}


def evaluate_reading_for_alerts(db: Session, device: Device, reading: SensorReading) -> None:
    rule = THRESHOLDS.get(reading.sensor_type)
    if not rule:
        return

    triggered = False
    if "min" in rule and reading.value < rule["min"]:
        triggered = True
    if "max" in rule and reading.value > rule["max"]:
        triggered = True

    if triggered:
        alert = Alert(
            farm_id=device.farm_id,
            type=f"{reading.sensor_type}_threshold",
            message=rule["message"],
            severity="warning",
        )
        db.add(alert)
        db.commit()
