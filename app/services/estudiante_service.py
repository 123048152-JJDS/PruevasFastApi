from sqlalchemy.orm import Session
from sqlalchemy import func
from fastapi import HTTPException, status
from app.models.estudiante import Estudiante
from app.schemas.estudiante import EstudianteCreate, EstudianteUpdate

# from datetime import datetime

# ── ANTES: base de datos en memoria ──────
# Semana 4 la reemplazamos con PostgreSQL
# estudiantes_db = [
#     {
#         "id": 1, "nombre": "Juan Pérez", "matricula": "2021001",
#         "email": "juan.perez@universidad.edu", "carrera": "ingenieria",
#         "semestre": 4, "promedio": 8.75, "telefono": "4421234567",
#         "activo": True, "fecha_registro": datetime(2021, 8, 15)
#     },
#     {
#         "id": 2, "nombre": "María López", "matricula": "2021002",
#         "email": "maria.lopez@universidad.edu", "carrera": "medicina",
#         "semestre": 6, "promedio": 9.20, "telefono": "4429876543",
#         "activo": True, "fecha_registro": datetime(2021, 8, 15)
#     },
#     {
#         "id": 3, "nombre": "Carlos García", "matricula": "2021003",
#         "email": "carlos.garcia@universidad.edu", "carrera": "derecho",
#         "semestre": 3, "promedio": 7.80, "telefono": None,
#         "activo": True, "fecha_registro": datetime(2021, 8, 15)
#     },
#     {
#         "id": 4, "nombre": "Ana Martínez", "matricula": "2021004",
#         "email": "ana.martinez@universidad.edu", "carrera": "ingenieria",
#         "semestre": 5, "promedio": 9.50, "telefono": "4425551234",
#         "activo": True, "fecha_registro": datetime(2022, 1, 20)
#     },
#     {
#         "id": 5, "nombre": "Pedro Sánchez", "matricula": "2024305",
#         "email": "pedro.sanchez@universidad.edu", "carrera": "medicina",
#         "semestre": 2, "promedio": 8.10, "telefono": None,
#         "activo": False, "fecha_registro": datetime(2024, 8, 10)
#     },
# ]
# siguiente_id = 6


# ── Helpers internos ──────────────────────
# AHORA: recibe db, consulta BD real, retorna objeto ORM
# def _buscar_por_id(estudiante_id: int) -> dict:
def _buscar_por_id(db: Session, estudiante_id: int) -> Estudiante:
    """Retorna el estudiante o lanza 404."""
    # for e in estudiantes_db:
    #     if e["id"] == estudiante_id:
    #         return e
    est = db.query(Estudiante).filter(Estudiante.id == estudiante_id).first()
    if not est:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Estudiante con ID {estudiante_id} no encontrado",
        )
    return est


# AHORA: usa queries SQLAlchemy en lugar de listas en memoria
def _validar_duplicados(
    db: Session,  # NUEVO: recibe sesión para consultar la BD
    email: str,
    matricula: str,
    excluir_id: int = None,
):
    """Lanza 409 si el email o matrícula ya existen (ignorando excluir_id)."""
    # for e in estudiantes_db:
    #     if excluir_id and e["id"] == excluir_id:
    #         continue
    #     if e["email"] == email:
    #         raise HTTPException(
    #             status_code=status.HTTP_409_CONFLICT,
    #             detail=f"Ya existe un estudiante con el email '{email}'"
    #         )
    #     if e["matricula"] == matricula:
    #         raise HTTPException(
    #             status_code=status.HTTP_409_CONFLICT,
    #             detail=f"Ya existe un estudiante con la matrícula '{matricula}'"
    #         )
    q = db.query(Estudiante)
    if excluir_id:
        q = q.filter(Estudiante.id != excluir_id)
    if q.filter(Estudiante.email == email).first():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Ya existe un estudiante con el email '{email}'",
        )
    if q.filter(Estudiante.matricula == matricula).first():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Ya existe un estudiante con la matrícula '{matricula}'",
        )


# ── Funciones de servicio ─────────────────
# AHORA: construye query SQLAlchemy con filtros encadenados
def obtener_todos(
    db: Session,  # Nuevo: recibe sesión para consultar la BD
    carrera=None,
    buscar=None,
    activo=None,
    skip=0,
    limit=10,
):
    # resultado = estudiantes_db
    # if carrera:
    #     resultado = [e for e in resultado if e["carrera"] == carrera.lower()]
    # if buscar:
    #     resultado = [e for e in resultado if buscar.lower() in e["nombre"].lower()]
    # if activo is not None:
    #     resultado = [e for e in resultado if e["activo"] == activo]
    # return resultado[skip: skip + limit]
    q = db.query(Estudiante)
    if carrera:
        q = q.filter(Estudiante.carrera == carrera.lower())
    if buscar:
        q = q.filter(Estudiante.nombre.ilike(f"%{buscar}%"))
    if activo is not None:
        q = q.filter(Estudiante.activo == activo)
    return q.offset(skip).limit(limit).all()


# AHORA: recibe db como primer argumento
def obtener_por_id(
    db: Session, estudiante_id: int
) -> Estudiante:  # ANTES: def obtener_por_id(estudiante_id: int) -> dict:
    return _buscar_por_id(db, estudiante_id)


# AHORA: crea objeto ORM, guarda en BD y refresca para obtener id/fecha
# def actualizar(estudiante_id: int, datos: EstudianteCreate) -> dict:
def crear(db: Session, datos: EstudianteCreate) -> Estudiante:
    # global siguiente_id
    # _validar_duplicados(datos.email, datos.matricula)
    _validar_duplicados(db, datos.email, datos.matricula)
    # nuevo = {
    #     "id": siguiente_id,
    #     **datos.model_dump(),
    #     "activo": True,
    #     "fecha_registro": datetime.now()
    # }
    # estudiantes_db.append(nuevo)
    # siguiente_id += 1
    nuevo = Estudiante(**datos.model_dump())
    db.add(nuevo)
    db.commit()
    db.refresh(nuevo)
    return nuevo


# AHORA: usa setattr para actualizar objeto ORM campo por campo
# def actualizar_parcial(estudiante_id: int, datos: EstudianteUpdate) -> dict:
def actualizar(db: Session, estudiante_id: int, datos: EstudianteCreate) -> Estudiante:
    """PUT — reemplaza todos los campos."""
    # estudiante = _buscar_por_id(estudiante_id)
    # _validar_duplicados(datos.email, datos.matricula, excluir_id=estudiante_id)
    # estudiante.update({**datos.model_dump()})
    # return estudiante
    est = _buscar_por_id(db, estudiante_id)
    _validar_duplicados(db, datos.email, datos.matricula, excluir_id=estudiante_id)
    for k, v in datos.model_dump().items():
        setattr(est, k, v)
    db.commit()
    db.refresh(est)
    return est


# def actualizar_parcial(estudiante_id: int, datos: EstudianteUpdate) -> dict:
#     estudiante = _buscar_por_id(estudiante_id)
#     cambios = datos.model_dump(exclude_unset=True)
#     if "email" in cambios or "matricula" in cambios:
#         _validar_duplicados(
#             cambios.get("email", estudiante["email"]),
#             cambios.get("matricula", estudiante["matricula"]),
#             excluir_id=estudiante_id
#         )
#     estudiante.update(cambios)
#     return estudiante


# AHORA: setattr campo por campo + commit
def actualizar_parcial(
    db: Session, estudiante_id: int, datos: EstudianteUpdate
) -> Estudiante:
    """PATCH — actualiza solo los campos enviados."""
    est = _buscar_por_id(db, estudiante_id)
    cambios = datos.model_dump(exclude_unset=True)
    if "email" in cambios or "matricula" in cambios:
        _validar_duplicados(
            db,
            cambios.get("email", est.email),
            cambios.get("matricula", est.matricula),
            excluir_id=estudiante_id,
        )
    for k, v in cambios.items():
        setattr(est, k, v)
    db.commit()
    db.refresh(est)
    return est


# def cambiar_estado(estudiante_id: int, activo: bool) -> dict:
#     estudiante = _buscar_por_id(estudiante_id)
#     estudiante["activo"] = activo
#     return estudiante


def cambiar_estado(db: Session, estudiante_id: int, activo: bool) -> Estudiante:
    """PATCH — activa o desactiva un estudiante."""
    est = _buscar_por_id(db, estudiante_id)
    est.activo = activo
    db.commit()
    db.refresh(est)
    return est


# def eliminar(estudiante_id: int) -> dict:
#     estudiante = _buscar_por_id(estudiante_id)
#     estudiantes_db.remove(estudiante)
#     return {"mensaje": f"Estudiante '{estudiante['nombre']}' eliminado correctamente"}


def eliminar(db: Session, estudiante_id: int) -> dict:
    """DELETE — elimina el registro permanentemente."""
    est = _buscar_por_id(db, estudiante_id)
    nombre = est.nombre
    db.delete(est)
    db.commit()
    return {"mensaje": f"Estudiante '{nombre}' eliminado correctamente"}


# def estadisticas() -> dict:
#     activos = [e for e in estudiantes_db if e["activo"]]
#     promedios = [e["promedio"] for e in estudiantes_db]
#     promedio_general = round(sum(promedios) / len(promedios), 2) if promedios else 0
#     carreras = {}
#     for e in estudiantes_db:
#         carreras[e["carrera"]] = carreras.get(e["carrera"], 0) + 1
#     return {
#         "total": len(estudiantes_db),
#         "activos": len(activos),
#         "inactivos": len(estudiantes_db) - len(activos),
#         "promedio_general": promedio_general,
#         "por_carrera": carreras,
#     }


def estadisticas(db: Session) -> dict:
    total = db.query(Estudiante).count()
    activos = db.query(Estudiante).filter(Estudiante.activo == True).count()
    promedio = db.query(func.avg(Estudiante.promedio)).scalar() or 0
    carreras = {}
    for row in (
        db.query(Estudiante.carrera, func.count(Estudiante.id))
        .group_by(Estudiante.carrera)
        .all()
    ):
        carreras[row[0]] = row[1]
    return {
        "total": total,
        "activos": activos,
        "inactivos": total - activos,
        "promedio_general": round(promedio, 2),
        "por_carrera": carreras,
    }
