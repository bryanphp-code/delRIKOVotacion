"""Genera una SECRET_KEY aleatoria y la guarda en .env (sin mostrarla)."""
import secrets
from pathlib import Path

env_path = Path(__file__).resolve().parent / ".env"
lines = env_path.read_text(encoding="utf-8").splitlines() if env_path.exists() else []

new_line = f"SECRET_KEY={secrets.token_urlsafe(48)}"
for i, line in enumerate(lines):
    if line.startswith("SECRET_KEY="):
        lines[i] = new_line
        break
else:
    lines.append(new_line)

env_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
print("SECRET_KEY regenerada en .env. Reinicia el servidor.")
