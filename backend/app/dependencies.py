from collections.abc import Callable

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from .database import get_db
from .repositories import UsuarioRepository
from .schemas import UsuarioOut
from .security import decodificar_token
from .services import convertir_usuario


bearer_scheme = HTTPBearer(auto_error=False)


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> UsuarioOut:
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Autenticacion requerida.",
        )

    payload = decodificar_token(credentials.credentials)
    usuario = UsuarioRepository(db).obtener_por_id(int(payload["sub"]))

    if not usuario or not usuario.activo:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario inactivo o inexistente.",
        )

    return convertir_usuario(usuario)


def require_roles(*roles: str) -> Callable:
    def dependency(usuario: UsuarioOut = Depends(get_current_user)) -> UsuarioOut:
        if usuario.rol not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tienes permisos para esta operacion.",
            )
        return usuario

    return dependency
