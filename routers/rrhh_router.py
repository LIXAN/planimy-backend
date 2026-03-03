from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from database import get_db
from models.models import Empleado, Usuario, RolUsuario
from schemas.rrhh_schemas import EmpleadoCreate, EmpleadoUpdate, EmpleadoOut
from routers.auth_router import get_current_user

router = APIRouter(prefix="/rrhh", tags=["RRHH"])

@router.get("/empleados", response_model=List[EmpleadoOut])
def get_empleados(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Obtiene la lista de todos los empleados."""
    empleados = db.query(Empleado).order_by(Empleado.created_at.desc()).offset(skip).limit(limit).all()
    return empleados

@router.post("/empleados", response_model=EmpleadoOut, status_code=status.HTTP_201_CREATED)
def create_empleado(
    empleado_in: EmpleadoCreate, 
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Crea un nuevo empleado."""
    if current_user.rol not in [RolUsuario.super_admin, RolUsuario.admin]:
        raise HTTPException(status_code=403, detail="No tienes permisos para crear empleados")

    nuevo_empleado = Empleado(**empleado_in.model_dump())
    db.add(nuevo_empleado)
    db.commit()
    db.refresh(nuevo_empleado)
    return nuevo_empleado

@router.put("/empleados/{empleado_id}", response_model=EmpleadoOut)
def update_empleado(
    empleado_id: UUID,
    empleado_in: EmpleadoUpdate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Actualiza la información de un empleado existente."""
    if current_user.rol not in [RolUsuario.super_admin, RolUsuario.admin]:
        raise HTTPException(status_code=403, detail="No tienes permisos para editar empleados")

    empleado_db = db.query(Empleado).filter(Empleado.id == empleado_id).first()
    if not empleado_db:
        raise HTTPException(status_code=404, detail="Empleado no encontrado")

    update_data = empleado_in.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(empleado_db, key, value)

    db.commit()
    db.refresh(empleado_db)
    return empleado_db

@router.delete("/empleados/{empleado_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_empleado(
    empleado_id: UUID,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Elimina permanentemente un empleado."""
    if current_user.rol not in [RolUsuario.super_admin]:
        raise HTTPException(status_code=403, detail="Solo los super_admin pueden eliminar empleados permanentemente")

    empleado_db = db.query(Empleado).filter(Empleado.id == empleado_id).first()
    if not empleado_db:
        raise HTTPException(status_code=404, detail="Empleado no encontrado")

    db.delete(empleado_db)
    db.commit()
