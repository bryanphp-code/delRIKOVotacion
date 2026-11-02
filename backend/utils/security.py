import os
import time
from datetime import datetime, timedelta, timezone

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from passlib.context import CryptContext

ALGORITHM = "HS256"
TOKEN_EXPIRE_MINUTES = 60
bearer_scheme = HTTPBearer(auto_error=False)


def _secret_key() -> str:
    key = os.getenv("SECRET_KEY")
    if not key or len(key) < 16:
        raise RuntimeError("SECRET_KEY no configurada o demasiado corta (mínimo 16 caracteres) en .env")
    return key


def create_access_token(username: str) -> str:
    payload = {
        "sub": username,
        "exp": datetime.now(timezone.utc) + timedelta(minutes=TOKEN_EXPIRE_MINUTES),
    }
    return jwt.encode(payload, _secret_key(), algorithm=ALGORITHM)


def get_current_admin(credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme)) -> str:
    """Dependencia que exige un token JWT de administrador válido."""
    error = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token inválido o expirado.",
        headers={"WWW-Authenticate": "Bearer"},
    )
    if credentials is None:
        raise error
    try:
        payload = jwt.decode(credentials.credentials, _secret_key(), algorithms=[ALGORITHM])
    except jwt.PyJWTError:
        raise error
    username = payload.get("sub")
    if not username:
        raise error
    return username


# Límite de intentos fallidos de login por IP (en memoria)
MAX_FAILED_ATTEMPTS = 5
LOCK_SECONDS = 300
_failed_attempts: dict[str, list[float]] = {}


def check_login_allowed(ip: str) -> None:
    now = time.time()
    attempts = [t for t in _failed_attempts.get(ip, []) if now - t < LOCK_SECONDS]
    _failed_attempts[ip] = attempts
    if len(attempts) >= MAX_FAILED_ATTEMPTS:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Demasiados intentos fallidos. Inténtalo de nuevo en unos minutos.",
        )


def register_failed_login(ip: str) -> None:
    _failed_attempts.setdefault(ip, []).append(time.time())


def clear_failed_logins(ip: str) -> None:
    _failed_attempts.pop(ip, None)


# Configuración del contexto para bcrypt
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    """
    Genera el hash seguro de una contraseña.
    Se asegura de recortar a 72 bytes/caracteres por la limitación de bcrypt.
    """
    if len(password.encode('utf-8')) > 72:
        password = password[:72]
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifica si una contraseña en texto plano coincide con su hash.
    También aplica el recorte por la misma limitación de bcrypt.
    """
    if len(plain_password.encode('utf-8')) > 72:
        plain_password = plain_password[:72]
    return pwd_context.verify(plain_password, hashed_password)