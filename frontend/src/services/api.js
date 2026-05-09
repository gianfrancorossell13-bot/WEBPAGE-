export const API_URL = import.meta.env.VITE_API_URL ?? "http://127.0.0.1:8000";

const SESSION_KEY = "guardian_ciudadano_session";

export class ApiError extends Error {
  constructor(message, status) {
    super(message);
    this.name = "ApiError";
    this.status = status;
  }
}

async function request(path, { method = "GET", token, body } = {}) {
  const headers = {
    Accept: "application/json",
  };

  if (token) {
    headers.Authorization = `Bearer ${token}`;
  }

  if (body) {
    headers["Content-Type"] = "application/json";
  }

  const response = await fetch(`${API_URL}${path}`, {
    method,
    headers,
    body: body ? JSON.stringify(body) : undefined,
  });

  const contentType = response.headers.get("content-type") ?? "";
  const data = contentType.includes("application/json") ? await response.json() : null;

  if (!response.ok) {
    throw new ApiError(data?.detail ?? "No se pudo completar la solicitud.", response.status);
  }

  return data;
}

export const sessionStore = {
  get() {
    try {
      return JSON.parse(localStorage.getItem(SESSION_KEY));
    } catch {
      return null;
    }
  },
  set(session) {
    localStorage.setItem(SESSION_KEY, JSON.stringify(session));
  },
  clear() {
    localStorage.removeItem(SESSION_KEY);
  },
};

export const authApi = {
  login(credentials) {
    return request("/api/auth/login", {
      method: "POST",
      body: credentials,
    });
  },
  requestRegistration(payload) {
    return request("/api/auth/register/request", {
      method: "POST",
      body: payload,
    });
  },
  verifyRegistration(payload) {
    return request("/api/auth/register/verify", {
      method: "POST",
      body: payload,
    });
  },
  me(token) {
    return request("/api/auth/me", { token });
  },
};

export const dashboardApi = {
  resumen(token) {
    return request("/api/resumen", { token });
  },
  distritos(token) {
    return request("/api/distritos", { token });
  },
  indicadores(token) {
    return request("/api/indicadores", { token });
  },
  ranking(token, tipo) {
    return request(`/api/ranking?tipo=${encodeURIComponent(tipo)}&limite=10`, { token });
  },
  principios(token) {
    return request("/api/principios", { token });
  },
};
