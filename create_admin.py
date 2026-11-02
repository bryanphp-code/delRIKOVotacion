from backend.database import SessionLocal
from backend.models.models import Admin
from backend.utils.security import hash_password

db = SessionLocal()

# Credenciales del administrador inicial
admin_username = "admin_spa"
admin_plain_password = "admin123"

# Verificar si ya existe el admin
existing_admin = db.query(Admin).filter(Admin.username == admin_username).first()

hashed_pwd = hash_password(admin_plain_password)

if not existing_admin:
    new_admin = Admin(
        username=admin_username,
        password_hash=hashed_pwd,
        active=True
    )
    db.add(new_admin)
    db.commit()
    print(f"✅ Administrador creado con éxito: usuario '{admin_username}', contraseña hasheada correctamente.")
else:
    # Actualizar la contraseña si ya existía para asegurar que tenga el hash correcto
    existing_admin.password_hash = hashed_pwd
    db.commit()
    print(f"🔄 Administrador '{admin_username}' ya existía. Contraseña actualizada con su respectivo hash bcrypt.")

db.close()