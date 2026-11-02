from datetime import datetime
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Text, UniqueConstraint, func
from sqlalchemy.orm import relationship
from backend.database import Base



class Client(Base):
    __tablename__ = "clients"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String(150), nullable=False)
    document_number = Column(String(20), unique=True, nullable=True, index=True)
    phone = Column(String(30), nullable=True)
    email = Column(String(100), nullable=True)
    active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relación con votos
    votes = relationship("Vote", back_populates="client", cascade="all, delete-orphan")


class Participant(Base):
    __tablename__ = "participants"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String(150), nullable=False)
    description = Column(Text, nullable=True)
    photo_url = Column(String(500), nullable=True)
    active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relación con votos
    votes = relationship("Vote", back_populates="participant", cascade="all, delete-orphan")


class Vote(Base):
    __tablename__ = "votes"

    id = Column(Integer, primary_key=True, index=True)
    client_id = Column(Integer, ForeignKey("clients.id"), nullable=False, unique=True) # Restricción de 1 solo voto por cliente en el MVP
    participant_id = Column(Integer, ForeignKey("participants.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relaciones
    client = relationship("Client", back_populates="votes")
    participant = relationship("Participant", back_populates="votes")


class ContestSetting(Base):
    __tablename__ = "contest_settings"

    id = Column(Integer, primary_key=True, index=True)
    contest_name = Column(String(150), default="Concurso de Disfraces SPA", nullable=False)
    is_open = Column(Boolean, default=False, nullable=False)  # Controla si las votaciones están abiertas
    access_code = Column(String(20), nullable=True)  # Código secreto diario; si es NULL no se exige
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    @property
    def requires_code(self) -> bool:
        return bool(self.access_code)


class Admin(Base):
    __tablename__ = "admins"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)  # Nunca en texto plano
    active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)


