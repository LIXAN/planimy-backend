from pydantic import BaseModel, ConfigDict
from typing import Optional
from uuid import UUID
from datetime import datetime, date
from models.models import EstadoEmpleado

class EmpleadoBase(BaseModel):
    nombre_completo: str
    documento_identidad: Optional[str] = None
    cargo: str
    telefono: Optional[str] = None
    fecha_contratacion: Optional[date] = None
    salario: Optional[float] = None
    estado: EstadoEmpleado = EstadoEmpleado.activo
    usuario_id: Optional[UUID] = None

class EmpleadoCreate(EmpleadoBase):
    pass

class EmpleadoUpdate(BaseModel):
    nombre_completo: Optional[str] = None
    documento_identidad: Optional[str] = None
    cargo: Optional[str] = None
    telefono: Optional[str] = None
    fecha_contratacion: Optional[date] = None
    salario: Optional[float] = None
    estado: Optional[EstadoEmpleado] = None
    usuario_id: Optional[UUID] = None

class EmpleadoOut(EmpleadoBase):
    id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
