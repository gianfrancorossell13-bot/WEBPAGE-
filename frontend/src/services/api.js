export const API_URL = import.meta.env.VITE_API_URL ?? "http://127.0.0.1:8000";
export const IS_STATIC_DEMO =
  !import.meta.env.VITE_API_URL && window.location.hostname.endsWith("github.io");

const SESSION_KEY = "guardian_ciudadano_session";

const DEMO_USER = {
  id: 1,
  nombre: "Analista Guardian",
  email: "analista@guardian.pe",
  rol: "admin",
  activo: true,
};

const DEMO_DISTRICTS = [
  {
    distrito: "San Juan de Lurigancho",
    latitud: -11.9823,
    longitud: -77.0049,
    homicidio_2024: 155,
    hurto_2024: 7787,
    robo_2024: 4877,
    extorsion_2024: 1305,
    estafa_2024: 1192,
  },
  {
    distrito: "Callao",
    latitud: -12.0566,
    longitud: -77.1181,
    homicidio_2024: 157,
    hurto_2024: 3770,
    robo_2024: 3008,
    extorsion_2024: 889,
    estafa_2024: 356,
  },
  {
    distrito: "San Martin de Porres",
    latitud: -12.0308,
    longitud: -77.0805,
    homicidio_2024: 71,
    hurto_2024: 4322,
    robo_2024: 4395,
    extorsion_2024: 778,
    estafa_2024: 329,
  },
  {
    distrito: "Ate",
    latitud: -12.0266,
    longitud: -76.9198,
    homicidio_2024: 68,
    hurto_2024: 4513,
    robo_2024: 2927,
    extorsion_2024: 556,
    estafa_2024: 396,
  },
  {
    distrito: "Comas",
    latitud: -11.932,
    longitud: -77.0409,
    homicidio_2024: 93,
    hurto_2024: 3371,
    robo_2024: 3056,
    extorsion_2024: 663,
    estafa_2024: 607,
  },
  {
    distrito: "Los Olivos",
    latitud: -11.9763,
    longitud: -77.075,
    homicidio_2024: 33,
    hurto_2024: 3609,
    robo_2024: 3259,
    extorsion_2024: 696,
    estafa_2024: 321,
  },
  {
    distrito: "La Victoria",
    latitud: -12.0733,
    longitud: -77.0169,
    homicidio_2024: 25,
    hurto_2024: 4192,
    robo_2024: 2344,
    extorsion_2024: 378,
    estafa_2024: 194,
  },
  {
    distrito: "Independencia",
    latitud: -11.99,
    longitud: -77.045,
    homicidio_2024: 14,
    hurto_2024: 2961,
    robo_2024: 1857,
    extorsion_2024: 472,
    estafa_2024: 208,
  },
  {
    distrito: "Villa El Salvador",
    latitud: -12.215,
    longitud: -76.9437,
    homicidio_2024: 53,
    hurto_2024: 2233,
    robo_2024: 2306,
    extorsion_2024: 488,
    estafa_2024: 374,
  },
  {
    distrito: "Puente Piedra",
    latitud: -11.8667,
    longitud: -77.0833,
    homicidio_2024: 59,
    hurto_2024: 1924,
    robo_2024: 1461,
    extorsion_2024: 462,
    estafa_2024: 269,
  },
].map((item, index) => ({
  ...item,
  id: index + 1,
  total_2024:
    item.homicidio_2024 +
    item.hurto_2024 +
    item.robo_2024 +
    item.extorsion_2024 +
    item.estafa_2024,
}));

const DEMO_PRINCIPLES = [
  {
    nombre: "Layering",
    aplicacion: "Frontend -> API FastAPI -> servicios -> repositorios -> SQLite.",
    evidencia: "La UI consume contratos HTTP y no accede directo a la base de datos.",
  },
  {
    nombre: "Minimo privilegio",
    aplicacion: "Los endpoints de analitica requieren token y rol activo.",
    evidencia: "La informacion operativa se deniega por defecto sin Authorization Bearer.",
  },
  {
    nombre: "Mediacion completa",
    aplicacion: "Cada request protegido valida token, expiracion, usuario y estado activo.",
    evidencia: "No se confia solo en el login inicial del navegador.",
  },
  {
    nombre: "Separacion de responsabilidades",
    aplicacion: "Auth, analitica, acceso a datos y presentacion viven en modulos distintos.",
    evidencia: "Evita endpoints con validacion, SQL y UI mezclados.",
  },
  {
    nombre: "Fail-safe defaults",
    aplicacion: "Ante token ausente, invalido o expirado, la API responde 401.",
    evidencia: "El estado inseguro bloquea el acceso en vez de permitirlo.",
  },
  {
    nombre: "Registro verificado",
    aplicacion: "El alta de usuarios requiere un codigo temporal enviado al correo.",
    evidencia: "El codigo se guarda hasheado, vence en 10 minutos y limita intentos.",
  },
];

const DEMO_TYPE_FIELDS = {
  homicidio: "homicidio_2024",
  hurto: "hurto_2024",
  robo: "robo_2024",
  extorsion: "extorsion_2024",
  estafa: "estafa_2024",
};

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

function demoSession(user = DEMO_USER) {
  return {
    access_token: "github-pages-demo-token",
    token_type: "bearer",
    expires_at: Math.floor(Date.now() / 1000) + 60 * 60,
    user,
  };
}

function getTotalByType(type) {
  const field = DEMO_TYPE_FIELDS[type];
  return DEMO_DISTRICTS.reduce((sum, item) => sum + item[field], 0);
}

function getDemoRanking(type = "total", limit = 10) {
  const field = DEMO_TYPE_FIELDS[type];
  return [...DEMO_DISTRICTS]
    .map((item) => ({
      distrito: item.distrito,
      valor: field ? item[field] : item.total_2024,
      latitud: item.latitud,
      longitud: item.longitud,
    }))
    .sort((a, b) => b.valor - a.valor)
    .slice(0, limit);
}

function getDemoSummary() {
  const totals = Object.keys(DEMO_TYPE_FIELDS).map((type) => ({
    type,
    total: getTotalByType(type),
  }));
  const topCrime = totals.sort((a, b) => b.total - a.total)[0].type;
  const topDistrict = [...DEMO_DISTRICTS].sort((a, b) => b.total_2024 - a.total_2024)[0];

  return {
    total_delitos: DEMO_DISTRICTS.reduce((sum, item) => sum + item.total_2024, 0),
    total_distritos: DEMO_DISTRICTS.length,
    delito_mayor_presion: topCrime,
    distrito_mayor_presion: topDistrict.distrito,
  };
}

function getDemoIndicators() {
  return [
    {
      nombre: "Hurtos registrados",
      valor: getTotalByType("hurto"),
      descripcion: "Total de hurtos registrados en los distritos cargados.",
    },
    {
      nombre: "Robos registrados",
      valor: getTotalByType("robo"),
      descripcion: "Total de robos registrados en los distritos cargados.",
    },
    {
      nombre: "Extorsiones registradas",
      valor: getTotalByType("extorsion"),
      descripcion: "Total de extorsiones registradas en los distritos cargados.",
    },
    {
      nombre: "Homicidios registrados",
      valor: getTotalByType("homicidio"),
      descripcion: "Total de homicidios registrados en los distritos cargados.",
    },
  ];
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
    if (IS_STATIC_DEMO) {
      if (
        credentials.email.trim().toLowerCase() !== DEMO_USER.email ||
        credentials.password !== "Guardian2026!"
      ) {
        return Promise.reject(new ApiError("Usa la cuenta academica demo para ingresar.", 401));
      }

      return Promise.resolve(demoSession());
    }

    return request("/api/auth/login", {
      method: "POST",
      body: credentials,
    });
  },
  requestRegistration(payload) {
    if (IS_STATIC_DEMO) {
      return Promise.resolve({
        email: payload.email.trim().toLowerCase(),
        mensaje: "Codigo de verificacion generado en modo demo.",
        email_enviado: false,
        expira_en_segundos: 600,
        codigo_dev: "123456",
      });
    }

    return request("/api/auth/register/request", {
      method: "POST",
      body: payload,
    });
  },
  verifyRegistration(payload) {
    if (IS_STATIC_DEMO) {
      if (payload.codigo !== "123456") {
        return Promise.reject(new ApiError("Codigo de verificacion invalido.", 400));
      }

      return Promise.resolve(
        demoSession({
          ...DEMO_USER,
          nombre: "Analista Demo",
          email: payload.email.trim().toLowerCase(),
          rol: "analista",
        })
      );
    }

    return request("/api/auth/register/verify", {
      method: "POST",
      body: payload,
    });
  },
  me(token) {
    if (IS_STATIC_DEMO) {
      return token ? Promise.resolve(DEMO_USER) : Promise.reject(new ApiError("Sin sesion.", 401));
    }

    return request("/api/auth/me", { token });
  },
};

export const dashboardApi = {
  resumen(token) {
    if (IS_STATIC_DEMO) {
      return Promise.resolve(getDemoSummary());
    }

    return request("/api/resumen", { token });
  },
  distritos(token) {
    if (IS_STATIC_DEMO) {
      return Promise.resolve(DEMO_DISTRICTS);
    }

    return request("/api/distritos", { token });
  },
  indicadores(token) {
    if (IS_STATIC_DEMO) {
      return Promise.resolve(getDemoIndicators());
    }

    return request("/api/indicadores", { token });
  },
  ranking(token, tipo) {
    if (IS_STATIC_DEMO) {
      return Promise.resolve(getDemoRanking(tipo));
    }

    return request(`/api/ranking?tipo=${encodeURIComponent(tipo)}&limite=10`, { token });
  },
  principios(token) {
    if (IS_STATIC_DEMO) {
      return Promise.resolve(DEMO_PRINCIPLES);
    }

    return request("/api/principios", { token });
  },
};
