import os
import sys
from logging.config import fileConfig

from alembic import context
from dotenv import load_dotenv
from sqlalchemy import create_engine, pool

# Cargar las variables de entorno desde .env
load_dotenv()

# Añadir la ruta raíz del proyecto para que Python encuentre el paquete 'backend'
sys.path.insert(0, os.path.realpath(os.path.join(os.path.dirname(__file__), '..')))

from backend.database import Base
# Importar los modelos para que Base los reconozca
from backend.models.models import Admin, Client, ContestSetting, Participant, Vote

config = context.config

# Configurar el archivo de logging si existe
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata

# Obtener la URL de la base de datos
database_url = os.getenv("DATABASE_URL")


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    context.configure(
        url=database_url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.connect() as connection:
        context.run_migrations(connection=connection)


def run_migrations_online() -> None:
    """Run migrations in 'online' mode using direct engine creation."""
    connectable = create_engine(database_url, poolclass=pool.NullPool)

    with connectable.connect() as connection:
        context.run_migrations(connection=connection)


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()