import base64
import hashlib
import hmac
import json
import os
import secrets
import time
from typing import Any

from fastapi import HTTPException, status

from .config import cargar_env

cargar_env()


PASSWORD_ITERATIONS = 260_000
TOKEN_TTL_SECONDS = int(os.getenv("GUARDIAN_TOKEN_TTL_SECONDS", "3600"))
TOKEN_SIGNING_KEY = os.getenv("GUARDIAN_TOKEN_KEY") or secrets.token_urlsafe(32)


def _b64_encode(raw: bytes) -> str:
    return base64.urlsafe_b64encode(raw).decode("utf-8").rstrip("=")


def _b64_decode(value: str) -> bytes:
    padding = "=" * (-len(value) % 4)
    return base64.urlsafe_b64decode(value + padding)


def normalizar_email(email: str) -> str:
    return email.strip().lower()


def hash_password(password: str, salt: str | None = None) -> tuple[str, str]:
    salt_bytes = _b64_decode(salt) if salt else secrets.token_bytes(16)
    digest = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt_bytes,
        PASSWORD_ITERATIONS,
    )
    return _b64_encode(salt_bytes), _b64_encode(digest)


def verificar_password(password: str, salt: str, expected_hash: str) -> bool:
    _, actual_hash = hash_password(password, salt)
    return hmac.compare_digest(actual_hash, expected_hash)


def validar_fortaleza_password(password: str) -> None:
    reglas = [
        len(password) >= 8,
        any(char.islower() for char in password),
        any(char.isupper() for char in password),
        any(char.isdigit() for char in password),
        any(not char.isalnum() for char in password),
    ]
    if not all(reglas):
        raise ValueError(
            "La contrasena debe tener 8 caracteres, mayuscula, minuscula, numero y simbolo."
        )


def crear_token_acceso(usuario_id: int, email: str, rol: str) -> dict[str, Any]:
    ahora = int(time.time())
    payload = {
        "sub": str(usuario_id),
        "email": email,
        "rol": rol,
        "iat": ahora,
        "exp": ahora + TOKEN_TTL_SECONDS,
        "nonce": secrets.token_urlsafe(12),
    }
    payload_bytes = json.dumps(payload, separators=(",", ":")).encode("utf-8")
    payload_b64 = _b64_encode(payload_bytes)
    signature = hmac.new(
        TOKEN_SIGNING_KEY.encode("utf-8"),
        payload_b64.encode("utf-8"),
        hashlib.sha256,
    ).digest()
    return {
        "access_token": f"{payload_b64}.{_b64_encode(signature)}",
        "expires_at": payload["exp"],
    }


def decodificar_token(token: str) -> dict[str, Any]:
    try:
        payload_b64, signature_b64 = token.split(".", 1)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token invalido.",
        ) from exc

    expected_signature = hmac.new(
        TOKEN_SIGNING_KEY.encode("utf-8"),
        payload_b64.encode("utf-8"),
        hashlib.sha256,
    ).digest()

    if not hmac.compare_digest(_b64_encode(expected_signature), signature_b64):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token invalido.",
        )

    payload = json.loads(_b64_decode(payload_b64))
    if int(payload.get("exp", 0)) < int(time.time()):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expirado.",
        )
    return payload
