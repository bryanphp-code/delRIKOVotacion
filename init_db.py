from backend.database import engine, Base
# Importar todos los modelos para que Base los registre
from backend.models.models import Admin, Client, ContestSetting, Participant, Vote

print("Creando tablas en la base de datos PostgreSQL (Neon)...")

# Crea todas las tablas definidas en los modelos
Base.metadata.create_all(bind=engine)

print("¡Tablas creadas exitosamente en Neon! 🚀")