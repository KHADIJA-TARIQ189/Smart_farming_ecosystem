/* ==========================================================================
   FieldSense — API client
   Talks to the FastAPI backend (smart-farming-backend). Change API_BASE
   below if your backend runs somewhere other than localhost:8000.
   ========================================================================== */

const API_BASE = "http://localhost:8000";

/**
 * ApiError carries the human-readable message the UI should show,
 * plus the raw status code for anything that needs to branch on it.
 */
class ApiError extends Error {
  constructor(message, status) {
    super(message);
    this.status = status;
  }
}

function getToken() {
  return localStorage.getItem("fs_token");
}
function setToken(token) {
  localStorage.setItem("fs_token", token);
}
function clearToken() {
  localStorage.removeItem("fs_token");
}

/**
 * Core request helper. Adds the Authorization header automatically when a
 * token is present, and turns any non-2xx response into a readable ApiError
 * so the UI can show a clear success/failure message.
 */
async function request(path, { method = "GET", body, form, auth = true, signal } = {}) {
  const headers = {};
  if (auth && getToken()) {
    headers["Authorization"] = `Bearer ${getToken()}`;
  }

  let payload;
  if (form) {
    headers["Content-Type"] = "application/x-www-form-urlencoded";
    payload = new URLSearchParams(form).toString();
  } else if (body !== undefined) {
    headers["Content-Type"] = "application/json";
    payload = JSON.stringify(body);
  }

  let res;
  try {
    res = await fetch(`${API_BASE}${path}`, { method, headers, body: payload, signal });
  } catch (networkErr) {
    throw new ApiError(
      "Can't reach the backend. Make sure the FastAPI server is running on " + API_BASE + ".",
      0
    );
  }

  let data = null;
  const text = await res.text();
  if (text) {
    try { data = JSON.parse(text); } catch { data = null; }
  }

  if (!res.ok) {
    const detail = (data && (data.detail || data.message)) || res.statusText || "Something went wrong.";
    const message = typeof detail === "string" ? detail : JSON.stringify(detail);
    throw new ApiError(message, res.status);
  }

  return data;
}

const Api = {
  // ---- auth ----
  register: (name, email, password) =>
    request("/auth/register", { method: "POST", auth: false, body: { name, email, password } }),

  login: (email, password) =>
    request("/auth/login", { method: "POST", auth: false, form: { username: email, password } }),

  me: () => request("/users/me"),

  // ---- farms ----
  listFarms: () => request("/farms"),
  createFarm: (name, location) => request("/farms", { method: "POST", body: { name, location: location || null } }),
  getFarm: (farmId) => request(`/farms/${farmId}`),

  // ---- devices ----
  listDevices: (farmId) => request(`/farms/${farmId}/devices`),
  createDevice: (farmId, name, type) => request(`/farms/${farmId}/devices`, { method: "POST", body: { name, type } }),

  // ---- sensors ----
  latestReadings: (deviceId) => request(`/sensors/${deviceId}/latest`),
  sensorHistory: (deviceId, sensorType, limit = 100) => {
    const q = new URLSearchParams();
    if (sensorType) q.set("sensor_type", sensorType);
    q.set("limit", String(limit));
    return request(`/sensors/${deviceId}/history?${q.toString()}`);
  },
  ingestReading: (apiKey, sensorType, value, unit) =>
    request("/sensors/ingest", { method: "POST", auth: false, body: { api_key: apiKey, sensor_type: sensorType, value, unit } }),

  // ---- actuators ----
  controlActuator: (deviceId, actuatorType, action) =>
    request(`/actuators/${deviceId}/control`, { method: "POST", body: { actuator_type: actuatorType, action } }),
  actuatorLogs: (deviceId) => request(`/actuators/${deviceId}/logs`),

  // ---- crops ----
  listCrops: (farmId) => request(`/farms/${farmId}/crops`),
  createCrop: (farmId, cropType, zone) => request(`/farms/${farmId}/crops`, { method: "POST", body: { crop_type: cropType, zone: zone || null } }),
  cropProfile: (cropType) => request(`/crop-profiles/${cropType}`),

  // ---- alerts ----
  listAlerts: (farmId) => request(farmId ? `/alerts?farm_id=${farmId}` : "/alerts"),
  resolveAlert: (alertId) => request(`/alerts/${alertId}/resolve`, { method: "PATCH" }),

  // ---- health ----
  health: () => request("/health", { auth: false }),
};
