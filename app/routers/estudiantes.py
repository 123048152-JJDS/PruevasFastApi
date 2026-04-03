from fastapi import APIRouter, Query, status, Body, Depends
from sqlalchemy.orm import Session
from typing import Optional
from app.schemas.estudiante import (
    EstudianteCreate,
    EstudianteResponse,
    EstudianteUpdate,
)
from app.database import get_db  # NUEVO: importar get_db
import app.services.estudiante_service as svc

router = APIRouter(prefix="/estudiantes", tags=["Estudiantes"])


# ─────────────────────────────────────────
# GET /estudiantes/stats/resumen
# Va ANTES de /{estudiante_id} para evitar
# que FastAPI interprete "stats" como un int
# ─────────────────────────────────────────
@router.get(
    "/stats/resumen",
    summary="Estadísticas generales",
    response_model=dict,
)
# def obtener_estadisticas():
def obtener_estadisticas(db: Session = Depends(get_db)):
    """
    Retorna estadísticas generales del sistema:
    - Total de estudiantes registrados
    - Cantidad de activos e inactivos
    - Promedio general de calificaciones
    - Distribución por carrera
    """
    # return svc.estadisticas()
    return svc.estadisticas(db)  # NUEVO: pasar db a la capa de servicio


# ─────────────────────────────────────────
# GET /estudiantes/
# ─────────────────────────────────────────
@router.get(
    "/",
    response_model=list[EstudianteResponse],
    summary="Listar estudiantes",
)
def listar_estudiantes(
    skip: int = Query(0, ge=0, description="Registros a saltar (paginación)"),
    limit: int = Query(10, ge=1, le=100, description="Cantidad máxima a retornar"),
    carrera: Optional[str] = Query(None, description="Filtrar por carrera"),
    buscar: Optional[str] = Query(None, description="Buscar por nombre"),
    activo: Optional[bool] = Query(None, description="Filtrar por estado activo/inactivo"),
    db: Session = Depends(get_db),  # NUEVO: inyectar sesión de BD
):
    """
    Lista estudiantes con paginación y filtros opcionales.
    Combina cualquier filtro: carrera, nombre y estado activo.
    """
    # return svc.obtener_todos(carrera, buscar, activo, skip, limit)
    return svc.obtener_todos(db, carrera, buscar, activo, skip, limit)  # NUEVO: pasar db a la capa de servicio


# ─────────────────────────────────────────
# GET /estudiantes/{estudiante_id}
# ─────────────────────────────────────────
@router.get(
    "/{estudiante_id}",
    response_model=EstudianteResponse,
    summary="Obtener estudiante por ID",
)
# def obtener_estudiante(estudiante_id: int):
def obtener_estudiante(estudiante_id: int, db: Session = Depends(get_db)):
    """
    Retorna un estudiante específico por su ID.
    Lanza 404 si no existe.
    """
    # return svc.obtener_por_id(estudiante_id)
    return svc.obtener_por_id(db, estudiante_id)


# ─────────────────────────────────────────
# POST /estudiantes/
# ─────────────────────────────────────────
@router.post(
    "/",
    response_model=EstudianteResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Crear estudiante",
)
# def crear_estudiante(estudiante: EstudianteCreate):
def crear_estudiante(estudiante: EstudianteCreate, db: Session = Depends(get_db)):
    """
    Crea un nuevo estudiante aplicando validaciones de schema y de negocio.

    Validaciones de schema (automáticas):
    - Nombre con al menos 2 palabras y sin números
    - Matrícula de exactamente 7 dígitos
    - Email con formato válido
    - Semestre entre 1 y 12
    - Promedio entre 0.0 y 10.0
    - Teléfono de 10 dígitos (opcional)

    Validaciones de negocio:
    - Email no duplicado (409)
    - Matrícula no duplicada (409)
    """
    # return svc.crear(estudiante)
    return svc.crear(db, estudiante)  # NUEVO: pasar db a la capa de servicio


# ─────────────────────────────────────────
# PUT /estudiantes/{estudiante_id}
# ─────────────────────────────────────────
@router.put(
    "/{estudiante_id}",
    response_model=EstudianteResponse,
    summary="Actualizar estudiante completo",
)
# def actualizar_estudiante(estudiante_id: int, estudiante: EstudianteCreate):
def actualizar_estudiante(estudiante_id: int, estudiante: EstudianteCreate, db: Session = Depends(get_db)):
    """
    Reemplaza TODOS los campos del estudiante.
    Debes enviar todos los datos aunque no cambien.
    Lanza 404 si el estudiante no existe.
    """
    # return svc.actualizar(estudiante_id, estudiante)
    return svc.actualizar(db, estudiante_id, estudiante)  # NUEVO: pasar db a la capa de servicio


# ─────────────────────────────────────────
# PATCH /estudiantes/{estudiante_id}
# ─────────────────────────────────────────
@router.patch(
    "/{estudiante_id}",
    response_model=EstudianteResponse,
    summary="Actualizar campos específicos",
)
# def actualizar_parcial(estudiante_id: int, estudiante: EstudianteUpdate):
def actualizar_parcial(estudiante_id: int, estudiante: EstudianteUpdate, db: Session = Depends(get_db)):
    """
    Actualiza SOLO los campos que envíes en el body.
    Los campos omitidos se conservan con su valor actual.
    Lanza 404 si el estudiante no existe.
    """
    # return svc.actualizar_parcial(estudiante_id, estudiante)
    return svc.actualizar_parcial(db, estudiante_id, estudiante)  # NUEVO: pasar db a la capa de servicio

# ─────────────────────────────────────────
# PUT /estudiantes/{estudiante_id}/estado
# Separado de PATCH general para evitar
# ambigüedad de rutas y ser más explícito
# ─────────────────────────────────────────
@router.put(
    "/{estudiante_id}/estado",
    response_model=EstudianteResponse,
    summary="Activar o desactivar estudiante",
)
def cambiar_estado(
    estudiante_id: int,
    activo: bool = Body(..., embed=True, description="true para activar, false para desactivar"),
    db: Session = Depends(get_db),                      # NUEVO
):
    """
    Cambia el estado activo/inactivo del estudiante.
    Recibe el valor en el body: { "activo": true } o { "activo": false }.
    Lanza 404 si el estudiante no existe.
    """
    # return svc.cambiar_estado(estudiante_id, activo)
    return svc.cambiar_estado(db, estudiante_id, activo)  # ANTES: sin db

# ─────────────────────────────────────────
# DELETE /estudiantes/{estudiante_id}
# ─────────────────────────────────────────
@router.delete(
    "/{estudiante_id}",
    summary="Eliminar estudiante",
    response_model=dict,
)
# def eliminar_estudiante(estudiante_id: int):
def eliminar_estudiante(estudiante_id: int, db: Session = Depends(get_db)):
    """
    Elimina permanentemente un estudiante por su ID.
    Retorna un mensaje de confirmación.
    Lanza 404 si el estudiante no existe.
    """
    # return svc.eliminar(estudiante_id)
    return svc.eliminar(db, estudiante_id)  # ANTES: sin db
