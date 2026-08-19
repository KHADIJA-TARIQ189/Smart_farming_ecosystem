# Smart Farming Ecosystem — Full Project

This zip contains both halves of the project, kept in their own separate,
well-organized folders:

```
smart-farming-project/
├── smart-farming-backend/     ← FastAPI backend (API, database, business logic)
└── smart-farming-frontend/     ← HTML/CSS/JS dashboard (what the user sees)
```

They run as two separate servers that talk to each other over HTTP — that's
normal and correct for this kind of project. You start both, then use the
frontend in your browser.

## Quick start

**1. Start the backend** (in one terminal):
```bash
cd smart-farming-backend
python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload
```
Check it worked: open **http://localhost:8000/health** → should show `{"status":"ok"}`.

**2. Start the frontend** (in a second terminal):
```bash
cd smart-farming-frontend
python3 -m http.server 5500
```
Open **http://localhost:5500** in your browser.

**3. Use it**
- Click **Create account** → fill the form → you're logged in automatically, with a success message.
- Click **+ Add farm** → give it a name.
- Click the farm card to open it.
- In the Devices tab, click **+ Add device** to get an API key.
- Every action (register, login, add farm, add device, control a pump/fan/light, resolve an alert) shows a clear success or error message, both inline and as a pop-up in the corner.

Full details for each half are in `smart-farming-backend/README.md` and
`smart-farming-frontend/README.md`.
