import os
from pathlib import Path
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.orm import DeclarativeBase, sessionmaker

# Buscar la ruta raíz del proyecto (delRIKO)
BASE_DIR = Path(__file__).resolve().parent.parent
env_path = BASE_DIR / ".env"

print(f"🔍 Buscando el archivo .env en: {env_path}")
if env_path.exists():
    print("✅ ¡Archivo .env encontrado!")
    load_dotenv(dotenv_path=env_path)
else:
    print("❌ ADVERTENCIA: No se encontró el archivo .env en esa ruta.")

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError(f"❌ La variable DATABASE_URL sigue sin encontrarse. Revisa que el archivo .env contenga 'DATABASE_URL=...'")

# Configuración del motor para PostgreSQL (Neon requiere SSL)
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    pool_recycle=300,
)

# Validación de la conexión a la base de datos
try:
    with engine.connect() as connection:
        connection.execute(text("SELECT 1"))
    print("¡Conexión exitosa a la base de datos PostgreSQL en Neon! 🚀")
except Exception as e:
    print(f"❌ Error al conectar con la base de datos: {e}")

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()