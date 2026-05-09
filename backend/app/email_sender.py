import logging
import os
import smtplib
from email.message import EmailMessage

from .config import cargar_env, env_bool

logger = logging.getLogger(__name__)

cargar_env()


def smtp_configurado() -> bool:
    return bool(
        os.getenv("GUARDIAN_SMTP_HOST")
        and os.getenv("GUARDIAN_SMTP_USER")
        and os.getenv("GUARDIAN_SMTP_PASSWORD")
    )


def mostrar_codigos_dev() -> bool:
    return env_bool(os.getenv("GUARDIAN_DEV_EMAIL_CODES"), default=False)


def enviar_codigo_verificacion(email: str, codigo: str) -> bool:
    if not smtp_configurado():
        if mostrar_codigos_dev():
            logger.warning("SMTP no configurado. Codigo de verificacion para %s: %s", email, codigo)
        else:
            logger.warning("SMTP no configurado. No se envio codigo para %s", email)
        return False

    host = os.environ["GUARDIAN_SMTP_HOST"]
    port = int(os.getenv("GUARDIAN_SMTP_PORT", "587"))
    user = os.environ["GUARDIAN_SMTP_USER"]
    password = os.environ["GUARDIAN_SMTP_PASSWORD"]
    sender = os.getenv("GUARDIAN_EMAIL_FROM", user)

    message = EmailMessage()
    message["Subject"] = "Codigo de verificacion - Guardian Ciudadano Peru"
    message["From"] = sender
    message["To"] = email
    message.set_content(
        "\n".join(
            [
                "Hola,",
                "",
                "Tu codigo de verificacion para Guardian Ciudadano Peru es:",
                "",
                codigo,
                "",
                "Este codigo vence en 10 minutos.",
                "Si no solicitaste este registro, ignora este mensaje.",
            ]
        )
    )

    if port == 465:
        with smtplib.SMTP_SSL(host, port, timeout=20) as smtp:
            smtp.login(user, password)
            smtp.send_message(message)
    else:
        with smtplib.SMTP(host, port, timeout=20) as smtp:
            smtp.starttls()
            smtp.login(user, password)
            smtp.send_message(message)

    return True
