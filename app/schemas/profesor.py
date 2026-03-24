from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Optional
from datetime import datetime


# ─────────────────────────────────────────
# BASE: campos comunes a todos los modelos
# ─────────────────────────────────────────
class ProfesorBase(BaseModel):
    nombre: str = Field(
        ..., min_length=3, max_length=100,
        description="Nombre completo del profesor"
    )
    email: EmailStr = Field(..., description="Correo electrónico válido")
    departamento: str = Field(
        ..., min_length=3, max_length=50,
        description="Departamento al que pertenece"
    )
    especialidad: str = Field(
        ..., min_length=3, max_length=100,
        description="Área de especialidad del profesor"
    )
    telefono: Optional[str] = Field(
        None, pattern=r"^\d{10}$",
        description="Teléfono de 10 dígitos (opcional)"
    )

    @field_validator("nombre")
    @classmethod
    def validar_nombre(cls, v: str) -> str:
        if any(char.isdigit() for char in v):
            raise ValueError("El nombre no puede contener números")
        if len(v.split()) < 2:
            raise ValueError("Debe incluir nombre y apellido")
        return v.strip().title()

    @field_validator("departamento")
    @classmethod
    def normalizar_departamento(cls, v: str) -> str:
        return v.strip().lower()

    @field_validator("especialidad")
    @classmethod
    def normalizar_especialidad(cls, v: str) -> str:
        return v.strip().lower()


# ─────────────────────────────────────────
# CREATE
# ─────────────────────────────────────────
class ProfesorCreate(ProfesorBase):
    pass


# ─────────────────────────────────────────
# RESPONSE
# ─────────────────────────────────────────
class ProfesorResponse(ProfesorBase):
    id: int
    activo: bool
    fecha_registro: datetime

    model_config = {"from_attributes": True}


# ─────────────────────────────────────────
# UPDATE: para PATCH (todo es opcional)
# ─────────────────────────────────────────
class ProfesorUpdate(BaseModel):
    nombre: Optional[str] = Field(None, min_length=3, max_length=100)
    email: Optional[EmailStr] = None
    departamento: Optional[str] = Field(None, min_length=3, max_length=50)
    especialidad: Optional[str] = Field(None, min_length=3, max_length=100)
    telefono: Optional[str] = Field(None, pattern=r"^\d{10}$")
    activo: Optional[bool] = None

    @field_validator("nombre")
    @classmethod
    def validar_nombre(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            if any(char.isdigit() for char in v):
                raise ValueError("El nombre no puede contener números")
            if len(v.split()) < 2:
                raise ValueError("Debe incluir nombre y apellido")
            return v.strip().title()
        return v

    @field_validator("departamento")
    @classmethod
    def normalizar_departamento(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            return v.strip().lower()
        return v

    @field_validator("especialidad")
    @classmethod
    def normalizar_especialidad(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            return v.strip().lower()
        return v
