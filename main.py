from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import engine, Base

# Base.metadata.create_all(bind=engine) # Se utilizará Alembic mejor

app = FastAPI(title="SaaS Inmobiliario", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from routers import auth_router, proyectos_router, apartamentos_router, rrhh_router

app.include_router(auth_router.router)
app.include_router(proyectos_router.router)
app.include_router(apartamentos_router.router)
app.include_router(rrhh_router.router)

@app.get("/")
def read_root():
    return {"message": "API Backend SaaS Inmobiliario funcionando"}
