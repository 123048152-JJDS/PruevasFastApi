from datetime import datetime
from fastapi import HTTPException, status
from app.schemas.profesor import ProfesorCreate, ProfesorUpdate

profesores_db = [
    {
        "id": 1, "nombre": "Roberto Méndez", "email": "r.mendez@universidad.edu",
        "departamento": "ingenieria", "especialidad": "estructuras de datos",
        "telefono": "4421110001", "activo": True,
        "fecha_registro": datetime(2020, 1, 10)
    },
    {
        "id": 2, "nombre": "Laura Vega", "email": "l.vega@universidad.edu",
        "departamento": "medicina", "especialidad": "anatomia humana",
        "telefono": "4421110002", "activo": True,
        "fecha_registro": datetime(2019, 3, 5)
    },
    {
        "id": 3, "nombre": "Sergio Ruiz", "email": "s.ruiz@universidad.edu",
        "departamento": "derecho", "especialidad": "derecho constitucional",
        "telefono": None, "activo": False,
        "fecha_registro": datetime(2018, 8, 20)
    },
]

siguiente_id = 4


# ── Helpers internos ──────────────────────
def _buscar_por_id(profesor_id: int) -> dict:
    for p in profesores_db:
        if p["id"] == profesor_id:
            return p
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Profesor con ID {profesor_id} no encontrado"
    )


def _validar_duplicados(email: str, excluir_id: int = None):
    for p in profesores_db:
        if excluir_id and p["id"] == excluir_id:
            continue
        if p["email"] == email:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Ya existe un profesor con el email '{email}'"
            )


# ── Funciones de servicio ─────────────────
def obtener_todos(departamento=None, activo=None, skip=0, limit=10):
    resultado = profesores_db
    if departamento:
        resultado = [p for p in resultado if p["departamento"] == departamento.lower()]
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
    profesor = _buscar_por_id(profesor_id)
    _validar_duplicados(datos.email, excluir_id=profesor_id)
    profesor.update({**datos.model_dump()})
    return profesor


def actualizar_parcial(profesor_id: int, datos: ProfesorUpdate) -> dict:
    profesor = _buscar_por_id(profesor_id)
    cambios = datos.model_dump(exclude_unset=True)
    if "email" in cambios:
        _validar_duplicados(cambios["email"], excluir_id=profesor_id)
    profesor.update(cambios)
    return profesor


def cambiar_estado(profesor_id: int, activo: bool) -> dict:
    profesor = _buscar_por_id(profesor_id)
    profesor["activo"] = activo
    return profesor


def eliminar(profesor_id: int) -> dict:
    profesor = _buscar_por_id(profesor_id)
    profesores_db.remove(profesor)
    return {"mensaje": f"Profesor '{profesor['nombre']}' eliminado correctamente"}
