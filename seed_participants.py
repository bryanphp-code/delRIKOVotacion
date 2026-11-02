from backend.database import SessionLocal
from backend.models.models import Participant

db = SessionLocal()

# Verificar si ya existen participantes para evitar duplicar registros si lo ejecutas varias veces
existing_count = db.query(Participant).count()

if existing_count == 0:
    participants_data = [
        Participant(
            full_name="Carlos - Drácula Moderno",
            description="Traje formal de etiqueta con capa de terciopelo oscuro y detalles góticos.",
            photo_url="https://images.unsplash.com/photo-1509557965875-b88c97052f0e?auto=format&fit=crop&w=600&q=80",
            active=True
        ),
        Participant(
            full_name="Ana - Catrina Elegante",
            description="Maquillaje tradicional de calavera con un vestido de gala negro y flores artesanales.",
            photo_url="https://images.unsplash.com/photo-1518709268805-4e9042af9f23?auto=format&fit=crop&w=600&q=80",
            active=True
        ),
        Participant(
            full_name="Luis - Astronauta Espacial",
            description="Traje espacial realista con casco reflectante, parches de la NASA y luces LED.",
            photo_url="https://images.unsplash.com/photo-1614728894747-a83421e2b9c9?auto=format&fit=crop&w=600&q=80",
            active=True
        )
    ]

    db.add_all(participants_data)
    db.commit()
    print("✅ ¡3 participantes de prueba insertados exitosamente en la base de datos! 🎃✨")
else:
    print(f"ℹ️ La tabla de participantes ya cuenta con {existing_count} registros. No se insertaron duplicados.")

db.close()