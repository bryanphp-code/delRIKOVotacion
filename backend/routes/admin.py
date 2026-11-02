from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session
from typing import List

from backend.database import get_db
from backend.models.models import ContestSetting, Admin, Vote, Client, Participant
from backend.schemas.schemas import (
    ContestSettingUpdate,
    ContestSettingResponse,
    AccessCodeUpdate,
    AccessCodeResponse,
    AdminLogin,
    Token,
)
from backend.utils.access import generate_access_code
from backend.utils.security import (
    verify_password,
    create_access_token,
    get_current_admin,
    check_login_allowed,
    register_failed_login,
    clear_failed_logins,
)

router = APIRouter(prefix="/api/admin", tags=["Admin & Settings"])


def _get_or_create_setting(db: Session) -> ContestSetting:
    setting = db.query(ContestSetting).first()
    if not setting:
        setting = ContestSetting(contest_name="Concurso de Disfraces SPA", is_open=False)
        db.add(setting)
        db.commit()
        db.refresh(setting)
    return setting


@router.get("/settings", response_model=ContestSettingResponse)
def get_contest_settings(db: Session = Depends(get_db)):
    """Obtiene el estado actual del concurso."""
    setting = db.query(ContestSetting).first()
    if not setting:
        setting = ContestSetting(contest_name="Concurso de Disfraces SPA", is_open=False)
        db.add(setting)
        db.commit()
        db.refresh(setting)
    return setting


@router.put("/settings", response_model=ContestSettingResponse)
def update_contest_settings(
    setting_data: ContestSettingUpdate,
    db: Session = Depends(get_db),
    _admin: str = Depends(get_current_admin),
):
    """Permite al administrador abrir/cerrar el concurso o cambiar el nombre."""
    setting = db.query(ContestSetting).first()
    if not setting:
        setting = ContestSetting(contest_name="Concurso de Disfraces SPA", is_open=False)
        db.add(setting)
        db.commit()

    update_data = setting_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(setting, key, value)

    db.commit()
    db.refresh(setting)
    return setting


@router.get("/access-code", response_model=AccessCodeResponse, summary="Ver el código secreto del día (solo admin)")
def get_access_code(db: Session = Depends(get_db), _admin: str = Depends(get_current_admin)):
    setting = db.query(ContestSetting).first()
    return {"access_code": setting.access_code if setting else None}


@router.put("/access-code", response_model=AccessCodeResponse, summary="Definir o quitar el código del día (solo admin)")
def set_access_code(
    data: AccessCodeUpdate,
    db: Session = Depends(get_db),
    _admin: str = Depends(get_current_admin),
):
    setting = _get_or_create_setting(db)
    setting.access_code = data.access_code
    db.commit()
    return {"access_code": setting.access_code}


@router.post("/access-code/generate", response_model=AccessCodeResponse, summary="Generar un código aleatorio nuevo (solo admin)")
def generate_new_access_code(db: Session = Depends(get_db), _admin: str = Depends(get_current_admin)):
    setting = _get_or_create_setting(db)
    setting.access_code = generate_access_code()
    db.commit()
    return {"access_code": setting.access_code}


@router.get("/votes", summary="Listar quién votó y por quién (solo admin)")
def list_votes(db: Session = Depends(get_db), _admin: str = Depends(get_current_admin)):
    rows = (
        db.query(
            Vote.id,
            Vote.created_at,
            Client.full_name.label("client_name"),
            Client.document_number,
            Client.email,
            Participant.full_name.label("participant_name"),
        )
        .join(Client, Client.id == Vote.client_id)
        .join(Participant, Participant.id == Vote.participant_id)
        .order_by(Vote.created_at.desc())
        .all()
    )
    return [
        {
            "id": r.id,
            "created_at": r.created_at,
            "client_name": r.client_name,
            "document_number": r.document_number,
            "email": r.email,
            "participant_name": r.participant_name,
        }
        for r in rows
    ]


@router.post("/login", response_model=Token)
def admin_login(login_data: AdminLogin, request: Request, db: Session = Depends(get_db)):
    """Inicio de sesión seguro para el administrador usando bcrypt."""
    ip = request.client.host if request.client else "unknown"
    check_login_allowed(ip)

    admin = db.query(Admin).filter(Admin.username == login_data.username, Admin.active == True).first()
    
    # Validar usuario y comprobar el hash de la contraseña
    if not admin or not verify_password(login_data.password, admin.password_hash):
        register_failed_login(ip)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales de administrador incorrectas."
        )

    clear_failed_logins(ip)
    return {
        "access_token": create_access_token(admin.username),
        "token_type": "bearer"
    }