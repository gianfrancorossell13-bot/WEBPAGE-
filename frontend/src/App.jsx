import { useEffect, useMemo, useState } from "react";
import { MapContainer, Marker, Popup, TileLayer } from "react-leaflet";
import L from "leaflet";
import {
  Bar,
  BarChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import {
  Activity,
  AlertTriangle,
  ArrowLeft,
  BarChart3,
  CheckCircle2,
  Database,
  Filter,
  KeyRound,
  Layers,
  LogIn,
  LogOut,
  Mail,
  MapPinned,
  ShieldCheck,
  UserPlus,
  UserRound,
} from "lucide-react";
import {
  API_URL,
  IS_STATIC_DEMO,
  ApiError,
  authApi,
  dashboardApi,
  sessionStore,
} from "./services/api";

const iconoMapa = L.icon({
  iconUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png",
  shadowUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png",
  iconAnchor: [12, 41],
});

const tipos = [
  { value: "total", label: "Total" },
  { value: "homicidio", label: "Homicidio" },
  { value: "hurto", label: "Hurto" },
  { value: "robo", label: "Robo" },
  { value: "extorsion", label: "Extorsion" },
  { value: "estafa", label: "Estafa" },
];

function App() {
  const [session, setSession] = useState(() => sessionStore.get());
  const [verificandoSesion, setVerificandoSesion] = useState(Boolean(session?.access_token));

  useEffect(() => {
    async function validarSesion() {
      const cached = sessionStore.get();

      if (!cached?.access_token) {
        setVerificandoSesion(false);
        return;
      }

      try {
        const user = await authApi.me(cached.access_token);
        const refreshed = { ...cached, user };
        sessionStore.set(refreshed);
        setSession(refreshed);
      } catch {
        sessionStore.clear();
        setSession(null);
      } finally {
        setVerificandoSesion(false);
      }
    }

    validarSesion();
  }, []);

  function handleAuthenticated(authSession) {
    sessionStore.set(authSession);
    setSession(authSession);
  }

  function handleLogout() {
    sessionStore.clear();
    setSession(null);
  }

  if (verificandoSesion) {
    return (
      <main className="page center">
        <div className="loadingBox">
          <ShieldCheck size={28} />
          <p>Validando sesion segura...</p>
        </div>
      </main>
    );
  }

  if (!session?.access_token) {
    return <AuthView onAuthenticated={handleAuthenticated} />;
  }

  return <Dashboard session={session} onUnauthorized={handleLogout} onLogout={handleLogout} />;
}

function AuthView({ onAuthenticated }) {
  const [mode, setMode] = useState("login");
  const [email, setEmail] = useState("analista@guardian.pe");
  const [password, setPassword] = useState("Guardian2026!");
  const [nombre, setNombre] = useState("");
  const [codigo, setCodigo] = useState("");
  const [pendingRegistration, setPendingRegistration] = useState(null);
  const [error, setError] = useState("");
  const [statusMessage, setStatusMessage] = useState("");
  const [loading, setLoading] = useState(false);

  async function submitLogin(event) {
    event.preventDefault();
    try {
      setLoading(true);
      setError("");
      setStatusMessage("");
      const authSession = await authApi.login({ email, password });
      onAuthenticated(authSession);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "No se pudo conectar con el backend.");
    } finally {
      setLoading(false);
    }
  }

  async function submitRegister(event) {
    event.preventDefault();
    try {
      setLoading(true);
      setError("");
      setStatusMessage("");
      const response = await authApi.requestRegistration({ nombre, email, password });
      setPendingRegistration(response);
      setCodigo(response.codigo_dev ?? "");
      setMode("verify");
      setStatusMessage(
        response.email_enviado
          ? "Te enviamos un codigo de 6 digitos al correo indicado."
          : "SMTP no esta configurado. Usa el codigo de desarrollo mostrado abajo."
      );
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "No se pudo solicitar el registro.");
    } finally {
      setLoading(false);
    }
  }

  async function submitVerification(event) {
    event.preventDefault();
    try {
      setLoading(true);
      setError("");
      const authSession = await authApi.verifyRegistration({ email, codigo });
      onAuthenticated(authSession);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "No se pudo verificar el codigo.");
    } finally {
      setLoading(false);
    }
  }

  function switchMode(nextMode) {
    setMode(nextMode);
    setError("");
    setStatusMessage("");
    setPendingRegistration(null);
    setCodigo("");
  }

  return (
    <main className="loginPage">
      <section className="loginIntro">
        <div className="brandMark">
          <ShieldCheck size={24} />
        </div>
        <p className="eyebrow">MVP seguro | Arquitectura de Aplicaciones</p>
        <h1>Guardian Ciudadano Peru</h1>
        <p>
          Plataforma de analisis territorial con autenticacion, separacion por capas y
          controles aplicados desde el diseno.
        </p>
        <div className="loginPrinciples">
          <span><Layers size={16} /> Layering</span>
          <span><KeyRound size={16} /> Minimo privilegio</span>
          <span><Activity size={16} /> Auditoria</span>
        </div>
      </section>

      <section className="loginCard" aria-label="Autenticacion">
        <div>
          <p className="eyebrow">
            {mode === "verify" ? "Verificacion de correo" : "Acceso autorizado"}
          </p>
          <h2>
            {mode === "login" && "Iniciar sesion"}
            {mode === "register" && "Crear cuenta"}
            {mode === "verify" && "Confirmar codigo"}
          </h2>
        </div>

        {mode !== "verify" && (
          <div className="modeSwitch" role="tablist" aria-label="Modo de autenticacion">
            <button
              className={mode === "login" ? "active" : ""}
              type="button"
              onClick={() => switchMode("login")}
            >
              Entrar
            </button>
            <button
              className={mode === "register" ? "active" : ""}
              type="button"
              onClick={() => switchMode("register")}
            >
              Registrarme
            </button>
          </div>
        )}

        {mode === "login" && (
          <form onSubmit={submitLogin} className="loginForm">
            <EmailField email={email} setEmail={setEmail} />
            <PasswordField password={password} setPassword={setPassword} />
            {error && <div className="errorBox">{error}</div>}
            <button className="primaryButton" type="submit" disabled={loading}>
              <LogIn size={18} />
              {loading ? "Validando..." : "Entrar"}
            </button>
          </form>
        )}

        {mode === "register" && (
          <form onSubmit={submitRegister} className="loginForm">
            <label>
              Nombre
              <div className="inputBox">
                <UserRound size={18} />
                <input
                  type="text"
                  value={nombre}
                  onChange={(event) => setNombre(event.target.value)}
                  autoComplete="name"
                  placeholder="Tu nombre"
                  required
                />
              </div>
            </label>
            <EmailField email={email} setEmail={setEmail} />
            <PasswordField password={password} setPassword={setPassword} />
            <p className="helperText">
              Usa 8 caracteres con mayuscula, minuscula, numero y simbolo.
            </p>
            {error && <div className="errorBox">{error}</div>}
            <button className="primaryButton" type="submit" disabled={loading}>
              <UserPlus size={18} />
              {loading ? "Enviando codigo..." : "Enviar codigo"}
            </button>
          </form>
        )}

        {mode === "verify" && (
          <form onSubmit={submitVerification} className="loginForm">
            {statusMessage && (
              <div className="successBox">
                <CheckCircle2 size={18} />
                <span>{statusMessage}</span>
              </div>
            )}
            <label>
              Correo
              <div className="inputBox">
                <Mail size={18} />
                <input type="email" value={email} readOnly />
              </div>
            </label>
            <label>
              Codigo de verificacion
              <div className="inputBox codeInput">
                <KeyRound size={18} />
                <input
                  type="text"
                  inputMode="numeric"
                  pattern="[0-9]{6}"
                  maxLength={6}
                  value={codigo}
                  onChange={(event) => setCodigo(event.target.value.replace(/\D/g, ""))}
                  placeholder="000000"
                  required
                />
              </div>
            </label>
            {pendingRegistration?.codigo_dev && (
              <div className="codeHint">
                Codigo de desarrollo: <strong>{pendingRegistration.codigo_dev}</strong>
              </div>
            )}
            {error && <div className="errorBox">{error}</div>}
            <button className="primaryButton" type="submit" disabled={loading}>
              <CheckCircle2 size={18} />
              {loading ? "Verificando..." : "Verificar y entrar"}
            </button>
            <button className="ghostButton" type="button" onClick={() => switchMode("register")}>
              <ArrowLeft size={16} />
              Cambiar datos
            </button>
          </form>
        )}

        <div className="demoAccount">
          Cuenta academica: <strong>analista@guardian.pe</strong> / <strong>Guardian2026!</strong>
        </div>
      </section>
    </main>
  );
}

function EmailField({ email, setEmail }) {
  return (
    <label>
      Correo
      <div className="inputBox">
        <Mail size={18} />
        <input
          type="email"
          value={email}
          onChange={(event) => setEmail(event.target.value)}
          autoComplete="username"
          required
        />
      </div>
    </label>
  );
}

function PasswordField({ password, setPassword }) {
  return (
    <label>
      Contrasena
      <div className="inputBox">
        <KeyRound size={18} />
        <input
          type="password"
          value={password}
          onChange={(event) => setPassword(event.target.value)}
          autoComplete="current-password"
          required
        />
      </div>
    </label>
  );
}

function Dashboard({ session, onUnauthorized, onLogout }) {
  const [resumen, setResumen] = useState(null);
  const [distritos, setDistritos] = useState([]);
  const [ranking, setRanking] = useState([]);
  const [indicadores, setIndicadores] = useState([]);
  const [principios, setPrincipios] = useState([]);
  const [tipoDelito, setTipoDelito] = useState("total");
  const [cargando, setCargando] = useState(true);
  const [error, setError] = useState("");

  const token = session.access_token;

  useEffect(() => {
    async function cargarDatos() {
      try {
        setError("");
        setCargando(true);

        const [resumenData, distritosData, indicadoresData, principiosData] =
          await Promise.all([
            dashboardApi.resumen(token),
            dashboardApi.distritos(token),
            dashboardApi.indicadores(token),
            dashboardApi.principios(token),
          ]);

        setResumen(resumenData);
        setDistritos(distritosData);
        setIndicadores(indicadoresData);
        setPrincipios(principiosData);
      } catch (err) {
        if (err instanceof ApiError && err.status === 401) {
          onUnauthorized();
          return;
        }
        setError("No se pudo cargar el tablero. Verifica que el backend este activo.");
      } finally {
        setCargando(false);
      }
    }

    cargarDatos();
  }, [token, onUnauthorized]);

  useEffect(() => {
    async function cargarRanking() {
      try {
        const rankingData = await dashboardApi.ranking(token, tipoDelito);
        setRanking(rankingData);
      } catch (err) {
        if (err instanceof ApiError && err.status === 401) {
          onUnauthorized();
          return;
        }
        setError("No se pudo cargar el ranking.");
      }
    }

    cargarRanking();
  }, [token, tipoDelito, onUnauthorized]);

  const totalMapa = useMemo(() => {
    return distritos.reduce((suma, item) => suma + item.total_2024, 0);
  }, [distritos]);

  if (cargando) {
    return (
      <main className="page center">
        <div className="loadingBox">
          <Database size={28} />
          <p>Cargando tablero operativo...</p>
        </div>
      </main>
    );
  }

  return (
    <main className="appShell">
      <header className="topBar">
        <div className="brandBlock">
          <div className="brandMark compact">
            <ShieldCheck size={20} />
          </div>
          <div>
            <strong>Guardian Ciudadano Peru</strong>
            <span>Analitica segura de delitos</span>
          </div>
        </div>

        <nav className="topActions" aria-label="Acciones principales">
          {IS_STATIC_DEMO ? (
            <a href="https://github.com/gianfrancorossell13-bot/WEBPAGE-" target="_blank" rel="noreferrer">
              Repo GitHub
            </a>
          ) : (
            <a href={`${API_URL}/docs`} target="_blank" rel="noreferrer">
              API Docs
            </a>
          )}
          <div className="userBadge">
            <UserRound size={16} />
            <span>{session.user?.nombre}</span>
            <small>{session.user?.rol}</small>
          </div>
          <button className="iconButton" type="button" onClick={onLogout} title="Cerrar sesion">
            <LogOut size={18} />
          </button>
        </nav>
      </header>

      {error && <div className="errorBox">{error}</div>}

      <section className="summaryHeader">
        <div>
          <p className="eyebrow">Vista ejecutiva</p>
          <h1>Tablero de presion delictiva</h1>
          <p>
            Datos consolidados de Lima Metropolitana y Callao protegidos por autenticacion y
            contratos de API.
          </p>
        </div>
        <div className="securityState">
          <ShieldCheck size={22} />
          <span>Sesion validada por token</span>
        </div>
      </section>

      <section className="cards">
        <InfoCard
          icon={<Database />}
          title="Total delitos"
          value={resumen?.total_delitos ?? 0}
          text="Suma de delitos en la muestra cargada."
        />
        <InfoCard
          icon={<MapPinned />}
          title="Distritos"
          value={resumen?.total_distritos ?? 0}
          text="Cobertura territorial analizada."
        />
        <InfoCard
          icon={<AlertTriangle />}
          title="Mayor presion"
          value={resumen?.distrito_mayor_presion ?? "-"}
          text="Distrito con mayor acumulado."
        />
        <InfoCard
          icon={<BarChart3 />}
          title="Delito destacado"
          value={resumen?.delito_mayor_presion ?? "-"}
          text="Tipo de delito con mayor volumen."
        />
      </section>

      <section className="layout">
        <article className="panel" id="mapa">
          <div className="panelHeader">
            <div>
              <p className="eyebrow">Analisis geoespacial</p>
              <h2>Mapa de puntos criticos</h2>
            </div>
            <span>{totalMapa.toLocaleString()} registros</span>
          </div>

          <MapContainer
            center={[-12.05, -77.04]}
            zoom={10}
            className="map"
            scrollWheelZoom={false}
          >
            <TileLayer
              attribution="&copy; OpenStreetMap contributors"
              url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
            />
            {distritos.map((item) => (
              <Marker
                key={item.id}
                position={[item.latitud, item.longitud]}
                icon={iconoMapa}
              >
                <Popup>
                  <strong>{item.distrito}</strong>
                  <br />
                  Total 2024: {item.total_2024.toLocaleString()}
                  <br />
                  Robo: {item.robo_2024.toLocaleString()}
                  <br />
                  Hurto: {item.hurto_2024.toLocaleString()}
                  <br />
                  Extorsion: {item.extorsion_2024.toLocaleString()}
                </Popup>
              </Marker>
            ))}
          </MapContainer>
        </article>

        <article className="panel">
          <div className="panelHeader">
            <div>
              <p className="eyebrow">Ranking</p>
              <h2>Distritos con mayor presion</h2>
            </div>
            <label className="selectLabel">
              <Filter size={16} />
              <select
                value={tipoDelito}
                onChange={(event) => setTipoDelito(event.target.value)}
              >
                {tipos.map((tipo) => (
                  <option key={tipo.value} value={tipo.value}>
                    {tipo.label}
                  </option>
                ))}
              </select>
            </label>
          </div>

          <div className="chartBox">
            <ResponsiveContainer width="100%" height={320}>
              <BarChart data={ranking}>
                <CartesianGrid stroke="#E5E7EB" vertical={false} />
                <XAxis
                  dataKey="distrito"
                  tick={{ fontSize: 11, fill: "#4B5563" }}
                  interval={0}
                  angle={-25}
                  textAnchor="end"
                  height={84}
                />
                <YAxis tick={{ fontSize: 12, fill: "#4B5563" }} />
                <Tooltip />
                <Bar dataKey="valor" fill="#2563EB" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </article>
      </section>

      <section className="layout secondary">
        <article className="panel">
          <div className="panelHeader">
            <div>
              <p className="eyebrow">Indicadores</p>
              <h2>Resumen operativo</h2>
            </div>
          </div>

          <div className="indicators">
            {indicadores.map((item) => (
              <div className="indicator" key={item.nombre}>
                <h3>{item.nombre}</h3>
                <strong>{Number(item.valor).toLocaleString()}</strong>
                <p>{item.descripcion}</p>
              </div>
            ))}
          </div>
        </article>

        <article className="panel">
          <div className="panelHeader">
            <div>
              <p className="eyebrow">Arquitectura segura</p>
              <h2>Principios aplicados</h2>
            </div>
          </div>

          <div className="principlesList">
            {principios.map((item) => (
              <div className="principleItem" key={item.nombre}>
                <strong>{item.nombre}</strong>
                <p>{item.aplicacion}</p>
                <span>{item.evidencia}</span>
              </div>
            ))}
          </div>
        </article>
      </section>
    </main>
  );
}

function InfoCard({ icon, title, value, text }) {
  return (
    <article className="infoCard">
      <div className="iconBox">{icon}</div>
      <h2>{title}</h2>
      <strong>{typeof value === "number" ? value.toLocaleString() : value}</strong>
      <p>{text}</p>
    </article>
  );
}

export default App;
