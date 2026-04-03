from urllib import request
from urllib.parse import quote

from fastapi import FastAPI, Request, Form, Depends  # NUEVO: agrega Depends
from fastapi.exceptions import HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from typing import Optional
from sqlalchemy.orm import Session  # NUEVO

# ─────────────────────────────────────────
# NUEVO: importar BD y crear tablas al arrancar
# ANTES: estas 3 líneas no existían
# ─────────────────────────────────────────
from app.database import engine, Base, get_db
from app.models import (
    Estudiante,
    Profesor,
)  # necesario para que Base registre las tablas

Base.metadata.create_all(bind=engine)  # crea las tablas si no existen (idempotente)

from app.routers import estudiantes, profesores
from app.schemas.estudiante import EstudianteCreate
from app.schemas.profesor import ProfesorCreate
import app.services.estudiante_service as est_svc
import app.services.profesor_service as prof_svc

from fastapi.staticfiles import StaticFiles

# ─────────────────────────────────────────
# Aplicación principal
# ─────────────────────────────────────────
app = FastAPI(
    title="Sistema Académico API",
    description="API para gestión de estudiantes y profesores",
    version="1.0.0",
)

app.mount(
    "/static", StaticFiles(directory="app/static"), name="static"
)  # ← agregar esta línea
templates = Jinja2Templates(directory="app/templates")
app.include_router(estudiantes.router)
app.include_router(profesores.router)


# ─────────────────────────────────────────
# pantalla de bienvenida en la raíz "/" con un mensaje simple y un enlace a la UI de estudiantes y profesores
# ─────────────────────────────────────────
@app.get("/", response_class=HTMLResponse, tags=["Sistema"])
def bienvenida(request: Request):
    return templates.TemplateResponse("welcome.html", {"request": request})


# ─────────────────────────────────────────
# Helper: construir URL de redirección con mensaje o error correctamente encodeado
# ─────────────────────────────────────────
def _redirect(base: str, mensaje: str = None, error: str = None) -> RedirectResponse:
    if mensaje:
        return RedirectResponse(url=f"{base}?mensaje={quote(mensaje)}", status_code=303)
    if error:
        return RedirectResponse(url=f"{base}?error={quote(error)}", status_code=303)
    return RedirectResponse(url=base, status_code=303)


# ─────────────────────────────────────────
# Health check
# ─────────────────────────────────────────
@app.get("/health", tags=["Sistema"], response_model=dict)
def health_check():
    """Verifica que el servidor está en línea."""
    return {"status": "ok"}


# ══════════════════════════════════════════
# VISTAS HTML — ESTUDIANTES
# ══════════════════════════════════════════


@app.get("/ui", response_class=HTMLResponse, tags=["UI"])
def ui_inicio(
    request: Request,
    mensaje: Optional[str] = None,
    error: Optional[str] = None,
    db: Session = Depends(get_db),  # NUEVO
):
    """Vista principal: tabla de estudiantes + formulario de registro."""
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "estudiantes": est_svc.obtener_todos(db),  # ANTES: obtener_todos()
            "stats": est_svc.estadisticas(db),  # ANTES: estadisticas()
            "mensaje": mensaje,
            "error": error,
        },
    )


@app.post("/ui/nuevo", tags=["UI"])
def ui_crear_estudiante(
    nombre: str = Form(...),
    matricula: str = Form(...),
    email: str = Form(...),
    carrera: str = Form(...),
    semestre: int = Form(...),
    promedio: float = Form(...),
    telefono: Optional[str] = Form(None),
    db: Session = Depends(get_db),  # NUEVO
):
    """Procesa el formulario de registro de estudiante."""
    try:
        datos = EstudianteCreate(
            nombre=nombre,
            matricula=matricula,
            email=email,
            carrera=carrera,
            semestre=semestre,
            promedio=promedio,
            telefono=telefono or None,
        )
        nuevo = est_svc.crear(db, datos)  # ANTES: est_svc.crear(datos)
        return _redirect(
            "/ui", mensaje=f"Estudiante '{nuevo.nombre}' registrado correctamente"
        )
        #                                         ANTES: nuevo['nombre']  ↑
    except HTTPException as e:
        return _redirect("/ui", error=e.detail)
    except Exception as e:
        return _redirect("/ui", error=str(e))


@app.post("/ui/estudiantes/{estudiante_id}/estado", tags=["UI"])
def ui_cambiar_estado_estudiante(
    estudiante_id: int,
    activo: str = Form(...),
    db: Session = Depends(get_db),  # NUEVO
):
    """Activa o desactiva un estudiante desde la UI."""
    try:
        est_svc.cambiar_estado(db, estudiante_id, activo == "true")  # ANTES: sin db
        return _redirect("/ui", mensaje="Estado actualizado correctamente")
    except HTTPException as e:
        return _redirect("/ui", error=e.detail)
    except Exception as e:
        return _redirect("/ui", error=str(e))


@app.post("/ui/estudiantes/{estudiante_id}/eliminar", tags=["UI"])
def ui_eliminar_estudiante(
    estudiante_id: int,
    db: Session = Depends(get_db),  # NUEVO
):
    """Elimina un estudiante desde la UI."""
    try:
        resultado = est_svc.eliminar(db, estudiante_id)  # ANTES: sin db
        return _redirect("/ui", mensaje=resultado["mensaje"])
    except HTTPException as e:
        return _redirect("/ui", error=e.detail)
    except Exception as e:
        return _redirect("/ui", error=str(e))


# ══════════════════════════════════════════
# VISTAS HTML — PROFESORES
# ══════════════════════════════════════════


@app.get("/ui/profesores", response_class=HTMLResponse, tags=["UI"])
def ui_profesores(
    request: Request,
    mensaje: Optional[str] = None,
    error: Optional[str] = None,
    db: Session = Depends(get_db),  # NUEVO
):
    """Vista principal: tabla de profesores + formulario de registro."""
    return templates.TemplateResponse(
        "profesores.html",
        {
            "request": request,
            "profesores": prof_svc.obtener_todos(db),  # ANTES: obtener_todos()
            "mensaje": mensaje,
            "error": error,
        },
    )


@app.post("/ui/profesores/nuevo", tags=["UI"])
def ui_crear_profesor(
    nombre: str = Form(...),
    email: str = Form(...),
    departamento: str = Form(...),
    especialidad: str = Form(...),
    telefono: Optional[str] = Form(None),
    db: Session = Depends(get_db),  # NUEVO
):
    """Procesa el formulario de registro de profesor."""
    try:
        datos = ProfesorCreate(
            nombre=nombre,
            email=email,
            departamento=departamento,
            especialidad=especialidad,
            telefono=telefono or None,
        )
        nuevo = prof_svc.crear(db, datos)  # ANTES: prof_svc.crear(datos)
        return _redirect(
            "/ui/profesores",
            mensaje=f"Profesor '{nuevo.nombre}' registrado correctamente",
        )
        #                                                   ANTES: nuevo['nombre']  ↑
    except HTTPException as e:
        return _redirect("/ui/profesores", error=e.detail)
    except Exception as e:
        return _redirect("/ui/profesores", error=str(e))


@app.post("/ui/profesores/{profesor_id}/estado", tags=["UI"])
def ui_cambiar_estado_profesor(
    profesor_id: int,
    activo: str = Form(...),
    db: Session = Depends(get_db),  # NUEVO
):
    """Activa o desactiva un profesor desde la UI."""
    try:
        prof_svc.cambiar_estado(db, profesor_id, activo == "true")  # ANTES: sin db
        return _redirect("/ui/profesores", mensaje="Estado actualizado correctamente")
    except HTTPException as e:
        return _redirect("/ui/profesores", error=e.detail)
    except Exception as e:
        return _redirect("/ui/profesores", error=str(e))


@app.post("/ui/profesores/{profesor_id}/eliminar", tags=["UI"])
def ui_eliminar_profesor(
    profesor_id: int,
    db: Session = Depends(get_db),  # NUEVO
):
    """Elimina un profesor desde la UI."""
    try:
        resultado = prof_svc.eliminar(db, profesor_id)  # ANTES: sin db
        return _redirect("/ui/profesores", mensaje=resultado["mensaje"])
    except HTTPException as e:
        return _redirect("/ui/profesores", error=e.detail)
    except Exception as e:
        return _redirect("/ui/profesores", error=str(e))
