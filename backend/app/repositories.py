from sqlalchemy.orm import Session

from .models import AuditLog, DistritoDelito, RegistroPendiente, Usuario


class UsuarioRepository:
    def __init__(self, db: Session):
        self.db = db

    def obtener_por_email(self, email: str) -> Usuario | None:
        return self.db.query(Usuario).filter(Usuario.email == email).first()

    def obtener_por_id(self, usuario_id: int) -> Usuario | None:
        return self.db.query(Usuario).filter(Usuario.id == usuario_id).first()

    def listar_activos(self) -> list[Usuario]:
        return self.db.query(Usuario).filter(Usuario.activo.is_(True)).order_by(Usuario.nombre).all()

    def guardar(self, usuario: Usuario) -> Usuario:
        self.db.add(usuario)
        self.db.commit()
        self.db.refresh(usuario)
        return usuario


class RegistroPendienteRepository:
    def __init__(self, db: Session):
        self.db = db

    def obtener_por_email(self, email: str) -> RegistroPendiente | None:
        return (
            self.db.query(RegistroPendiente)
            .filter(RegistroPendiente.email == email)
            .first()
        )

    def guardar(self, registro: RegistroPendiente) -> RegistroPendiente:
        self.db.add(registro)
        self.db.commit()
        self.db.refresh(registro)
        return registro


class DistritoRepository:
    def __init__(self, db: Session):
        self.db = db

    def listar(self) -> list[DistritoDelito]:
        return self.db.query(DistritoDelito).order_by(DistritoDelito.distrito).all()


class AuditRepository:
    def __init__(self, db: Session):
        self.db = db

    def registrar(
        self,
        accion: str,
        resultado: str,
        usuario_id: int | None = None,
        ip: str | None = None,
        detalle: str | None = None,
    ) -> None:
        self.db.add(
            AuditLog(
                usuario_id=usuario_id,
                accion=accion,
                resultado=resultado,
                ip=ip,
                detalle=detalle,
            )
        )
        self.db.commit()
