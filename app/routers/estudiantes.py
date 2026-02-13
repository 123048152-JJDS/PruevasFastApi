from fastapi import APIRouter, Query
router = APIRouter(
    prefix="/estudiantes",
    tags=["Estudiantes"]
)

estudiantes_db = [
    {"id": 1, "nombre": "Juan Pérez", "matricula": "2021001", "carrera": "ingenieria"},
    {"id": 2, "nombre": "María López", "matricula": "2021002", "carrera": "medicina"},
    {"id": 3, "nombre": "Carlos García", "matricula": "2021003", "carrera": "derecho"},
    {"id": 4, "nombre": "Ana Martínez", "matricula": "2021004", "carrera": "ingenieria"},
    {"id": 5, "nombre": "Pedro Sánchez", "matricula": "2024305", "carrera": "medicina"},
    {"id": 6, "nombre": "Carlos Marques", "matricula": "2065003", "carrera": "derecho"},
    {"id": 7, "nombre": "Luisa Martínez", "matricula": "2021544", "carrera": "ingenieria"},
    {"id": 8, "nombre": "Petronilo Sánchez", "matricula": "2025405", "carrera": "medicina"}
]

@router.get("/")
def listar_estudiantes(
    skip: int = Query(0, ge=0, description="Número de registros a saltar"),
    limit: int = Query(10, ge=1, le=100, description="Cantidad de registros a retornar"),
    carrera: str = Query(None, description="Filtrar por carrera")
):
    """
    Lista todos los estudiantes con paginación.
   
    - **skip**: Cuántos estudiantes saltar (para paginación)
    - **limit**: Cuántos estudiantes retornar (máximo 100)
    - **Carrera**: Filtro de estudiantes por carrera
    """
    estudiantes = estudiantes_db

    if carrera:
        estudiantes = [e for e in estudiantes if e["carrera"]== carrera]
    return {
        "total": len(estudiantes_db),
        "skip": skip,
        "limit": limit,
        "Filtros":{"carrera": carrera} if carrera else None,
        "estudiantes": estudiantes_db[skip : skip + limit]
    }

@router.get("/{estudiante_id}")
def obtener_estudiante(estudiante_id: int):
    """
    Obtiene un estudiante por su ID.
    """
    for estudiante in estudiantes_db:
        if estudiante["id"] == estudiante_id:
            return estudiante
    return {"error": "Estudiante no encontrado"}