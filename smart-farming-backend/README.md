# Smart Farming Ecosystem — Backend

FastAPI backend for the Smart Farming Ecosystem FYP. This is Phase 1 of the roadmap:
auth, farms, devices, sensor data ingestion, threshold alerts, actuator control (logged),
and a live WebSocket feed — all runnable and testable **without any hardware**.

---

## 1. Setup (5 minutes, no Docker needed)

```bash
# 1. Create and activate a virtual environment
python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Copy the env file (default uses SQLite — zero setup)
cp .env.example .env

# 4. (Optional but recommended) seed baseline crop profiles
python scripts/seed_crop_profiles.py

# 5. Run the server
uvicorn app.main:app --reload
```

Server runs at **http://localhost:8000**. A `smart_farming.db` SQLite file is created
automatically on first run — nothing else to install.

---

## 2. How to check the backend is working properly

### A. Automated tests (fastest check)
```bash
pytest tests/ -v
```
This runs a full end-to-end flow test (register → login → create farm → create device →
ingest a sensor reading → confirm an alert auto-fires → confirm the reading shows up) plus
a basic health check. If all tests pass (`X passed`), your core logic is correct.

### B. Interactive API docs (visual check)
With the server running, open **http://localhost:8000/docs** in a browser. FastAPI
auto-generates a Swagger UI where you can call every endpoint by hand and see live
request/response JSON — this is also useful for your FYP demo.

### C. Manual walkthrough with curl (proves the real flow works)
```bash
# 1. Register a user
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"name":"Test Farmer","email":"farmer@example.com","password":"testpass123"}'

# 2. Log in (note: /auth/login expects form fields, not JSON — "username" = your email)
curl -X POST http://localhost:8000/auth/login \
  -d "username=farmer@example.com&password=testpass123"
# copy the "access_token" from the response, use it below as <TOKEN>

# 3. Create a farm
curl -X POST http://localhost:8000/farms \
  -H "Authorization: Bearer <TOKEN>" -H "Content-Type: application/json" \
  -d '{"name":"Green Valley","location":"Punjab"}'
# copy the "id" from the response as <FARM_ID>

# 4. Create a device under that farm
curl -X POST http://localhost:8000/farms/<FARM_ID>/devices \
  -H "Authorization: Bearer <TOKEN>" -H "Content-Type: application/json" \
  -d '{"name":"Node A","type":"esp32"}'
# copy the "api_key" from the response as <API_KEY>, and "id" as <DEVICE_ID>

# 5. Simulate a sensor reading (this is what a real ESP32 will POST later —
#    no user token needed here, the device authenticates with its own api_key)
curl -X POST http://localhost:8000/sensors/ingest \
  -H "Content-Type: application/json" \
  -d '{"api_key":"<API_KEY>","sensor_type":"moisture","value":22.5,"unit":"%"}'

# 6. Confirm an alert was auto-created (moisture < 30% triggers one)
curl "http://localhost:8000/alerts?farm_id=<FARM_ID>" -H "Authorization: Bearer <TOKEN>"

# 7. Confirm the reading is retrievable
curl http://localhost:8000/sensors/<DEVICE_ID>/latest -H "Authorization: Bearer <TOKEN>"
```

If step 6 returns an alert and step 7 returns your reading, the full pipeline —
device auth → data storage → automatic alert logic → data retrieval — is confirmed working.

### D. Simulated hardware stream (before you have a real ESP32)
```bash
python scripts/simulate_sensor.py --api-key <API_KEY> --interval 3 --count 10
```
This repeatedly POSTs realistic fake readings, like a real sensor node would. Watch them
land in the database via `GET /sensors/<DEVICE_ID>/history`, or connect a WebSocket client
to `ws://localhost:8000/ws/farm/<FARM_ID>` to see them pushed live (once you wire
`manager.broadcast(...)` into the ingest endpoint — currently the WebSocket infra is in
place but not yet called from `/sensors/ingest`; that's a one-line addition, see
`app/services/notification_service.py`).

---

## 3. Full stack with Postgres + MQTT (optional, do this later)

Once you're ready to move off SQLite / start testing real MQTT-based ingestion (Month 3
of the roadmap):

```bash
docker compose up -d              # starts Postgres + Mosquitto
pip install -r requirements-postgres.txt   # installs psycopg2-binary
```
Then in `.env`, switch:
```
DATABASE_URL=postgresql://sf_user:sf_pass@localhost:5432/smart_farming
MQTT_ENABLED=true
```
Restart the server. Sensor data can now also arrive via MQTT topic
`farm/{farm_id}/device/{device_id}/reading` (see `app/services/mqtt_service.py`), in
addition to the REST `/sensors/ingest` endpoint.

---

## 4. Project structure

```
app/
├── main.py             # FastAPI app, router registration, startup
├── config.py            # env-based settings
├── database.py           # SQLAlchemy engine/session
├── models/               # ORM tables: user, farm, device, sensor_reading, crop,
│                          # crop_profile, actuator_log, alert
├── schemas/               # Pydantic request/response contracts
├── routers/                # HTTP route handlers (thin — logic lives in services/)
├── services/                # irrigation_logic (threshold alerts), mqtt_service,
│                             # notification_service (WebSocket manager)
├── core/                     # security (JWT/password hashing), deps (auth dependency)
└── ai/                        # placeholder for Phase 3 ML models

scripts/
├── seed_crop_profiles.py      # populates baseline crop profiles
└── simulate_sensor.py          # fakes an ESP32 posting readings

tests/
├── conftest.py                  # isolated SQLite test DB fixture
├── test_health.py
└── test_flow.py                  # full end-to-end flow test
```

## 5. What's implemented vs. what's next

**Working now:** auth (register/login/JWT), farms, devices (with per-device api_key),
sensor ingestion (REST), threshold-based alerts, actuator control logging, crop +
crop-profile endpoints, WebSocket endpoint scaffold, MQTT service (off by default).

**Not yet implemented (see the roadmap for when):** wiring WebSocket broadcast into the
ingest endpoint (trivial — a few lines), Alembic migrations (currently using
`Base.metadata.create_all`, fine for dev), AI/ML endpoints (Months 9–10), image upload
for disease detection, blockchain traceability.
