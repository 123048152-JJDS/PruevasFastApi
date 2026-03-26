from datetime import datetime
from fastapi import HTTPException, status
from app.schemas.estudiante import EstudianteCreate, EstudianteUpdate

# ── Base de datos en memoria ──────────────
# Semana 4 la reemplazamos con PostgreSQL
estudiantes_db = [
    {
        "id": 1, "nombre": "Juan Pérez", "matricula": "2021001",
        "email": "juan.perez@universidad.edu", "carrera": "ingenieria",
        "semestre": 4, "promedio": 8.75, "telefono": "4421234567",
        "activo": True, "fecha_registro": datetime(2021, 8, 15)
    },
    {
        "id": 2, "nombre": "María López", "matricula": "2021002",
        "email": "maria.lopez@universidad.edu", "carrera": "medicina",
        "semestre": 6, "promedio": 9.20, "telefono": "4429876543",
        "activo": True, "fecha_registro": datetime(2021, 8, 15)
    },
    {
        "id": 3, "nombre": "Carlos García", "matricula": "2021003",
        "email": "carlos.garcia@universidad.edu", "carrera": "derecho",
        "semestre": 3, "promedio": 7.80, "telefono": None,
        "activo": True, "fecha_registro": datetime(2021, 8, 15)
    },
    {
        "id": 4, "nombre": "Ana Martínez", "matricula": "2021004",
        "email": "ana.martinez@universidad.edu", "carrera": "ingenieria",
        "semestre": 5, "promedio": 9.50, "telefono": "4425551234",
        "activo": True, "fecha_registro": datetime(2022, 1, 20)
    },
    {
        "id": 5, "nombre": "Pedro Sánchez", "matricula": "2024305",
        "email": "pedro.sanchez@universidad.edu", "carrera": "medicina",
        "semestre": 2, "promedio": 8.10, "telefono": None,
        "activo": False, "fecha_registro": datetime(2024, 8, 10)
    },
]

siguiente_id = 6


# ── Helpers internos ──────────────────────
def _buscar_por_id(estudiante_id: int) -> dict:
    """Retorna el estudiante o lanza 404."""
    for e in estudiantes_db:
        if e["id"] == estudiante_id:
            return e
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Estudiante con ID {estudiante_id} no encontrado"
    )


def _validar_duplicados(email: str, matricula: str, excluir_id: int = None):
    """Lanza 409 si el email o matrícula ya existen (ignorando excluir_id)."""
    for e in estudiantes_db:
        if excluir_id and e["id"] == excluir_id:
            continue
        if e["email"] == email:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Ya existe un estudiante con el email '{email}'"
            )
        if e["matricula"] == matricula:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Ya existe un estudiante con la matrícula '{matricula}'"
            )


# ── Funciones de servicio ─────────────────
def obtener_todos(carrera=None, buscar=None, activo=None, skip=0, limit=10):
    resultado = estudiantes_db
    if carrera:
        resultado = [e for e in resultado if e["carrera"] == carrera.lower()]
    if buscar:
        resultado = [e for e in resultado if buscar.lower() in e["nombre"].lower()]
    if activo is not None:
        resultado = [e for e in resultado if e["activo"] == activo]
    return resultado[skip: skip + limit]


def obtener_por_id(estudiante_id: int) -> dict:
    return _buscar_por_id(estudiante_id)


def crear(datos: EstudianteCreate) -> dict:
    global siguiente_id
    _validar_duplicados(datos.email, datos.matricula)
    nuevo = {
        "id": siguiente_id,
        **datos.model_dump(),
        "activo": True,
        "fecha_registro": datetime.now()
    }
    estudiantes_db.append(nuevo)
    siguiente_id += 1
    return nuevo


def actualizar(estudiante_id: int, datos: EstudianteCreate) -> dict:
    """PUT — reemplaza todos los campos."""
    estudiante = _buscar_por_id(estudiante_id)
    _validar_duplicados(datos.email, datos.matricula, excluir_id=estudiante_id)
    estudiante.update({**datos.model_dump()})
    return estudiante


def actualizar_parcial(estudiante_id: int, datos: EstudianteUpdate) -> dict:
    """PATCH — actualiza solo los campos enviados."""
    estudiante = _buscar_por_id(estudiante_id)
    cambios = datos.model_dump(exclude_unset=True)
    if "email" in cambios or "matricula" in cambios:
        _validar_duplicados(
            cambios.get("email", estudiante["email"]),
            cambios.get("matricula", estudiante["matricula"]),
            excluir_id=estudiante_id
        )
    estudiante.update(cambios)
    return estudiante


def cambiar_estado(estudiante_id: int, activo: bool) -> dict:
    """PATCH — activa o desactiva un estudiante."""
    estudiante = _buscar_por_id(estudiante_id)
    estudiante["activo"] = activo
    return estudiante


def eliminar(estudiante_id: int) -> dict:
    """DELETE — elimina el registro permanentemente."""
    estudiante = _buscar_por_id(estudiante_id)
    estudiantes_db.remove(estudiante)
    return {"mensaje": f"Estudiante '{estudiante['nombre']}' eliminado correctamente"}


def estadisticas() -> dict:
    activos = [e for e in estudiantes_db if e["activo"]]
    promedios = [e["promedio"] for e in estudiantes_db]
    promedio_general = round(sum(promedios) / len(promedios), 2) if promedios else 0
    carreras = {}
    for e in estudiantes_db:
        carreras[e["carrera"]] = carreras.get(e["carrera"], 0) + 1
    return {
        "total": len(estudiantes_db),
        "activos": len(activos),
        "inactivos": len(estudiantes_db) - len(activos),
        "promedio_general": promedio_general,
        "por_carrera": carreras
    }