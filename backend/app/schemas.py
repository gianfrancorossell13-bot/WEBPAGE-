from pydantic import BaseModel, Field, field_validator

from .security import normalizar_email, validar_fortaleza_password


class LoginRequest(BaseModel):
    email: str = Field(min_length=5, max_length=255)
    password: str = Field(min_length=8, max_length=128)

    @field_validator("email")
    @classmethod
    def validar_email(cls, value: str) -> str:
        email = normalizar_email(value)
        if "@" not in email or "." not in email.split("@")[-1]:
            raise ValueError("Correo electronico invalido.")
        return email


class RegisterRequest(BaseModel):
    nombre: str = Field(min_length=2, max_length=120)
    email: str = Field(min_length=5, max_length=255)
    password: str = Field(min_length=8, max_length=128)

    @field_validator("nombre")
    @classmethod
    def validar_nombre(cls, value: str) -> str:
        nombre = " ".join(value.strip().split())
        if len(nombre) < 2:
            raise ValueError("Nombre invalido.")
        return nombre

    @field_validator("email")
    @classmethod
    def validar_email(cls, value: str) -> str:
        email = normalizar_email(value)
        if "@" not in email or "." not in email.split("@")[-1]:
            raise ValueError("Correo electronico invalido.")
        return email

    @field_validator("password")
    @classmethod
    def validar_password(cls, value: str) -> str:
        validar_fortaleza_password(value)
        return value


class VerifyRegistrationRequest(BaseModel):
    email: str = Field(min_length=5, max_length=255)
    codigo: str = Field(min_length=6, max_length=6)

    @field_validator("email")
    @classmethod
    def validar_email(cls, value: str) -> str:
        email = normalizar_email(value)
        if "@" not in email or "." not in email.split("@")[-1]:
            raise ValueError("Correo electronico invalido.")
        return email

    @field_validator("codigo")
    @classmethod
    def validar_codigo(cls, value: str) -> str:
        codigo = value.strip()
        if not codigo.isdigit():
            raise ValueError("El codigo debe tener 6 digitos.")
        return codigo


class RegisterStartResponse(BaseModel):
    email: str
    mensaje: str
    email_enviado: bool
    expira_en_segundos: int
    codigo_dev: str | None = None


class UsuarioOut(BaseModel):
    id: int
    nombre: str
    email: str
    rol: str
    activo: bool


class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    expires_at: int
    user: UsuarioOut


class DistritoDelitoBase(BaseModel):
    distrito: str
    latitud: float
    longitud: float
    homicidio_2024: int
    hurto_2024: int
    robo_2024: int
    extorsion_2024: int
    estafa_2024: int


class DistritoDelitoOut(DistritoDelitoBase):
    id: int
    total_2024: int

    class Config:
        from_attributes = True


class IndicadorOut(BaseModel):
    nombre: str
    valor: int | float | str
    descripcion: str


class RankingItem(BaseModel):
    distrito: str
    valor: int
    latitud: float
    longitud: float


class ResumenOut(BaseModel):
    total_delitos: int
    total_distritos: int
    delito_mayor_presion: str
    distrito_mayor_presion: str


class PrincipioAplicadoOut(BaseModel):
    nombre: str
    aplicacion: str
    evidencia: str
