from fastapi import APIRouter, Query

router = APIRouter(
    prefix="/estudiantes",
    tags=["Estudiantes"]
)

# Base de datos simulada (temporal)
estudiantes_db = [
    {"id": 1, "nombre": "Juan Pérez", "matricula": "2021001", "carrera": "Ingeniería"},
    {"id": 2, "nombre": "María López", "matricula": "2021002", "carrera": "Medicina"},
    {"id": 3, "nombre": "Carlos García", "matricula": "2021003", "carrera": "Derecho"},
    {"id": 4, "nombre": "Ana Martínez", "matricula": "2021004", "carrera": "Ingeniería"},
    {"id": 5, "nombre": "Pedro Sánchez", "matricula": "2021005", "carrera": "Medicina"},
    
    {"id": 6, "nombre": "Laura Rodríguez", "matricula": "2021006", "carrera": "Arquitectura"},
    {"id": 7, "nombre": "Miguel Fernández", "matricula": "2021007", "carrera": "Psicología"},
    {"id": 8, "nombre": "Sofía González", "matricula": "2021008", "carrera": "Administración"},
    {"id": 9, "nombre": "Diego Ramírez", "matricula": "2021009", "carrera": "Contabilidad"},
    {"id": 10, "nombre": "Valentina Díaz", "matricula": "2021010", "carrera": "Enfermería"},
    {"id": 11, "nombre": "Javier Torres", "matricula": "2021011", "carrera": "Ingeniería"},
    {"id": 12, "nombre": "Camila Silva", "matricula": "2021012", "carrera": "Diseño"},
    {"id": 13, "nombre": "Andrés Castro", "matricula": "2021013", "carrera": "Medicina"},
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
    - **carrera**: Filtro de estudiantes por carrera
    """
    
    estudiantes = estudiantes_db
    
    if carrera:
        estudiantes = [e for e in estudiantes if e["carrera"]==carrera]
        
    return {
        "total": len(estudiantes_db),
        "skip": skip,
        "limit": limit,
        "Filtros":{"carrera":carrera} if carrera else None,
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