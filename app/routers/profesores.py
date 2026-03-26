from fastapi import APIRouter, Query, HTTPException, status
from typing import Optional
from app.schemas.profesor import ProfesorCreate, ProfesorUpdate, ProfesorResponse
import app.services.profesor_service as svc

router = APIRouter(
    prefix="/profesores",
    tags=["Profesores"]
)


# ─────────────────────────────────────────
# GET /profesores/stats/resumen
# IMPORTANTE: va ANTES de /{profesor_id}
# ─────────────────────────────────────────
@router.get("/stats/resumen", summary="Estadísticas generales de profesores")
def obtener_estadisticas():
    """Retorna estadísticas generales del módulo de profesores."""
    return svc.estadisticas()


# ─────────────────────────────────────────
# GET /profesores/
# ─────────────────────────────────────────
@router.get("/", response_model=list[ProfesorResponse], summary="Listar profesores")
def listar_profesores(
    skip: int = Query(0, ge=0, description="Registros a saltar"),
    limit: int = Query(10, ge=1, le=100, description="Cantidad a retornar"),
    departamento: Optional[str] = Query(None, description="Filtrar por departamento"),
    buscar: Optional[str] = Query(None, description="Buscar por nombre"),
    activo: Optional[bool] = Query(None, description="Filtrar por estado")
):
    """Lista profesores con paginación y filtros opcionales."""
    return svc.obtener_todos(departamento, buscar, activo, skip, limit)


# ─────────────────────────────────────────
# GET /profesores/{profesor_id}
# ─────────────────────────────────────────
@router.get("/{profesor_id}", response_model=ProfesorResponse, summary="Obtener profesor por ID")
def obtener_profesor(profesor_id: int):
    """Retorna un profesor específico por su ID. Lanza 404 si no existe."""
    return svc.obtener_por_id(profesor_id)


# ─────────────────────────────────────────
# POST /profesores/
# ─────────────────────────────────────────
@router.post("/", response_model=ProfesorResponse, status_code=status.HTTP_201_CREATED, summary="Crear profesor")
def crear_profesor(profesor: ProfesorCreate):
    """Crea un nuevo profesor. Valida email único y formato de campos."""
    return svc.crear(profesor)


# ─────────────────────────────────────────
# PUT /profesores/{profesor_id}
# ─────────────────────────────────────────
@router.put("/{profesor_id}", response_model=ProfesorResponse, summary="Actualizar profesor completo")
def actualizar_profesor(profesor_id: int, profesor: ProfesorCreate):
    """PUT — reemplaza todos los campos del profesor."""
    return svc.actualizar(profesor_id, profesor)


# ─────────────────────────────────────────
# PATCH /profesores/{profesor_id}
# ─────────────────────────────────────────
@router.patch("/{profesor_id}", response_model=ProfesorResponse, summary="Actualizar profesor parcial")
def actualizar_parcial(profesor_id: int, profesor: ProfesorUpdate):
    """PATCH — actualiza solo los campos enviados."""
    return svc.actualizar_parcial(profesor_id, profesor)


# ─────────────────────────────────────────
# PATCH /profesores/{profesor_id}/estado
# ─────────────────────────────────────────
@router.patch("/{profesor_id}/estado", response_model=ProfesorResponse, summary="Activar o desactivar profesor")
def cambiar_estado(profesor_id: int, activo: bool = Query(..., description="true = activar, false = desactivar")):
    """Activa o desactiva un profesor sin eliminarlo."""
    return svc.cambiar_estado(profesor_id, activo)


# ─────────────────────────────────────────
# DELETE /profesores/{profesor_id}
# ─────────────────────────────────────────
@router.delete("/{profesor_id}", status_code=status.HTTP_200_OK, summary="Eliminar profesor")
def eliminar_profesor(profesor_id: int):
    """DELETE — elimina el registro permanentemente."""
    return svc.eliminar(profesor_id)