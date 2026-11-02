from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from backend.database import get_db
from backend.models.models import Client, Vote
from backend.schemas.schemas import ClientCreate, ClientResponse
from backend.utils.security import get_current_admin

router = APIRouter(prefix="/api/clients", tags=["Clients"])


@router.post("/", response_model=ClientResponse, status_code=status.HTTP_201_CREATED)
def register_client(client_data: ClientCreate, db: Session = Depends(get_db)):
    """
    Registra un nuevo cliente para la votación. 
    Si ya existe un cliente con el mismo número de documento, lo devuelve en lugar de duplicarlo.
    """
    # Si se proporciona un número de documento, verificamos si ya está registrado
    if client_data.document_number:
        existing_client = db.query(Client).filter(Client.document_number == client_data.document_number).first()
        if existing_client:
            already_voted = db.query(Vote.id).filter(Vote.client_id == existing_client.id).first()
            if already_voted:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Este documento ya ha emitido su voto en el concurso."
                )
            return existing_client

    # Crear nuevo cliente
    new_client = Client(
        full_name=client_data.full_name,
        document_number=client_data.document_number,
        phone=client_data.phone,
        email=client_data.email,
        active=True
    )
    
    db.add(new_client)
    db.commit()
    db.refresh(new_client)
    return new_client


@router.get("/", response_model=List[ClientResponse])
def list_clients(db: Session = Depends(get_db), _admin: str = Depends(get_current_admin)):
    """Lista todos los clientes registrados (útil para el panel de administración)."""
    clients = db.query(Client).all()
    return clients


@router.get("/{client_id}", response_model=ClientResponse)
def get_client(client_id: int, db: Session = Depends(get_db), _admin: str = Depends(get_current_admin)):
    """Obtiene los datos de un cliente específico por su ID."""
    client = db.query(Client).filter(Client.id == client_id).first()
    if not client:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    return client