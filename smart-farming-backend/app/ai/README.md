# AI / ML models — Phase 3+ (Months 9–10 of the roadmap)

This folder is a placeholder. When you get to the AI phase, add:

- `yield_predictor.py` — loads a trained Linear Regression / Random Forest model,
  exposes `predict(sensor_history) -> float`
- `disease_classifier.py` — loads a CNN (YOLOv8 / ResNet50) for leaf disease detection
  from images, exposes `predict(image_bytes) -> dict`
- `anomaly_detector.py` — flags unusual sensor patterns

Wire these into a new `app/routers/ai.py` with endpoints like:
```
POST /ai/yield-prediction
POST /ai/disease-detect   (multipart image upload)
GET  /ai/anomalies?farm_id=
```

Not needed for Phase 1 (backend core) — safe to ignore until later.
