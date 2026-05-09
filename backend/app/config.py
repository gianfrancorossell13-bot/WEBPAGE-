from pathlib import Path

try:
    from dotenv import load_dotenv
except ImportError:
    load_dotenv = None


BACKEND_DIR = Path(__file__).resolve().parents[1]
ENV_PATH = BACKEND_DIR / ".env"


def cargar_env() -> None:
    if load_dotenv is not None:
        load_dotenv(dotenv_path=ENV_PATH)


def env_bool(value: str | None, default: bool = False) -> bool:
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "si", "on"}
