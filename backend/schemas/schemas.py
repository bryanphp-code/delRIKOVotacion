import re
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, field_validator


# --- CLIENTES ---
class ClientBase(BaseModel):
    full_name: str
    document_number: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None


class ClientCreate(ClientBase):
    document_number: str
    access_code: Optional[str] = None

    @field_validator("document_number", mode="before")
    @classmethod
    def validate_document_number(cls, v):
        if not isinstance(v, str):
            raise ValueError("El documento debe ser texto numérico.")
        v = re.sub(r"[\s-]", "", v)
        if not re.fullmatch(r"\d{8,20}", v):
            raise ValueError("El documento (DNI o Carnet de Extranjería) debe tener al menos 8 dígitos numéricos.")
        return v


class ClientResponse(ClientBase):
    id: int
    active: bool
    created_at: datetime

    class Config:
        from_attributes = True


# --- PARTICIPANTES ---
class ParticipantBase(BaseModel):
    full_name: str
    description: Optional[str] = None
    photo_url: Optional[str] = None


class ParticipantCreate(ParticipantBase):
    pass


class ParticipantUpdate(BaseModel):
    full_name: Optional[str] = None
    description: Optional[str] = None
    photo_url: Optional[str] = None
    active: Optional[bool] = None


class ParticipantResponse(ParticipantBase):
    id: int
    active: bool
    created_at: datetime

    class Config:
        from_attributes = True


# --- VOTOS ---
class VoteCreate(BaseModel):
    client_id: int
    participant_id: int
    access_code: Optional[str] = None


class VoteResponse(BaseModel):
    id: int
    client_id: int
    participant_id: int
    created_at: datetime

    class Config:
        from_attributes = True


# --- CONFIGURACIÓN DEL CONCURSO ---
class ContestSettingUpdate(BaseModel):
    contest_name: Optional[str] = None
    is_open: Optional[bool] = None


class ContestSettingResponse(BaseModel):
    id: int
    contest_name: str
    is_open: bool
    requires_code: bool = False
    updated_at: datetime

    class Config:
        from_attributes = True


class AccessCodeUpdate(BaseModel):
    access_code: Optional[str] = None

    @field_validator("access_code", mode="before")
    @classmethod
    def validate_access_code(cls, v):
        if v is None or (isinstance(v, str) and not v.strip()):
            return None
        v = str(v).strip().upper()
        if not re.fullmatch(r"[A-Z0-9]{4,20}", v):
            raise ValueError("El código debe tener entre 4 y 20 letras o números, sin espacios.")
        return v


class AccessCodeResponse(BaseModel):
    access_code: Optional[str] = None


# --- ADMINISTRADORES Y AUTH ---
class AdminLogin(BaseModel):
    username: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str