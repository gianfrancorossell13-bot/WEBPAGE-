from fastapi import Depends, FastAPI, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from .database import Base, SessionLocal, engine, get_db
from .dependencies import get_current_user, require_roles
from .repositories import UsuarioRepository
from .schemas import (
    DistritoDelitoOut,
    IndicadorOut,
    LoginRequest,
    PrincipioAplicadoOut,
    RankingItem,
    RegisterRequest,
    RegisterStartResponse,
    ResumenOut,
    TokenResponse,
    UsuarioOut,
    VerifyRegistrationRequest,
)
from .seed import cargar_datos_iniciales, cargar_usuario_academico
from .services import (
    PRINCIPIOS_APLICADOS,
    TIPOS_DELITO,
    AnalyticsService,
    AuthService,
    convertir_usuario,
)

Base.metadata.create_all(bind=engine)

db_inicio = SessionLocal()
try:
    cargar_datos_iniciales(db_inicio)
    cargar_usuario_academico(db_inicio)
finally:
    db_inicio.close()

app = FastAPI(
    title="Guardian Ciudadano Peru API",
    description="API segura para analizar delitos en Lima Metropolitana y Callao.",
    version="2.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type"],
)


@app.middleware("http")
async def agregar_cabeceras_seguras(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "no-referrer"
    response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
    return response


def servicio_analitica(db: Session = Depends(get_db)) -> AnalyticsService:
    return AnalyticsService(db)


@app.get("/")
def inicio():
    return {
        "mensaje": "API de Guardian Ciudadano Peru",
        "documentacion": "/docs",
        "version": "2.0.0",
    }


@app.get("/api/health")
def healthcheck():
    return {"status": "ok", "service": "guardian-ciudadano-api"}


@app.post("/api/auth/login", response_model=TokenResponse)
def login(payload: LoginRequest, request: Request, db: Session = Depends(get_db)):
    ip = request.client.host if request.client else None
    return AuthService(db).login(payload.email, payload.password, ip=ip)


@app.post("/api/auth/register/request", response_model=RegisterStartResponse)
def solicitar_registro(
    payload: RegisterRequest,
    request: Request,
    db: Session = Depends(get_db),
):
    ip = request.client.host if request.client else None
    return AuthService(db).solicitar_registro(
        payload.nombre,
        payload.email,
        payload.password,
        ip=ip,
    )


@app.post("/api/auth/register/verify", response_model=TokenResponse)
def verificar_registro(
    payload: VerifyRegistrationRequest,
    request: Request,
    db: Session = Depends(get_db),
):
    ip = request.client.host if request.client else None
    return AuthService(db).verificar_registro(payload.email, payload.codigo, ip=ip)


@app.get("/api/auth/me", response_model=UsuarioOut)
def obtener_sesion(usuario: UsuarioOut = Depends(get_current_user)):
    return usuario


@app.get("/api/admin/usuarios", response_model=list[UsuarioOut])
def listar_usuarios(
    _: UsuarioOut = Depends(require_roles("admin")),
    db: Session = Depends(get_db),
):
    return [convertir_usuario(usuario) for usuario in UsuarioRepository(db).listar_activos()]


@app.get("/api/principios", response_model=list[PrincipioAplicadoOut])
def listar_principios(_: UsuarioOut = Depends(get_current_user)):
    return PRINCIPIOS_APLICADOS


@app.get("/api/distritos", response_model=list[DistritoDelitoOut])
def listar_distritos(
    _: UsuarioOut = Depends(get_current_user),
    analitica: AnalyticsService = Depends(servicio_analitica),
):
    return analitica.listar_distritos()


@app.get("/api/tipos-delito")
def listar_tipos_delito(_: UsuarioOut = Depends(get_current_user)):
    return ["total", *TIPOS_DELITO.keys()]


@app.get("/api/resumen", response_model=ResumenOut)
def obtener_resumen(
    _: UsuarioOut = Depends(get_current_user),
    analitica: AnalyticsService = Depends(servicio_analitica),
):
    return analitica.obtener_resumen()


@app.get("/api/ranking", response_model=list[RankingItem])
def obtener_ranking(
    tipo: str = Query("total", description="total, homicidio, hurto, robo, extorsion o estafa"),
    limite: int = Query(10, ge=1, le=50),
    _: UsuarioOut = Depends(get_current_user),
    analitica: AnalyticsService = Depends(servicio_analitica),
):
    return analitica.obtener_ranking(tipo=tipo, limite=limite)


@app.get("/api/hotspots", response_model=list[RankingItem])
def obtener_hotspots(
    tipo: str = Query("total", description="total, homicidio, hurto, robo, extorsion o estafa"),
    _: UsuarioOut = Depends(get_current_user),
    analitica: AnalyticsService = Depends(servicio_analitica),
):
    return analitica.obtener_ranking(tipo=tipo, limite=5)


@app.get("/api/indicadores", response_model=list[IndicadorOut])
def obtener_indicadores(
    _: UsuarioOut = Depends(get_current_user),
    analitica: AnalyticsService = Depends(servicio_analitica),
):
    return analitica.obtener_indicadores()
