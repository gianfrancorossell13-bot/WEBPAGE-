import secrets
from datetime import datetime, timedelta

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from .email_sender import enviar_codigo_verificacion, mostrar_codigos_dev
from .models import DistritoDelito, RegistroPendiente, Usuario
from .repositories import (
    AuditRepository,
    DistritoRepository,
    RegistroPendienteRepository,
    UsuarioRepository,
)
from .schemas import DistritoDelitoOut, IndicadorOut, RankingItem, ResumenOut, UsuarioOut
from .security import crear_token_acceso, hash_password, normalizar_email, verificar_password


TIPOS_DELITO = {
    "homicidio": "homicidio_2024",
    "hurto": "hurto_2024",
    "robo": "robo_2024",
    "extorsion": "extorsion_2024",
    "estafa": "estafa_2024",
}

REGISTRATION_CODE_TTL_SECONDS = 600
REGISTRATION_MAX_ATTEMPTS = 5


PRINCIPIOS_APLICADOS = [
    {
        "nombre": "Layering",
        "aplicacion": "Frontend -> API FastAPI -> servicios -> repositorios -> SQLite.",
        "evidencia": "La UI no accede a la base de datos; consume contratos HTTP.",
    },
    {
        "nombre": "Minimo privilegio",
        "aplicacion": "Los endpoints de analitica requieren token y rol activo.",
        "evidencia": "La informacion operativa se deniega por defecto sin Authorization Bearer.",
    },
    {
        "nombre": "Mediacion completa",
        "aplicacion": "Cada request protegido valida token, expiracion, usuario y estado activo.",
        "evidencia": "No se confia solo en el login inicial del navegador.",
    },
    {
        "nombre": "Separacion de responsabilidades",
        "aplicacion": "Auth, analitica, acceso a datos y presentacion viven en modulos distintos.",
        "evidencia": "Evita endpoints con validacion, SQL y UI mezclados.",
    },
    {
        "nombre": "Fail-safe defaults",
        "aplicacion": "Ante token ausente, invalido o expirado, la API responde 401.",
        "evidencia": "El estado inseguro bloquea el acceso en vez de permitirlo.",
    },
    {
        "nombre": "Registro verificado",
        "aplicacion": "El alta de usuarios requiere un codigo temporal enviado al correo.",
        "evidencia": "El codigo se guarda hasheado, vence en 10 minutos y limita intentos.",
    },
]


def calcular_total(item: DistritoDelito) -> int:
    return (
        item.homicidio_2024
        + item.hurto_2024
        + item.robo_2024
        + item.extorsion_2024
        + item.estafa_2024
    )


def convertir_salida(item: DistritoDelito) -> DistritoDelitoOut:
    return DistritoDelitoOut(
        id=item.id,
        distrito=item.distrito,
        latitud=item.latitud,
        longitud=item.longitud,
        homicidio_2024=item.homicidio_2024,
        hurto_2024=item.hurto_2024,
        robo_2024=item.robo_2024,
        extorsion_2024=item.extorsion_2024,
        estafa_2024=item.estafa_2024,
        total_2024=calcular_total(item),
    )


def convertir_usuario(usuario: Usuario) -> UsuarioOut:
    return UsuarioOut(
        id=usuario.id,
        nombre=usuario.nombre,
        email=usuario.email,
        rol=usuario.rol,
        activo=usuario.activo,
    )


class AuthService:
    def __init__(self, db: Session):
        self.db = db
        self.usuarios = UsuarioRepository(db)
        self.registros = RegistroPendienteRepository(db)
        self.audit = AuditRepository(db)

    def login(self, email: str, password: str, ip: str | None = None) -> dict:
        email_normalizado = normalizar_email(email)
        usuario = self.usuarios.obtener_por_email(email_normalizado)

        if not usuario or not usuario.activo:
            self.audit.registrar("login", "fallido", ip=ip, detalle=email_normalizado)
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Credenciales invalidas.",
            )

        if not verificar_password(password, usuario.password_salt, usuario.password_hash):
            self.audit.registrar("login", "fallido", usuario_id=usuario.id, ip=ip)
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Credenciales invalidas.",
            )

        token = crear_token_acceso(usuario.id, usuario.email, usuario.rol)
        usuario.ultimo_login_en = datetime.utcnow()
        self.db.commit()
        self.audit.registrar("login", "exitoso", usuario_id=usuario.id, ip=ip)
        return {
            **token,
            "token_type": "bearer",
            "user": convertir_usuario(usuario),
        }

    def solicitar_registro(
        self,
        nombre: str,
        email: str,
        password: str,
        ip: str | None = None,
    ) -> dict:
        email_normalizado = normalizar_email(email)

        if self.usuarios.obtener_por_email(email_normalizado):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Este correo ya esta registrado.",
            )

        codigo = f"{secrets.randbelow(1_000_000):06d}"
        password_salt, password_hash = hash_password(password)
        codigo_salt, codigo_hash = hash_password(codigo)
        expira_en = datetime.utcnow() + timedelta(seconds=REGISTRATION_CODE_TTL_SECONDS)
        registro = self.registros.obtener_por_email(email_normalizado)

        if registro:
            registro.nombre = nombre
            registro.password_hash = password_hash
            registro.password_salt = password_salt
            registro.codigo_hash = codigo_hash
            registro.codigo_salt = codigo_salt
            registro.intentos = 0
            registro.consumido = False
            registro.expira_en = expira_en
        else:
            registro = RegistroPendiente(
                nombre=nombre,
                email=email_normalizado,
                password_hash=password_hash,
                password_salt=password_salt,
                codigo_hash=codigo_hash,
                codigo_salt=codigo_salt,
                expira_en=expira_en,
            )

        self.registros.guardar(registro)

        try:
            email_enviado = enviar_codigo_verificacion(email_normalizado, codigo)
        except Exception as exc:
            self.audit.registrar(
                "registro_codigo",
                "email_fallido",
                ip=ip,
                detalle=f"{email_normalizado}: {exc}",
            )
            if not mostrar_codigos_dev():
                detalle = "Revisa conexion a SMTP, puerto, firewall o App Password de Gmail."
                if isinstance(exc, TimeoutError):
                    detalle = "No se pudo conectar con Gmail SMTP. Revisa red, firewall o puerto SMTP."
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail=detalle,
                ) from exc
            email_enviado = False

        if not email_enviado and not mostrar_codigos_dev():
            self.audit.registrar(
                "registro_codigo",
                "smtp_no_configurado",
                ip=ip,
                detalle=email_normalizado,
            )
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=(
                    "El envio de correo no esta configurado. "
                    "Configura las variables SMTP del backend."
                ),
            )

        self.audit.registrar("registro_codigo", "generado", ip=ip, detalle=email_normalizado)
        return {
            "email": email_normalizado,
            "mensaje": "Codigo de verificacion generado.",
            "email_enviado": email_enviado,
            "expira_en_segundos": REGISTRATION_CODE_TTL_SECONDS,
            "codigo_dev": codigo if not email_enviado and mostrar_codigos_dev() else None,
        }

    def verificar_registro(
        self,
        email: str,
        codigo: str,
        ip: str | None = None,
    ) -> dict:
        email_normalizado = normalizar_email(email)
        registro = self.registros.obtener_por_email(email_normalizado)

        if not registro or registro.consumido:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No existe un registro pendiente para este correo.",
            )

        if self.usuarios.obtener_por_email(email_normalizado):
            registro.consumido = True
            self.db.commit()
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Este correo ya esta registrado.",
            )

        if registro.expira_en < datetime.utcnow():
            self.audit.registrar("registro_verificacion", "expirado", ip=ip, detalle=email_normalizado)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El codigo expiro. Solicita uno nuevo.",
            )

        if registro.intentos >= REGISTRATION_MAX_ATTEMPTS:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Demasiados intentos. Solicita un nuevo codigo.",
            )

        if not verificar_password(codigo, registro.codigo_salt, registro.codigo_hash):
            registro.intentos += 1
            self.db.commit()
            self.audit.registrar("registro_verificacion", "fallido", ip=ip, detalle=email_normalizado)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Codigo de verificacion invalido.",
            )

        usuario = Usuario(
            nombre=registro.nombre,
            email=registro.email,
            password_hash=registro.password_hash,
            password_salt=registro.password_salt,
            rol="analista",
            activo=True,
            ultimo_login_en=datetime.utcnow(),
        )
        registro.consumido = True
        self.db.add(usuario)
        self.db.commit()
        self.db.refresh(usuario)

        self.audit.registrar(
            "registro_verificacion",
            "exitoso",
            usuario_id=usuario.id,
            ip=ip,
            detalle=email_normalizado,
        )
        token = crear_token_acceso(usuario.id, usuario.email, usuario.rol)
        return {
            **token,
            "token_type": "bearer",
            "user": convertir_usuario(usuario),
        }


class AnalyticsService:
    def __init__(self, db: Session):
        self.distritos = DistritoRepository(db)

    def listar_distritos(self) -> list[DistritoDelitoOut]:
        return [convertir_salida(item) for item in self.distritos.listar()]

    def obtener_resumen(self) -> ResumenOut:
        datos = self.distritos.listar()

        if not datos:
            raise HTTPException(status_code=404, detail="No hay datos registrados.")

        totales_por_tipo = {
            tipo: sum(getattr(item, campo) for item in datos)
            for tipo, campo in TIPOS_DELITO.items()
        }

        distrito_top = max(datos, key=calcular_total)
        delito_top = max(totales_por_tipo, key=totales_por_tipo.get)

        return ResumenOut(
            total_delitos=sum(totales_por_tipo.values()),
            total_distritos=len(datos),
            delito_mayor_presion=delito_top,
            distrito_mayor_presion=distrito_top.distrito,
        )

    def obtener_ranking(self, tipo: str = "total", limite: int = 10) -> list[RankingItem]:
        datos = self.distritos.listar()

        if tipo != "total" and tipo not in TIPOS_DELITO:
            raise HTTPException(status_code=400, detail="Tipo de delito no valido.")

        ranking = []

        for item in datos:
            valor = calcular_total(item) if tipo == "total" else getattr(item, TIPOS_DELITO[tipo])
            ranking.append(
                RankingItem(
                    distrito=item.distrito,
                    valor=valor,
                    latitud=item.latitud,
                    longitud=item.longitud,
                )
            )

        ranking.sort(key=lambda item: item.valor, reverse=True)
        return ranking[:limite]

    def obtener_indicadores(self) -> list[IndicadorOut]:
        datos = self.distritos.listar()

        return [
            IndicadorOut(
                nombre="Hurtos registrados",
                valor=sum(item.hurto_2024 for item in datos),
                descripcion="Total de hurtos registrados en los distritos cargados.",
            ),
            IndicadorOut(
                nombre="Robos registrados",
                valor=sum(item.robo_2024 for item in datos),
                descripcion="Total de robos registrados en los distritos cargados.",
            ),
            IndicadorOut(
                nombre="Extorsiones registradas",
                valor=sum(item.extorsion_2024 for item in datos),
                descripcion="Total de extorsiones registradas en los distritos cargados.",
            ),
            IndicadorOut(
                nombre="Homicidios registrados",
                valor=sum(item.homicidio_2024 for item in datos),
                descripcion="Total de homicidios registrados en los distritos cargados.",
            ),
        ]
