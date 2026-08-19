/* ==========================================================================
   FieldSense — application logic
   ========================================================================== */

// ---------------------------------------------------------------------------
// State
// ---------------------------------------------------------------------------
const state = {
  user: null,          // current logged-in user object
  farms: [],           // farms owned by the user
  currentFarm: null,    // farm currently open in the "farm" view
  devices: [],
  crops: [],
  alerts: [],
  currentDevice: null,   // device open in the drawer
  actuatorState: {},      // { [deviceId]: { pump: 'on'|'off', fan: ..., light: ... } }
};

document.getElementById("footer-api-base").textContent = API_BASE;

// ---------------------------------------------------------------------------
// Toasts (success / error messages shown for every action)
// ---------------------------------------------------------------------------
function toast(message, type = "success", timeout = 4200) {
  const stack = document.getElementById("toast-stack");
  const el = document.createElement("div");
  el.className = `toast is-${type}`;
  el.innerHTML = `<span class="toast-icon">${type === "success" ? "✓" : "!"}</span><p>${escapeHtml(message)}</p>`;
  stack.appendChild(el);
  setTimeout(() => {
    el.style.transition = "opacity .2s ease";
    el.style.opacity = "0";
    setTimeout(() => el.remove(), 200);
  }, timeout);
}

function escapeHtml(str) {
  const div = document.createElement("div");
  div.textContent = String(str);
  return div.innerHTML;
}

function showFormMsg(elId, message, type) {
  const el = document.getElementById(elId);
  el.textContent = message;
  el.className = `form-msg is-${type}`;
}
function clearFormMsg(elId) {
  const el = document.getElementById(elId);
  el.textContent = "";
  el.className = "form-msg";
}

function setBusy(buttonEl, busy) {
  const label = buttonEl.querySelector(".btn-label");
  const spinner = buttonEl.querySelector(".btn-spinner");
  buttonEl.disabled = busy;
  if (spinner) spinner.hidden = !busy;
  if (label) label.style.opacity = busy ? "0.6" : "1";
}

// ---------------------------------------------------------------------------
// View router — every "click and it opens that page" interaction routes here
// ---------------------------------------------------------------------------
const views = ["home", "login", "register", "dashboard", "farm"];

function goTo(viewName, opts = {}) {
  const requiresAuth = viewName === "dashboard" || viewName === "farm";
  if (requiresAuth && !state.user) {
    toast("Please log in first to view that page.", "error");
    viewName = "login";
  }

  views.forEach((v) => {
    document.getElementById(`view-${v}`).hidden = v !== viewName;
  });
  window.scrollTo({ top: 0, behavior: "smooth" });

  if (viewName === "dashboard") refreshDashboard();
  if (viewName === "farm" && opts.farmId) openFarm(opts.farmId);
}

document.querySelectorAll("[data-nav]").forEach((el) => {
  el.addEventListener("click", () => goTo(el.dataset.nav));
});

// ---------------------------------------------------------------------------
// Auth: session bootstrap
// ---------------------------------------------------------------------------
function setPrivateNav(isLoggedIn) {
  document.getElementById("nav-public").hidden = isLoggedIn;
  document.getElementById("nav-private").hidden = !isLoggedIn;
}

async function bootstrapSession() {
  if (!getToken()) {
    setPrivateNav(false);
    return;
  }
  try {
    const me = await Api.me();
    state.user = me;
    document.getElementById("user-chip-name").textContent = me.name;
    setPrivateNav(true);
  } catch (err) {
    clearToken();
    setPrivateNav(false);
  }
}

// ---------------------------------------------------------------------------
// Password show/hide
// ---------------------------------------------------------------------------
document.querySelectorAll("[data-peek]").forEach((btn) => {
  btn.addEventListener("click", () => {
    const input = document.getElementById(btn.dataset.peek);
    const showing = input.type === "text";
    input.type = showing ? "password" : "text";
    btn.textContent = showing ? "Show" : "Hide";
  });
});

// ---------------------------------------------------------------------------
// Register
// ---------------------------------------------------------------------------
document.getElementById("form-register").addEventListener("submit", async (e) => {
  e.preventDefault();
  clearFormMsg("register-msg");
  const name = document.getElementById("register-name").value.trim();
  const email = document.getElementById("register-email").value.trim();
  const password = document.getElementById("register-password").value;
  const submitBtn = document.getElementById("register-submit");

  if (!name || !email || password.length < 6) {
    showFormMsg("register-msg", "Please fill every field — password needs at least 6 characters.", "error");
    return;
  }

  setBusy(submitBtn, true);
  try {
    await Api.register(name, email, password);
    showFormMsg("register-msg", "Account created! Logging you in…", "success");
    toast(`Welcome, ${name} — your account was created successfully.`, "success");

    // Auto login right after registering, for a smooth "click and it opens that page" flow
    const token = await Api.login(email, password);
    setToken(token.access_token);
    await bootstrapSession();
    document.getElementById("form-register").reset();
    goTo("dashboard");
  } catch (err) {
    showFormMsg("register-msg", err.message, "error");
    toast(err.message, "error");
  } finally {
    setBusy(submitBtn, false);
  }
});

// ---------------------------------------------------------------------------
// Login
// ---------------------------------------------------------------------------
document.getElementById("form-login").addEventListener("submit", async (e) => {
  e.preventDefault();
  clearFormMsg("login-msg");
  const email = document.getElementById("login-email").value.trim();
  const password = document.getElementById("login-password").value;
  const submitBtn = document.getElementById("login-submit");

  if (!email || !password) {
    showFormMsg("login-msg", "Enter both your email and password.", "error");
    return;
  }

  setBusy(submitBtn, true);
  try {
    const token = await Api.login(email, password);
    setToken(token.access_token);
    await bootstrapSession();
    showFormMsg("login-msg", "Logged in successfully.", "success");
    toast(`Welcome back, ${state.user ? state.user.name : "farmer"}.`, "success");
    document.getElementById("form-login").reset();
    goTo("dashboard");
  } catch (err) {
    showFormMsg("login-msg", err.message, "error");
    toast(err.message, "error");
  } finally {
    setBusy(submitBtn, false);
  }
});

// ---------------------------------------------------------------------------
// Logout
// ---------------------------------------------------------------------------
document.getElementById("btn-logout").addEventListener("click", () => {
  clearToken();
  state.user = null;
  setPrivateNav(false);
  toast("You've been logged out.", "success");
  goTo("home");
});

// ---------------------------------------------------------------------------
// Dashboard: farms
// ---------------------------------------------------------------------------
async function refreshDashboard() {
  document.getElementById("dashboard-heading").textContent = state.user ? `Welcome, ${state.user.name.split(" ")[0]}` : "Every field, one view";
  try {
    const [farms, allDeviceCounts] = await Promise.all([Api.listFarms(), Promise.resolve(null)]);
    state.farms = farms;
    renderFarms(farms);
  } catch (err) {
    toast(err.message, "error");
  }
}

function renderFarms(farms) {
  const grid = document.getElementById("farms-grid");
  const empty = document.getElementById("farms-empty");
  grid.innerHTML = "";

  if (!farms.length) {
    empty.hidden = false;
    return;
  }
  empty.hidden = true;

  farms.forEach((farm) => {
    const card = document.createElement("button");
    card.className = "farm-card";
    card.innerHTML = `
      <h3>${escapeHtml(farm.name)}</h3>
      <div class="loc">${escapeHtml(farm.location || "Location not set")}</div>
      <div class="farm-card-stats">
        <div><b>#${farm.id}</b>Farm ID</div>
        <div><b>${new Date(farm.created_at).toLocaleDateString()}</b>Added</div>
      </div>
    `;
    card.addEventListener("click", () => goTo("farm", { farmId: farm.id }));
    grid.appendChild(card);
  });
}

function toggleNewFarmPanel(show) {
  document.getElementById("newfarm-panel").hidden = !show;
  if (show) document.getElementById("farm-name").focus();
  else { document.getElementById("form-newfarm").reset(); clearFormMsg("newfarm-msg"); }
}
document.getElementById("btn-open-newfarm").addEventListener("click", () => toggleNewFarmPanel(true));
document.getElementById("btn-empty-newfarm").addEventListener("click", () => toggleNewFarmPanel(true));
document.getElementById("btn-cancel-newfarm").addEventListener("click", () => toggleNewFarmPanel(false));

document.getElementById("form-newfarm").addEventListener("submit", async (e) => {
  e.preventDefault();
  clearFormMsg("newfarm-msg");
  const name = document.getElementById("farm-name").value.trim();
  const location = document.getElementById("farm-location").value.trim();
  const submitBtn = e.target.querySelector("button[type=submit]");

  if (!name) {
    showFormMsg("newfarm-msg", "Farm name is required.", "error");
    return;
  }

  setBusy(submitBtn, true);
  try {
    await Api.createFarm(name, location);
    showFormMsg("newfarm-msg", "Farm added successfully.", "success");
    toast(`"${name}" was added to your farms.`, "success");
    toggleNewFarmPanel(false);
    await refreshDashboard();
  } catch (err) {
    showFormMsg("newfarm-msg", err.message, "error");
    toast(err.message, "error");
  } finally {
    setBusy(submitBtn, false);
  }
});

// ---------------------------------------------------------------------------
// Farm detail
// ---------------------------------------------------------------------------
async function openFarm(farmId) {
  try {
    const farm = await Api.getFarm(farmId);
    state.currentFarm = farm;
    document.getElementById("farm-heading").textContent = farm.name;
    document.getElementById("farm-sub").textContent = `${farm.location || "No location set"} · Farm #${farm.id}`;

    await Promise.all([refreshDevices(), refreshCrops(), refreshAlerts()]);
    setActiveFarmTab("devices");
  } catch (err) {
    toast(err.message, "error");
    goTo("dashboard");
  }
}

// -- tabs --
document.querySelectorAll(".tab-btn").forEach((btn) => {
  btn.addEventListener("click", () => setActiveFarmTab(btn.dataset.tab));
});
function setActiveFarmTab(tab) {
  document.querySelectorAll(".tab-btn").forEach((b) => b.classList.toggle("is-active", b.dataset.tab === tab));
  document.querySelectorAll("[data-tab-panel]").forEach((p) => p.classList.toggle("is-active", p.dataset.tabPanel === tab));
}

// -- devices --
async function refreshDevices() {
  const devices = await Api.listDevices(state.currentFarm.id);
  state.devices = devices;
  renderDevices(devices);
}

function renderDevices(devices) {
  const list = document.getElementById("devices-list");
  const empty = document.getElementById("devices-empty");
  list.innerHTML = "";
  if (!devices.length) { empty.hidden = false; return; }
  empty.hidden = true;

  devices.forEach((d) => {
    const card = document.createElement("button");
    card.className = "device-card";
    card.innerHTML = `
      <div class="device-card-top">
        <h4>${escapeHtml(d.name)}</h4>
        <span class="status-pill ${d.status === "online" ? "status-online" : "status-offline"}">${escapeHtml(d.status)}</span>
      </div>
      <div class="device-card-meta">${escapeHtml(d.type)} · #${d.id}</div>
      <div class="device-card-meta">${d.last_seen ? "Last seen " + new Date(d.last_seen).toLocaleString() : "No data received yet"}</div>
    `;
    card.addEventListener("click", () => openDeviceDrawer(d));
    list.appendChild(card);
  });
}

function toggleNewDevicePanel(show) {
  document.getElementById("newdevice-panel").hidden = !show;
  if (show) document.getElementById("device-name").focus();
  else { document.getElementById("form-newdevice").reset(); clearFormMsg("newdevice-msg"); }
}
document.getElementById("btn-open-newdevice").addEventListener("click", () => toggleNewDevicePanel(true));
document.getElementById("btn-cancel-newdevice").addEventListener("click", () => toggleNewDevicePanel(false));

document.getElementById("form-newdevice").addEventListener("submit", async (e) => {
  e.preventDefault();
  clearFormMsg("newdevice-msg");
  const name = document.getElementById("device-name").value.trim();
  const type = document.getElementById("device-type").value;
  const submitBtn = e.target.querySelector("button[type=submit]");

  if (!name) {
    showFormMsg("newdevice-msg", "Device name is required.", "error");
    return;
  }

  setBusy(submitBtn, true);
  try {
    const device = await Api.createDevice(state.currentFarm.id, name, type);
    showFormMsg("newdevice-msg", "Device added — API key generated.", "success");
    toast(`"${name}" was added. Its API key is ready to use.`, "success");
    toggleNewDevicePanel(false);
    await refreshDevices();
    openDeviceDrawer(device);
  } catch (err) {
    showFormMsg("newdevice-msg", err.message, "error");
    toast(err.message, "error");
  } finally {
    setBusy(submitBtn, false);
  }
});

// -- crops --
async function refreshCrops() {
  const crops = await Api.listCrops(state.currentFarm.id);
  state.crops = crops;
  renderCrops(crops);
}
function renderCrops(crops) {
  const list = document.getElementById("crops-list");
  const empty = document.getElementById("crops-empty");
  list.innerHTML = "";
  if (!crops.length) { empty.hidden = false; return; }
  empty.hidden = true;

  crops.forEach((c) => {
    const card = document.createElement("div");
    card.className = "crop-card";
    card.innerHTML = `
      <h4>${escapeHtml(c.crop_type)}</h4>
      <div class="crop-meta">${escapeHtml(c.zone || "No zone set")}</div>
      <div class="crop-meta">${c.planted_date ? "Planted " + new Date(c.planted_date).toLocaleDateString() : "Planting date not set"}</div>
      <span class="crop-status">${escapeHtml(c.status)}</span>
    `;
    list.appendChild(card);
  });
}

function toggleNewCropPanel(show) {
  document.getElementById("newcrop-panel").hidden = !show;
  if (show) document.getElementById("crop-type").focus();
  else { document.getElementById("form-newcrop").reset(); clearFormMsg("newcrop-msg"); }
}
document.getElementById("btn-open-newcrop").addEventListener("click", () => toggleNewCropPanel(true));
document.getElementById("btn-cancel-newcrop").addEventListener("click", () => toggleNewCropPanel(false));

document.getElementById("form-newcrop").addEventListener("submit", async (e) => {
  e.preventDefault();
  clearFormMsg("newcrop-msg");
  const cropType = document.getElementById("crop-type").value.trim();
  const zone = document.getElementById("crop-zone").value.trim();
  const submitBtn = e.target.querySelector("button[type=submit]");

  if (!cropType) {
    showFormMsg("newcrop-msg", "Crop type is required.", "error");
    return;
  }

  setBusy(submitBtn, true);
  try {
    await Api.createCrop(state.currentFarm.id, cropType, zone);
    showFormMsg("newcrop-msg", "Crop added successfully.", "success");
    toast(`"${cropType}" was added to this farm.`, "success");
    toggleNewCropPanel(false);
    await refreshCrops();
  } catch (err) {
    showFormMsg("newcrop-msg", err.message, "error");
    toast(err.message, "error");
  } finally {
    setBusy(submitBtn, false);
  }
});

// -- alerts --
async function refreshAlerts() {
  const alerts = await Api.listAlerts(state.currentFarm.id);
  state.alerts = alerts;
  renderAlerts(alerts);
}
function renderAlerts(alerts) {
  const list = document.getElementById("alerts-list");
  const empty = document.getElementById("alerts-empty");
  const badge = document.getElementById("alert-badge");
  list.innerHTML = "";

  const unresolved = alerts.filter((a) => !a.resolved);
  if (unresolved.length) {
    badge.hidden = false;
    badge.textContent = `${unresolved.length} active alert${unresolved.length > 1 ? "s" : ""}`;
  } else {
    badge.hidden = true;
  }

  if (!alerts.length) { empty.hidden = false; return; }
  empty.hidden = true;

  alerts.forEach((a) => {
    const row = document.createElement("div");
    row.className = `alert-row ${a.resolved ? "is-resolved" : ""}`;
    row.innerHTML = `
      <div>
        <p class="al-msg">${escapeHtml(a.message)}</p>
        <div class="al-meta">${escapeHtml(a.severity).toUpperCase()} · ${new Date(a.created_at).toLocaleString()}</div>
      </div>
    `;
    if (!a.resolved) {
      const btn = document.createElement("button");
      btn.className = "btn btn-secondary btn-sm";
      btn.textContent = "Mark resolved";
      btn.addEventListener("click", async () => {
        btn.disabled = true;
        try {
          await Api.resolveAlert(a.id);
          toast("Alert marked as resolved.", "success");
          await refreshAlerts();
        } catch (err) {
          toast(err.message, "error");
          btn.disabled = false;
        }
      });
      row.appendChild(btn);
    }
    list.appendChild(row);
  });
}

// ---------------------------------------------------------------------------
// Device drawer: readings, actuator control, logs
// ---------------------------------------------------------------------------
function openDeviceDrawer(device) {
  if (!device || device.id === undefined) {
    console.error("openDeviceDrawer called with an invalid device:", device);
    toast("Couldn't open that device — please refresh and try again.", "error");
    return;
  }

  state.currentDevice = device;
  document.getElementById("device-drawer-type").textContent = (device.type || "device").toUpperCase();
  document.getElementById("device-drawer-title").textContent = device.name || `Device #${device.id}`;
  document.getElementById("device-apikey").textContent = device.api_key || "Not available";
  document.getElementById("device-drawer-overlay").hidden = false;
  clearFormMsg("actuator-msg");

  refreshDeviceReadings();
  refreshDeviceLogs();
  resetActuatorToggles();
}
document.getElementById("btn-close-drawer").addEventListener("click", closeDeviceDrawer);
document.getElementById("device-drawer-overlay").addEventListener("click", (e) => {
  if (e.target.id === "device-drawer-overlay") closeDeviceDrawer();
});
function closeDeviceDrawer() {
  document.getElementById("device-drawer-overlay").hidden = true;
  state.currentDevice = null;
}

document.getElementById("btn-copy-apikey").addEventListener("click", async () => {
  const key = document.getElementById("device-apikey").textContent;
  try {
    await navigator.clipboard.writeText(key);
    toast("API key copied to clipboard.", "success");
  } catch {
    toast("Couldn't copy automatically — select and copy the key manually.", "error");
  }
});

async function refreshDeviceReadings() {
  const grid = document.getElementById("device-readings");
  const empty = document.getElementById("device-readings-empty");
  try {
    const readings = await Api.latestReadings(state.currentDevice.id);
    grid.innerHTML = "";
    if (!readings.length) { empty.hidden = false; return; }
    empty.hidden = true;
    readings.forEach((r) => {
      const chip = document.createElement("div");
      chip.className = "reading-chip";
      chip.innerHTML = `
        <div class="rc-type">${escapeHtml(r.sensor_type)}</div>
        <div class="rc-val">${r.value}${r.unit ? " " + escapeHtml(r.unit) : ""}</div>
        <div class="rc-time">${new Date(r.recorded_at).toLocaleString()}</div>
      `;
      grid.appendChild(chip);
    });
  } catch (err) {
    toast(err.message, "error");
  }
}

async function refreshDeviceLogs() {
  const list = document.getElementById("device-logs");
  try {
    const logs = await Api.actuatorLogs(state.currentDevice.id);
    list.innerHTML = "";
    if (!logs.length) {
      list.innerHTML = `<p style="font-size:12.5px;color:var(--text-faint);margin:0;">No actions logged yet.</p>`;
      return;
    }
    logs.slice(0, 12).forEach((log) => {
      const row = document.createElement("div");
      row.className = "log-row";
      row.innerHTML = `
        <span class="lg-action">${escapeHtml(log.actuator_type)} → ${escapeHtml(log.action)}</span>
        <span class="lg-time">${new Date(log.triggered_at).toLocaleTimeString()}</span>
      `;
      list.appendChild(row);
    });

    // sync toggle visuals with the most recent action per actuator
    const latestByType = {};
    logs.forEach((l) => {
      if (!latestByType[l.actuator_type] || new Date(l.triggered_at) > new Date(latestByType[l.actuator_type].triggered_at)) {
        latestByType[l.actuator_type] = l;
      }
    });
    Object.entries(latestByType).forEach(([type, log]) => setToggleVisual(type, log.action));
  } catch (err) {
    toast(err.message, "error");
  }
}

function resetActuatorToggles() {
  document.querySelectorAll(".actuator-toggle").forEach((t) => {
    t.querySelectorAll(".toggle-btn").forEach((b) => b.classList.remove("is-active-on", "is-active-off"));
  });
}
function setToggleVisual(actuatorType, action) {
  const wrap = document.querySelector(`.actuator-toggle[data-actuator="${actuatorType}"]`);
  if (!wrap) return;
  wrap.querySelectorAll(".toggle-btn").forEach((b) => b.classList.remove("is-active-on", "is-active-off"));
  const activeBtn = wrap.querySelector(`.toggle-btn[data-action="${action}"]`);
  if (activeBtn) activeBtn.classList.add(action === "on" ? "is-active-on" : "is-active-off");
}

document.querySelectorAll(".actuator-toggle .toggle-btn").forEach((btn) => {
  btn.addEventListener("click", async () => {
    if (!state.currentDevice) return;
    const actuatorType = btn.closest(".actuator-toggle").dataset.actuator;
    const action = btn.dataset.action;
    clearFormMsg("actuator-msg");
    btn.disabled = true;
    try {
      await Api.controlActuator(state.currentDevice.id, actuatorType, action);
      setToggleVisual(actuatorType, action);
      showFormMsg("actuator-msg", `${capitalize(actuatorType)} switched ${action}.`, "success");
      toast(`${capitalize(actuatorType)} switched ${action}.`, "success");
      refreshDeviceLogs();
    } catch (err) {
      showFormMsg("actuator-msg", err.message, "error");
      toast(err.message, "error");
    } finally {
      btn.disabled = false;
    }
  });
});
function capitalize(s) { return s.charAt(0).toUpperCase() + s.slice(1); }

// ---------------------------------------------------------------------------
// Hero "live field grid" — a small decorative animation, not real data,
// grounding the landing page in the product's actual subject matter.
// ---------------------------------------------------------------------------
function initPulseGrid() {
  const grid = document.getElementById("pulse-grid");
  const cells = [];
  for (let i = 0; i < 40; i++) {
    const cell = document.createElement("span");
    grid.appendChild(cell);
    cells.push(cell);
  }
  function tick() {
    cells.forEach((c) => (c.style.background = "var(--surface-3)"));
    const activeCount = 3 + Math.floor(Math.random() * 4);
    const used = new Set();
    for (let i = 0; i < activeCount; i++) {
      let idx;
      do { idx = Math.floor(Math.random() * cells.length); } while (used.has(idx));
      used.add(idx);
      const isAmber = Math.random() < 0.18;
      cells[idx].style.background = isAmber ? "var(--amber)" : "var(--green)";
      cells[idx].style.transition = "background .6s ease";
    }
    document.getElementById("ro-moist").textContent = (28 + Math.random() * 22).toFixed(1) + "%";
    document.getElementById("ro-temp").textContent = (21 + Math.random() * 9).toFixed(1) + "°C";
    document.getElementById("ro-hum").textContent = (45 + Math.random() * 25).toFixed(0) + "%";
  }
  tick();
  setInterval(tick, 1800);
}

// ---------------------------------------------------------------------------
// Boot
// ---------------------------------------------------------------------------
(async function boot() {
  initPulseGrid();
  await bootstrapSession();
  goTo(state.user ? "dashboard" : "home");
})();
