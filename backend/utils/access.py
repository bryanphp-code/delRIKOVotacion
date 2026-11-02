import secrets

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from backend.models.models import ContestSetting
from backend.utils.security import check_login_allowed, register_failed_login

# Más permisivo que el login: en el spa todos los clientes comparten la misma IP
MAX_CODE_ATTEMPTS = 20
CODE_ALPHABET = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"  # sin caracteres ambiguos (0/O, 1/I)
CODE_LENGTH = 6


def generate_access_code() -> str:
    return "".join(secrets.choice(CODE_ALPHABET) for _ in range(CODE_LENGTH))


def verify_access_code(db: Session, provided: str | None, ip: str) -> None:
    """Exige el código diario si el administrador configuró uno."""
    setting = db.query(ContestSetting).first()
    if not setting or not setting.access_code:
        return

    key = f"code:{ip}"
    check_login_allowed(key, MAX_CODE_ATTEMPTS)

    candidate = (provided or "").strip().upper()
    if not secrets.compare_digest(candidate.encode(), setting.access_code.encode()):
        register_failed_login(key)
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Código del día incorrecto. Pídelo al personal del spa.",
        )
