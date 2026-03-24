from fastapi import APIRouter, Query, Body, status
from typing import Optional
from app.schemas.profesor import ProfesorCreate, ProfesorResponse, ProfesorUpdate
import app.services.profesor_service as svc

router = APIRouter(prefix="/profesores", tags=["Profesores"])


@router.get(
    "/",
    response_model=list[ProfesorResponse],
    summary="Listar profesores",
)
def listar_profesores(
    skip: int = Query(0, ge=0, description="Registros a saltar (paginación)"),
    limit: int = Query(10, ge=1, le=100, description="Cantidad máxima a retornar"),
    departamento: Optional[str] = Query(None, description="Filtrar por departamento"),
    activo: Optional[bool] = Query(None, description="Filtrar por estado activo/inactivo"),
):
    """
    Lista profesores con paginación y filtros opcionales.
    """
    return svc.obtener_todos(departamento, activo, skip, limit)


@router.get(
    "/{profesor_id}",
    response_model=ProfesorResponse,
    summary="Obtener profesor por ID",
)
def obtener_profesor(profesor_id: int):
    """
    Retorna un profesor específico por su ID.
    Lanza 404 si no existe.
    """
    return svc.obtener_por_id(profesor_id)


@router.post(
    "/",
    response_model=ProfesorResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Crear profesor",
)
def crear_profesor(profesor: ProfesorCreate):
    """
    Crea un nuevo profesor.
    Validaciones de negocio: email no duplicado (409).
    """
    return svc.crear(profesor)


@router.put(
    "/{profesor_id}",
    response_model=ProfesorResponse,
    summary="Actualizar profesor completo",
)
def actualizar_profesor(profesor_id: int, profesor: ProfesorCreate):
    """
    Reemplaza TODOS los campos del profesor.
    Debes enviar todos los datos aunque no cambien.
    Lanza 404 si el profesor no existe.
    """
    return svc.actualizar(profesor_id, profesor)


@router.patch(
    "/{profesor_id}",
    response_model=ProfesorResponse,
    summary="Actualizar campos específicos",
)
def actualizar_parcial(profesor_id: int, profesor: ProfesorUpdate):
    """
    Actualiza SOLO los campos que envíes en el body.
    Los campos omitidos se conservan con su valor actual.
    Lanza 404 si el profesor no existe.
    """
    return svc.actualizar_parcial(profesor_id, profesor)


@router.put(
    "/{profesor_id}/estado",
    response_model=ProfesorResponse,
    summary="Activar o desactivar profesor",
)
def cambiar_estado(
    profesor_id: int,
    activo: bool = Body(..., embed=True, description="true para activar, false para desactivar"),
):
    """
    Cambia el estado activo/inactivo del profesor.
    Recibe el valor en el body: { "activo": true } o { "activo": false }.
    Lanza 404 si el profesor no existe.
    """
    return svc.cambiar_estado(profesor_id, activo)


@router.delete(
    "/{profesor_id}",
    summary="Eliminar profesor",
    response_model=dict,
)
def eliminar_profesor(profesor_id: int):
    """
    Elimina permanentemente un profesor por su ID.
    Retorna un mensaje de confirmación.
    Lanza 404 si el profesor no existe.
    """
    return svc.eliminar(profesor_id)