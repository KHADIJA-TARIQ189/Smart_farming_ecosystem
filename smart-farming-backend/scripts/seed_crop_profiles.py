"""
Run once to populate baseline crop profiles used by GET /crop-profiles/{crop_type}.

Usage:
    python scripts/seed_crop_profiles.py
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.database import Base, engine, SessionLocal
from app.models.crop_profile import CropProfile
from app import models  # noqa: F401

PROFILES = [
    dict(crop_type="wheat", ideal_moisture_min=20, ideal_moisture_max=45,
         ideal_temp_min=15, ideal_temp_max=25, ideal_humidity_min=40, ideal_humidity_max=70),
    dict(crop_type="tomato", ideal_moisture_min=40, ideal_moisture_max=70,
         ideal_temp_min=18, ideal_temp_max=27, ideal_humidity_min=50, ideal_humidity_max=80),
    dict(crop_type="rice", ideal_moisture_min=60, ideal_moisture_max=90,
         ideal_temp_min=20, ideal_temp_max=35, ideal_humidity_min=60, ideal_humidity_max=90),
]


def run():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        for p in PROFILES:
            existing = db.query(CropProfile).filter(CropProfile.crop_type == p["crop_type"]).first()
            if existing:
                print(f"  skip (exists): {p['crop_type']}")
                continue
            db.add(CropProfile(**p))
            print(f"  added: {p['crop_type']}")
        db.commit()
    finally:
        db.close()


if __name__ == "__main__":
    run()
    print("Done.")
