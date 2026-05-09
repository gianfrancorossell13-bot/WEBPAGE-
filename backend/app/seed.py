import os

from sqlalchemy.orm import Session

from .models import DistritoDelito, Usuario
from .security import hash_password, normalizar_email, validar_fortaleza_password


DATA_INICIAL = [
    {
        "distrito": "San Juan de Lurigancho",
        "latitud": -11.9823,
        "longitud": -77.0049,
        "homicidio_2024": 155,
        "hurto_2024": 7787,
        "robo_2024": 4877,
        "extorsion_2024": 1305,
        "estafa_2024": 1192,
    },
    {
        "distrito": "Callao",
        "latitud": -12.0566,
        "longitud": -77.1181,
        "homicidio_2024": 157,
        "hurto_2024": 3770,
        "robo_2024": 3008,
        "extorsion_2024": 889,
        "estafa_2024": 356,
    },
    {
        "distrito": "San Martin de Porres",
        "latitud": -12.0308,
        "longitud": -77.0805,
        "homicidio_2024": 71,
        "hurto_2024": 4322,
        "robo_2024": 4395,
        "extorsion_2024": 778,
        "estafa_2024": 329,
    },
    {
        "distrito": "Ate",
        "latitud": -12.0266,
        "longitud": -76.9198,
        "homicidio_2024": 68,
        "hurto_2024": 4513,
        "robo_2024": 2927,
        "extorsion_2024": 556,
        "estafa_2024": 396,
    },
    {
        "distrito": "Comas",
        "latitud": -11.9320,
        "longitud": -77.0409,
        "homicidio_2024": 93,
        "hurto_2024": 3371,
        "robo_2024": 3056,
        "extorsion_2024": 663,
        "estafa_2024": 607,
    },
    {
        "distrito": "Los Olivos",
        "latitud": -11.9763,
        "longitud": -77.0750,
        "homicidio_2024": 33,
        "hurto_2024": 3609,
        "robo_2024": 3259,
        "extorsion_2024": 696,
        "estafa_2024": 321,
    },
    {
        "distrito": "La Victoria",
        "latitud": -12.0733,
        "longitud": -77.0169,
        "homicidio_2024": 25,
        "hurto_2024": 4192,
        "robo_2024": 2344,
        "extorsion_2024": 378,
        "estafa_2024": 194,
    },
    {
        "distrito": "Independencia",
        "latitud": -11.9900,
        "longitud": -77.0450,
        "homicidio_2024": 14,
        "hurto_2024": 2961,
        "robo_2024": 1857,
        "extorsion_2024": 472,
        "estafa_2024": 208,
    },
    {
        "distrito": "Villa El Salvador",
        "latitud": -12.2150,
        "longitud": -76.9437,
        "homicidio_2024": 53,
        "hurto_2024": 2233,
        "robo_2024": 2306,
        "extorsion_2024": 488,
        "estafa_2024": 374,
    },
    {
        "distrito": "Puente Piedra",
        "latitud": -11.8667,
        "longitud": -77.0833,
        "homicidio_2024": 59,
        "hurto_2024": 1924,
        "robo_2024": 1461,
        "extorsion_2024": 462,
        "estafa_2024": 269,
    },
]


def cargar_datos_iniciales(db: Session):
    total = db.query(DistritoDelito).count()

    if total == 0:
        for item in DATA_INICIAL:
            db.add(DistritoDelito(**item))

        db.commit()


def cargar_usuario_academico(db: Session):
    email = normalizar_email(os.getenv("GUARDIAN_ADMIN_EMAIL", "analista@guardian.pe"))
    password = os.getenv("GUARDIAN_ADMIN_PASSWORD", "Guardian2026!")

    if db.query(Usuario).filter(Usuario.email == email).first():
        return

    validar_fortaleza_password(password)
    salt, password_hash = hash_password(password)
    db.add(
        Usuario(
            nombre="Analista Guardian",
            email=email,
            password_salt=salt,
            password_hash=password_hash,
            rol="admin",
            activo=True,
        )
    )

    db.commit()
