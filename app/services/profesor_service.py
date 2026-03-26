from datetime import datetime
from fastapi import HTTPException, status
from app.schemas.profesor import ProfesorCreate, ProfesorUpdate

# ── Base de datos en memoria ──────────────
# Semana 4 la reemplazamos con PostgreSQL
profesores_db = [
    {
        "id": 1, "nombre": "Roberto Hernández",
        "email": "roberto.hernandez@universidad.edu",
        "departamento": "ingenieria", "especialidad": "programacion orientada a objetos",
        "telefono": "4421112233", "activo": True,
        "fecha_registro": datetime(2020, 1, 10)
    },
    {
        "id": 2, "nombre": "Laura Jiménez",
        "email": "laura.jimenez@universidad.edu",
        "departamento": "medicina", "especialidad": "anatomia humana",
        "telefono": "4429998877", "activo": True,
        "fecha_registro": datetime(2019, 8, 5)
    },
    {
        "id": 3, "nombre": "Miguel Torres",
        "email": "miguel.torres@universidad.edu",
        "departamento": "derecho", "especialidad": "derecho constitucional",
        "telefono": None, "activo": True,
        "fecha_registro": datetime(2021, 3, 15)
    },
]

siguiente_id = 4


# ── Helpers internos ──────────────────────
def _buscar_por_id(profesor_id: int) -> dict:
    """Retorna el profesor o lanza 404."""
    for p in profesores_db:
        if p["id"] == profesor_id:
            return p
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Profesor con ID {profesor_id} no encontrado"
    )


def _validar_duplicados(email: str, excluir_id: int = None):
    """Lanza 409 si el email ya existe (ignorando excluir_id)."""
    for p in profesores_db:
        if excluir_id and p["id"] == excluir_id:
            continue
        if p["email"] == email:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Ya existe un profesor con el email '{email}'"
            )


# ── Funciones de servicio ─────────────────
def obtener_todos(departamento=None, buscar=None, activo=None, skip=0, limit=10):
    resultado = profesores_db
    if departamento:
        resultado = [p for p in resultado if p["departamento"] == departamento.lower()]
    if buscar:
        resultado = [p for p in resultado if buscar.lower() in p["nombre"].lower()]
    if activo is not None:
        resultado = [p for p in resultado if p["activo"] == activo]
    return resultado[skip: skip + limit]


def obtener_por_id(profesor_id: int) -> dict:
    return _buscar_por_id(profesor_id)


def crear(datos: ProfesorCreate) -> dict:
    global siguiente_id
    _validar_duplicados(datos.email)
    nuevo = {
        "id": siguiente_id,
        **datos.model_dump(),
        "activo": True,
        "fecha_registro": datetime.now()
    }
    profesores_db.append(nuevo)
    siguiente_id += 1
    return nuevo


def actualizar(profesor_id: int, datos: ProfesorCreate) -> dict:
    """PUT — reemplaza todos los campos."""
    profesor = _buscar_por_id(profesor_id)
    _validar_duplicados(datos.email, excluir_id=profesor_id)
    profesor.update({**datos.model_dump()})
    return profesor


def actualizar_parcial(profesor_id: int, datos: ProfesorUpdate) -> dict:
    """PATCH — actualiza solo los campos enviados."""
    profesor = _buscar_por_id(profesor_id)
    cambios = datos.model_dump(exclude_unset=True)
    if "email" in cambios:
        _validar_duplicados(
            cambios.get("email", profesor["email"]),
            excluir_id=profesor_id
        )
    profesor.update(cambios)
    return profesor


def cambiar_estado(profesor_id: int, activo: bool) -> dict:
    """PATCH — activa o desactiva un profesor."""
    profesor = _buscar_por_id(profesor_id)
    profesor["activo"] = activo
    return profesor


def eliminar(profesor_id: int) -> dict:
    """DELETE — elimina el registro permanentemente."""
    profesor = _buscar_por_id(profesor_id)
    profesores_db.remove(profesor)
    return {"mensaje": f"Profesor '{profesor['nombre']}' eliminado correctamente"}


def estadisticas() -> dict:
    activos = [p for p in profesores_db if p["activo"]]
    departamentos = {}
    for p in profesores_db:
        departamentos[p["departamento"]] = departamentos.get(p["departamento"], 0) + 1
    return {
        "total": len(profesores_db),
        "activos": len(activos),
        "inactivos": len(profesores_db) - len(activos),
        "por_departamento": departamentos
    }