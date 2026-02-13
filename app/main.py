from fastapi import FastAPI
from app.routers import estudiantes

app = FastAPI(
    title="Sistema Académico API",
    description="API para gestión de estudiantes",
    version="1.0.0"
)

app.include_router(estudiantes.router)

@app.get("/")
def read_root():
    return {
        "mensaje": "Bienvenido al Sistema Académico",
        "version": "1.0.0",
        "docs": "/docs"
    }

@app.get("/health")
def health_check():
    return {"status": "ok"}