import os
import sys

# Add the current directory to the sys path so we can import from backend-fastapi correctly
sys.path.append(os.getcwd())

from database import SessionLocal
from models.models import Proyecto, Torre, Piso, Apartamento, TipoPlantilla

def delete_test_projects():
    db = SessionLocal()
    nombres_a_borrar = ["Proyecto Zonas", "Proyecto Test API", "Proyecto Test CLI"]
    
    try:
        proyectos = db.query(Proyecto).filter(Proyecto.nombre.in_(nombres_a_borrar)).all()
        proyecto_ids = [p.id for p in proyectos]
        
        print(f"Borrando proyectos con IDs: {proyecto_ids}")
        
        if proyecto_ids:
            # Delete dependent records first to avoid foreign key constraint errors
            db.query(Apartamento).filter(Apartamento.piso.has(Piso.torre.has(Torre.proyecto_id.in_(proyecto_ids)))).delete(synchronize_session=False)
            db.query(Piso).filter(Piso.torre.has(Torre.proyecto_id.in_(proyecto_ids))).delete(synchronize_session=False)
            db.query(Torre).filter(Torre.proyecto_id.in_(proyecto_ids)).delete(synchronize_session=False)
            db.query(TipoPlantilla).filter(TipoPlantilla.proyecto_id.in_(proyecto_ids)).delete(synchronize_session=False)
            
            # Finally delete the projects
            db.query(Proyecto).filter(Proyecto.id.in_(proyecto_ids)).delete(synchronize_session=False)
            
            db.commit()
            print("Proyectos test borrados exitosamente.")
        else:
            print("No se encontraron los proyectos test.")
    except Exception as e:
        print(f"Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    delete_test_projects()
