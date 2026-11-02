from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from backend.routes import clients, participants, votes, admin

app = FastAPI(
    title="API Votación Disfraces SPA",
    version="1.0.0",
    description="Backend oficial para el concurso de disfraces del SPA (MVP)"
)

# Configuración de CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir routers de la API (¡Deben ir antes del StaticFiles!)
app.include_router(clients.router)
app.include_router(participants.router)
app.include_router(votes.router)
app.include_router(admin.router)

@app.get("/api/health")
def read_root():
    return {
        "message": "¡API del Concurso de Disfraces del SPA funcionando al 100%! 🎃✨",
        "status": "online"
    }

# Montar los archivos estáticos del frontend en la raíz
app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")