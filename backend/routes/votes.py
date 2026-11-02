from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy import func, desc
from sqlalchemy.orm import Session
from typing import List

from backend.database import get_db
from backend.models.models import Vote, Client, Participant, ContestSetting
from backend.schemas.schemas import VoteCreate, VoteResponse
from backend.utils.access import verify_access_code

router = APIRouter(prefix="/api/votes", tags=["Votes"])


@router.post("/", response_model=VoteResponse, status_code=status.HTTP_201_CREATED)
def cast_vote(vote_data: VoteCreate, request: Request, db: Session = Depends(get_db)):
    """
    Registra el voto de un cliente por un participante.
    Verifica que el concurso esté abierto, que el cliente y participante existan,
    y que el cliente no haya votado previamente.
    """
    # 1. Verificar si el concurso está abierto
    setting = db.query(ContestSetting).first()
    # Si existe una configuración y is_open es False, bloqueamos
    if setting and not setting.is_open:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Las votaciones están cerradas temporalmente."
        )

    # 1b. Verificar el código secreto diario
    verify_access_code(db, vote_data.access_code, request.client.host if request.client else "unknown")

    # 2. Verificar que el cliente exista
    client = db.query(Client).filter(Client.id == vote_data.client_id).first()
    if not client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cliente no encontrado."
        )

    # 3. Verificar que el participante exista y esté activo
    participant = db.query(Participant).filter(Participant.id == vote_data.participant_id, Participant.active == True).first()
    if not participant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Participante no encontrado o inactivo."
        )

    # 4. Verificar si el cliente ya votó previamente (doble seguridad a nivel de app)
    existing_vote = db.query(Vote).filter(Vote.client_id == vote_data.client_id).first()
    if existing_vote:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Este cliente ya ha emitido su voto en el concurso."
        )

    # 4b. Segunda validación: ningún cliente con el mismo documento puede haber votado
    if client.document_number:
        doc_vote = db.query(Vote.id).join(Client, Client.id == Vote.client_id)\
            .filter(Client.document_number == client.document_number).first()
        if doc_vote:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Este cliente ya ha emitido su voto en el concurso."
            )

    # 5. Registrar el voto
    new_vote = Vote(
        client_id=vote_data.client_id,
        participant_id=vote_data.participant_id
    )

    try:
        db.add(new_vote)
        db.commit()
        db.refresh(new_vote)
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Error al registrar el voto. Es posible que ya exista un voto asociado a este cliente."
        )

    return new_vote


@router.get("/results", summary="Obtener resultados del concurso")
def get_vote_results(db: Session = Depends(get_db)):
    """
    Devuelve un conteo de votos agrupados por participante (ideal para la pantalla de resultados o admin).
    """
    results = db.query(
        Participant.id,
        Participant.full_name,
        Participant.photo_url,
        func.count(Vote.id).label("total_votes")
    ).outerjoin(Vote, Participant.id == Vote.participant_id)\
     .filter(Participant.active == True)\
     .group_by(Participant.id, Participant.full_name, Participant.photo_url)\
     .order_by(desc("total_votes"))\
     .all()

    return [
        {
            "participant_id": r.id,
            "full_name": r.full_name,
            "photo_url": r.photo_url,
            "total_votes": r.total_votes
        }
        for r in results
    ]