import getpass
import sys

from backend.database import SessionLocal
from backend.models.models import Admin
from backend.utils.security import hash_password

MIN_PASSWORD_LENGTH = 12

admin_username = input("Usuario admin [admin_spa]: ").strip() or "admin_spa"
admin_plain_password = getpass.getpass("Contraseña: ")

if len(admin_plain_password) < MIN_PASSWORD_LENGTH:
    sys.exit(f"❌ La contraseña debe tener al menos {MIN_PASSWORD_LENGTH} caracteres.")
if admin_plain_password != getpass.getpass("Repite la contraseña: "):
    sys.exit("❌ Las contraseñas no coinciden.")

db = SessionLocal()

existing_admin = db.query(Admin).filter(Admin.username == admin_username).first()
hashed_pwd = hash_password(admin_plain_password)

if not existing_admin:
    db.add(Admin(username=admin_username, password_hash=hashed_pwd, active=True))
    db.commit()
    print(f"Administrador '{admin_username}' creado con éxito.")
else:
    existing_admin.password_hash = hashed_pwd
    existing_admin.active = True
    db.commit()
    print(f"Administrador '{admin_username}' ya existía. Contraseña actualizada.")

db.close()