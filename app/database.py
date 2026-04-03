from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from app.config import settings

# Motor de base de datos
# check_same_thread=False solo es necesario para SQLite
engine = create_engine(
    settings.database_url,
    connect_args={"check_same_thread": False}
)

# Fábrica de sesiones — cada request HTTP obtiene su propia sesión
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)


# Clase base para todos los modelos ORM
class Base(DeclarativeBase):
    pass


# Dependency para FastAPI — se usa con Depends(get_db)
def get_db():
    db = SessionLocal()
    try:
        yield db  # entrega la sesión al endpoint
    finally:
        db.close()  # siempre cierra al terminar
