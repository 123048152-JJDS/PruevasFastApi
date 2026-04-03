"""
seed.py — Precarga de datos iniciales
Ejecutar UNA SOLA VEZ después de levantar la BD:

    python seed.py

Si la tabla ya tiene datos, no inserta nada (idempotente).
"""

from datetime import datetime
from app.database import SessionLocal, engine, Base
from app.models.estudiante import Estudiante
from app.models.profesor import Profesor


# ── Datos originales (los que tenías en memoria) ──────────────────────────────

ESTUDIANTES = [
    {
        "nombre": "Juan Pérez",
        "matricula": "2021001",
        "email": "juan.perez@universidad.edu",
        "carrera": "ingenieria",
        "semestre": 4,
        "promedio": 8.75,
        "telefono": "4421234567",
        "activo": True,
        "fecha_registro": datetime(2021, 8, 15),
    },
    {
        "nombre": "María López",
        "matricula": "2021002",
        "email": "maria.lopez@universidad.edu",
        "carrera": "medicina",
        "semestre": 6,
        "promedio": 9.20,
        "telefono": "4429876543",
        "activo": True,
        "fecha_registro": datetime(2021, 8, 15),
    },
    {
        "nombre": "Carlos García",
        "matricula": "2021003",
        "email": "carlos.garcia@universidad.edu",
        "carrera": "derecho",
        "semestre": 3,
        "promedio": 7.80,
        "telefono": None,
        "activo": True,
        "fecha_registro": datetime(2021, 8, 15),
    },
    {
        "nombre": "Ana Martínez",
        "matricula": "2021004",
        "email": "ana.martinez@universidad.edu",
        "carrera": "ingenieria",
        "semestre": 5,
        "promedio": 9.50,
        "telefono": "4425551234",
        "activo": True,
        "fecha_registro": datetime(2022, 1, 20),
    },
    {
        "nombre": "Pedro Sánchez",
        "matricula": "2024305",
        "email": "pedro.sanchez@universidad.edu",
        "carrera": "medicina",
        "semestre": 2,
        "promedio": 8.10,
        "telefono": None,
        "activo": False,
        "fecha_registro": datetime(2024, 8, 10),
    },
]

PROFESORES = [
    {
        "nombre": "Roberto Hernández",
        "email": "roberto.hernandez@universidad.edu",
        "departamento": "ingenieria",
        "especialidad": "programacion orientada a objetos",
        "telefono": "4421112233",
        "activo": True,
        "fecha_registro": datetime(2020, 1, 10),
    },
    {
        "nombre": "Laura Jiménez",
        "email": "laura.jimenez@universidad.edu",
        "departamento": "medicina",
        "especialidad": "anatomia humana",
        "telefono": "4429998877",
        "activo": True,
        "fecha_registro": datetime(2019, 8, 5),
    },
    {
        "nombre": "Miguel Torres",
        "email": "miguel.torres@universidad.edu",
        "departamento": "derecho",
        "especialidad": "derecho constitucional",
        "telefono": None,
        "activo": True,
        "fecha_registro": datetime(2021, 3, 15),
    },
]


# ── Función principal ─────────────────────────────────────────────────────────

def seed():
    # Asegura que las tablas existen antes de insertar
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        # ── Estudiantes ───────────────────────────────
        total_est = db.query(Estudiante).count()
        if total_est == 0:
            for datos in ESTUDIANTES:
                db.add(Estudiante(**datos))
            db.commit()
            print(f"✅ {len(ESTUDIANTES)} estudiantes insertados.")
        else:
            print(f"⏭️  Estudiantes: tabla ya tiene {total_est} registros, se omite.")

        # ── Profesores ────────────────────────────────
        total_prof = db.query(Profesor).count()
        if total_prof == 0:
            for datos in PROFESORES:
                db.add(Profesor(**datos))
            db.commit()
            print(f"✅ {len(PROFESORES)} profesores insertados.")
        else:
            print(f"⏭️  Profesores: tabla ya tiene {total_prof} registros, se omite.")

    except Exception as e:
        db.rollback()
        print(f"❌ Error durante el seed: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed()
    print("\n🎓 Seed completado. Ya puedes levantar el servidor.")
