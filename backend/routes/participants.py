from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from backend.database import get_db
from backend.models.models import Participant
from backend.schemas.schemas import ParticipantCreate, ParticipantResponse, ParticipantUpdate
from backend.utils.security import get_current_admin

router = APIRouter(prefix="/api/participants", tags=["Participants"])


@router.get("/", response_model=List[ParticipantResponse])
def list_participants(db: Session = Depends(get_db)):
    """Lista todos los participantes activos para que los clientes puedan votar."""
    participants = db.query(Participant).filter(Participant.active == True).all()
    return participants


@router.post("/", response_model=ParticipantResponse, status_code=status.HTTP_201_CREATED)
def create_participant(
    participant_data: ParticipantCreate,
    db: Session = Depends(get_db),
    _admin: str = Depends(get_current_admin),
):
    """Registra un nuevo participante en el concurso (Uso del Administrador)."""
    new_participant = Participant(
        full_name=participant_data.full_name,
        description=participant_data.description,
        photo_url=participant_data.photo_url,
        active=True
    )
    db.add(new_participant)
    db.commit()
    db.refresh(new_participant)
    return new_participant


@router.put("/{participant_id}", response_model=ParticipantResponse)
def update_participant(
    participant_id: int,
    participant_data: ParticipantUpdate,
    db: Session = Depends(get_db),
    _admin: str = Depends(get_current_admin),
):
    """Actualiza los datos o estado de un participante."""
    participant = db.query(Participant).filter(Participant.id == participant_id).first()
    if not participant:
        raise HTTPException(status_code=404, detail="Participante no encontrado")

    update_data = participant_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(participant, key, value)

    db.commit()
    db.refresh(participant)
    return participant