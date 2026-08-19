# FieldSense — Smart Farming Frontend

A plain HTML/CSS/JavaScript dashboard for the Smart Farming Ecosystem backend
(FastAPI). No build step, no npm install — open it in a browser once the
backend is running.

## 1. Run the backend first

From your `smart-farming-backend` folder:

```bash
python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload
```

Confirm it's up: open **http://localhost:8000/health** — you should see `{"status":"ok"}`.

## 2. Run this frontend

The frontend calls the backend at `http://localhost:8000` by default (set in
`js/api.js`, top of the file — change `API_BASE` if your backend runs
somewhere else).

Because it makes `fetch()` calls, serve it over a local web server rather
than double-clicking the HTML file (some browsers block API calls from
`file://` pages). Easiest options:

```bash
# Option A — Python (already on most machines)
cd smart-farming-frontend
python3 -m http.server 5500
# then open http://localhost:5500

# Option B — VS Code
# Right-click index.html → "Open with Live Server"
```

## 3. What's included

| Page | What it does |
|---|---|
| **Overview** | Landing page explaining the product |
| **Create account** | Registers a user, then logs them in automatically |
| **Log in** | Signs in and takes you straight to your farms |
| **Farms (dashboard)** | Add farms, click any farm card to open it |
| **Farm detail** | Three tabs — Devices, Crops, Alerts |
| **Device drawer** | Opens when you click a device — shows its API key, latest sensor readings, on/off actuator controls (pump / fan / light), and the action log |

Every action (register, log in, add farm, add device, add crop, resolve
alert, toggle an actuator) shows a clear **success or error message** — both
as an inline message under the form and as a toast in the top-right corner —
so it's always obvious whether something worked.

## 4. Try it end-to-end without real hardware

1. Create an account (auto-logs you in).
2. Add a farm.
3. Open the farm → Devices tab → **+ Add device**. Copy the API key shown in
   the drawer that opens.
4. From the backend folder, simulate a sensor feed:
   ```bash
   python scripts/simulate_sensor.py --api-key <API_KEY> --interval 3 --count 10
   ```
5. Reopen the device drawer in the browser — you'll see live readings, and
   if moisture drops below 30% an alert appears automatically on the Alerts
   tab.
6. Use the Pump / Fan / Light buttons to log actuator actions.

## 5. Project structure

```
smart-farming-frontend/
├── index.html        # every view (home, login, register, dashboard, farm, device drawer)
├── css/style.css      # design system + all page styles
├── js/api.js           # one function per backend endpoint, with readable error messages
└── js/app.js             # view routing, forms, toasts, rendering
```

No frameworks, no bundler — open `js/app.js` and `js/api.js` directly to see
or change how a screen behaves.
