# from fastapi import APIRouter, Query, HTTPException, status
from fastapi import APIRouter, Query, status, Depends
from sqlalchemy.orm import Session
from typing import Optional
from app.schemas.profesor import ProfesorCreate, ProfesorUpdate, ProfesorResponse
from app.database import get_db          # NUEVO: importar get_db
import app.services.profesor_service as svc

router = APIRouter(prefix="/profesores",tags=["Profesores"])


# ─────────────────────────────────────────
# GET /profesores/stats/resumen
# IMPORTANTE: va ANTES de /{profesor_id}
# ─────────────────────────────────────────
@router.get("/stats/resumen", summary="Estadísticas generales de profesores")
# def obtener_estadisticas():
def obtener_estadisticas(db: Session = Depends(get_db)):
    """Retorna estadísticas generales del módulo de profesores."""
    # return svc.estadisticas()
    return svc.estadisticas(db)  # NUEVO: pasar db a la capa de servicio

# ─────────────────────────────────────────
# GET /profesores/
# ─────────────────────────────────────────
@router.get("/", response_model=list[ProfesorResponse], summary="Listar profesores")
def listar_profesores(
    skip: int = Query(0, ge=0, description="Registros a saltar"),
    limit: int = Query(10, ge=1, le=100, description="Cantidad a retornar"),
    departamento: Optional[str] = Query(None, description="Filtrar por departamento"),
    buscar: Optional[str] = Query(None, description="Buscar por nombre"),
    activo: Optional[bool] = Query(None, description="Filtrar por estado"),
    db: Session = Depends(get_db),                      # NUEVO: inyectar sesión de BD
):
    """Lista profesores con paginación y filtros opcionales."""
    # return svc.obtener_todos(departamento, buscar, activo, skip, limit)
    return svc.obtener_todos(db, departamento, buscar, activo, skip, limit)  # NUEVO: pasar db a la capa de servicio


# ─────────────────────────────────────────
# GET /profesores/{profesor_id}
# ─────────────────────────────────────────
@router.get("/{profesor_id}", response_model=ProfesorResponse, summary="Obtener profesor por ID")
# def obtener_profesor(profesor_id: int):
def obtener_profesor(profesor_id: int, db: Session = Depends(get_db)):
    """Retorna un profesor específico por su ID. Lanza 404 si no existe."""
    # return svc.obtener_por_id(profesor_id)
    return svc.obtener_por_id(db, profesor_id)  # NUEVO: pasar db a la capa de servicio


# ─────────────────────────────────────────
# POST /profesores/
# ─────────────────────────────────────────
@router.post("/", response_model=ProfesorResponse, status_code=status.HTTP_201_CREATED, summary="Crear profesor")
# def crear_profesor(profesor: ProfesorCreate):
def crear_profesor(profesor: ProfesorCreate, db: Session = Depends(get_db)):
    """Crea un nuevo profesor. Valida email único y formato de campos."""
    # return svc.crear(profesor)
    return svc.crear(db, profesor)  # NUEVO: pasar db a la capa de servicio


# ─────────────────────────────────────────
# PUT /profesores/{profesor_id}
# ─────────────────────────────────────────
@router.put("/{profesor_id}", response_model=ProfesorResponse, summary="Actualizar profesor completo")
# def actualizar_profesor(profesor_id: int, profesor: ProfesorCreate):
def actualizar_profesor(profesor_id: int, profesor: ProfesorCreate, db: Session = Depends(get_db)):
    """PUT — reemplaza todos los campos del profesor."""
    # return svc.actualizar(profesor_id, profesor)
    return svc.actualizar(db, profesor_id, profesor)  # NUEVO: pasar db a la capa de servicio


# ─────────────────────────────────────────
# PATCH /profesores/{profesor_id}
# ─────────────────────────────────────────
@router.patch("/{profesor_id}", response_model=ProfesorResponse, summary="Actualizar profesor parcial")
# def actualizar_parcial(profesor_id: int, profesor: ProfesorUpdate):
def actualizar_parcial(profesor_id: int, profesor: ProfesorUpdate, db: Session = Depends(get_db)):
    """PATCH — actualiza solo los campos enviados."""
    # return svc.actualizar_parcial(profesor_id, profesor)
    return svc.actualizar_parcial(db, profesor_id, profesor)  # NUEVO: pasar db a la capa de servicio


# ─────────────────────────────────────────
# PATCH /profesores/{profesor_id}/estado
# ─────────────────────────────────────────
@router.patch("/{profesor_id}/estado", response_model=ProfesorResponse, summary="Activar o desactivar profesor")
# def cambiar_estado(profesor_id: int, activo: bool = Query(..., description="true = activar, false = desactivar")):
def cambiar_estado(profesor_id: int, activo: bool = Query(..., description="true = activar, false = desactivar"), db: Session = Depends(get_db)):
    """Activa o desactiva un profesor sin eliminarlo."""
    # return svc.cambiar_estado(profesor_id, activo)
    return svc.cambiar_estado(db, profesor_id, activo)  # NUEVO: pasar db a la capa de servicio

# ─────────────────────────────────────────
# DELETE /profesores/{profesor_id}
# ─────────────────────────────────────────
@router.delete("/{profesor_id}", status_code=status.HTTP_200_OK, summary="Eliminar profesor")
# def eliminar_profesor(profesor_id: int):
def eliminar_profesor(profesor_id: int, db: Session = Depends(get_db)):
    """DELETE — elimina el registro permanentemente."""
    # return svc.eliminar(profesor_id)
    return svc.eliminar(db, profesor_id)  # NUEVO: pasar db a la capa de servicio