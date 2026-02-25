from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from database import get_db
from models.models import Proyecto, Torre, TipoPlantilla, Usuario, RolUsuario
from schemas.inmob_schemas import ProyectoCreate, ProyectoOut, TorreCreate, TorreOut, TipoPlantillaCreate, TipoPlantillaOut, PisoCreate, PisoOut, TipoPlantillaUpdate, TorreConPisosOut
from routers.auth_router import get_current_user
import uuid
from models.models import Piso


router = APIRouter(prefix="/proyectos", tags=["Proyectos"])

@router.get("/", response_model=List[ProyectoOut])
def get_proyectos(db: Session = Depends(get_db), current_user: Usuario = Depends(get_current_user)):
    return db.query(Proyecto).all()

@router.post("/", response_model=ProyectoOut)
def create_proyecto(proyecto: ProyectoCreate, db: Session = Depends(get_db), current_user: Usuario = Depends(get_current_user)):
    if current_user.rol not in [RolUsuario.super_admin, RolUsuario.admin]:
        raise HTTPException(status_code=403, detail="No tienes permisos para crear proyectos")
    
    new_proyecto = Proyecto(**proyecto.model_dump())
    db.add(new_proyecto)
    db.commit()
    db.refresh(new_proyecto)
    return new_proyecto

@router.get("/{proyecto_id}", response_model=ProyectoOut)
def get_proyecto(proyecto_id: uuid.UUID, db: Session = Depends(get_db), current_user: Usuario = Depends(get_current_user)):
    proyecto = db.query(Proyecto).filter(Proyecto.id == proyecto_id).first()
    if not proyecto:
        raise HTTPException(status_code=404, detail="Proyecto no encontrado")
    return proyecto

@router.post("/{proyecto_id}/torres", response_model=TorreOut)
def create_torre(proyecto_id: uuid.UUID, torre: TorreCreate, db: Session = Depends(get_db), current_user: Usuario = Depends(get_current_user)):
    if current_user.rol not in [RolUsuario.super_admin, RolUsuario.admin]:
        raise HTTPException(status_code=403, detail="No tienes permisos para crear torres")
    
    proyecto = db.query(Proyecto).filter(Proyecto.id == proyecto_id).first()
    if not proyecto:
        raise HTTPException(status_code=404, detail="Proyecto no encontrado")
        
    new_torre = Torre(nombre=torre.nombre, numero_pisos=torre.numero_pisos, proyecto_id=proyecto_id)
    db.add(new_torre)
    db.commit()
    db.refresh(new_torre)
    return new_torre

@router.post("/{proyecto_id}/tipos", response_model=TipoPlantillaOut)
def create_tipo_plantilla(proyecto_id: uuid.UUID, tipo: TipoPlantillaCreate, db: Session = Depends(get_db), current_user: Usuario = Depends(get_current_user)):
    if current_user.rol not in [RolUsuario.super_admin, RolUsuario.admin]:
        raise HTTPException(status_code=403, detail="No tienes permisos para crear tipos de apartamento")
    
    proyecto = db.query(Proyecto).filter(Proyecto.id == proyecto_id).first()
    if not proyecto:
        raise HTTPException(status_code=404, detail="Proyecto no encontrado")
        
    new_tipo = TipoPlantilla(**tipo.model_dump(), proyecto_id=proyecto_id)
    db.add(new_tipo)
    db.commit()
    db.refresh(new_tipo)
@router.get("/{proyecto_id}/torres/{torre_id}", response_model=TorreConPisosOut)
def get_torre(proyecto_id: uuid.UUID, torre_id: uuid.UUID, db: Session = Depends(get_db), current_user: Usuario = Depends(get_current_user)):
    torre = db.query(Torre).filter(Torre.id == torre_id, Torre.proyecto_id == proyecto_id).first()
    if not torre:
        raise HTTPException(status_code=404, detail="Torre no encontrada")
    return torre

@router.post("/{proyecto_id}/torres/{torre_id}/pisos", response_model=PisoOut)
def create_piso(proyecto_id: uuid.UUID, torre_id: uuid.UUID, piso: PisoCreate, db: Session = Depends(get_db), current_user: Usuario = Depends(get_current_user)):
    if current_user.rol not in [RolUsuario.super_admin, RolUsuario.admin]:
        raise HTTPException(status_code=403, detail="No tienes permisos para crear pisos")
    
    torre = db.query(Torre).filter(Torre.id == torre_id, Torre.proyecto_id == proyecto_id).first()
    if not torre:
        raise HTTPException(status_code=404, detail="Torre no encontrada")
        
    # Calculate bounds from input
    cantidad_aptos = sum(apto_tipo.cantidad for apto_tipo in piso.apartamentos_tipos)
    
    new_piso = Piso(numero_nivel=piso.numero_nivel, cantidad_aptos=cantidad_aptos, torre_id=torre_id)
    db.add(new_piso)
    
    # Update Torre total
    torre.numero_aptos += cantidad_aptos
    
    db.flush() # flush to get new_piso.id
    
    from models.models import Apartamento
    for apto_tipo in piso.apartamentos_tipos:
        for _ in range(apto_tipo.cantidad):
            db.add(Apartamento(
                precio=0.0,
                tipo_id=apto_tipo.tipo_id,
                piso_id=new_piso.id
            ))
            
    db.commit()
    db.refresh(new_piso)
    return new_piso

@router.put("/{proyecto_id}/tipos/{tipo_id}", response_model=TipoPlantillaOut)
def update_tipo_plantilla(proyecto_id: uuid.UUID, tipo_id: uuid.UUID, data: TipoPlantillaUpdate, db: Session = Depends(get_db), current_user: Usuario = Depends(get_current_user)):
    if current_user.rol not in [RolUsuario.super_admin, RolUsuario.admin]:
        raise HTTPException(status_code=403, detail="No tienes permisos para editar tipos de apartamento")
        
    tipo = db.query(TipoPlantilla).filter(TipoPlantilla.id == tipo_id, TipoPlantilla.proyecto_id == proyecto_id).first()
    if not tipo:
        raise HTTPException(status_code=404, detail="Tipo de apartamento no encontrado")
        
    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(tipo, key, value)
        
    db.commit()
    db.refresh(tipo)
    return tipo

@router.delete("/{proyecto_id}/tipos/{tipo_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_tipo_plantilla(proyecto_id: uuid.UUID, tipo_id: uuid.UUID, db: Session = Depends(get_db), current_user: Usuario = Depends(get_current_user)):
    if current_user.rol not in [RolUsuario.super_admin, RolUsuario.admin]:
        raise HTTPException(status_code=403, detail="No tienes permisos para eliminar tipos de apartamento")
        
    tipo = db.query(TipoPlantilla).filter(TipoPlantilla.id == tipo_id, TipoPlantilla.proyecto_id == proyecto_id).first()
    if not tipo:
        raise HTTPException(status_code=404, detail="Tipo de apartamento no encontrado")
        
    from models.models import Apartamento
    aptos_usando_tipo = db.query(Apartamento).filter(Apartamento.tipo_id == tipo_id).count()
    if aptos_usando_tipo > 0:
        raise HTTPException(status_code=400, detail="No procesable: Hay apartamentos existentes que utilizan este Tipo de Plantilla. Bórrelos primero.")
        
    db.delete(tipo)
    db.commit()
    return None

@router.delete("/{proyecto_id}/torres/{torre_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_torre(proyecto_id: uuid.UUID, torre_id: uuid.UUID, db: Session = Depends(get_db), current_user: Usuario = Depends(get_current_user)):
    if current_user.rol not in [RolUsuario.super_admin, RolUsuario.admin]:
        raise HTTPException(status_code=403, detail="No tienes permisos para eliminar torres")
        
    torre = db.query(Torre).filter(Torre.id == torre_id, Torre.proyecto_id == proyecto_id).first()
    if not torre:
        raise HTTPException(status_code=404, detail="Torre no encontrada")
        
    db.delete(torre)
    db.commit()
    return None

@router.delete("/{proyecto_id}/torres/{torre_id}/pisos/{piso_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_piso(proyecto_id: uuid.UUID, torre_id: uuid.UUID, piso_id: uuid.UUID, db: Session = Depends(get_db), current_user: Usuario = Depends(get_current_user)):
    if current_user.rol not in [RolUsuario.super_admin, RolUsuario.admin]:
        raise HTTPException(status_code=403, detail="No tienes permisos para eliminar pisos")
        
    torre = db.query(Torre).filter(Torre.id == torre_id, Torre.proyecto_id == proyecto_id).first()
    if not torre:
        raise HTTPException(status_code=404, detail="Torre no encontrada")
        
    piso = db.query(Piso).filter(Piso.id == piso_id, Piso.torre_id == torre_id).first()
    if not piso:
        raise HTTPException(status_code=404, detail="Piso no encontrado")
        
    # We must explicitly subtract this floor's capacity from the Tower total
    torre.numero_aptos = max(0, torre.numero_aptos - piso.cantidad_aptos)
    
    db.delete(piso)
    db.commit()
    return None
