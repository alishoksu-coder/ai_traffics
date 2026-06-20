import asyncio
import subprocess
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.database import get_conn
from app.seed import (
    seed_locations_astana_if_empty,
    seed_segments_if_empty,
    seed_admin_if_empty,
    seed_history_if_empty,
)
from app.services.simulation_service import sim
from app.vehicles import veh_sim

from app.routers import traffic_router, routing_router, social_router, admin_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("[STARTUP] Zapusk AI Traffic Backend...")
    conn = get_conn(settings.db_path)
    try:
        seed_locations_astana_if_empty(conn)
        seed_segments_if_empty(conn)
        seed_admin_if_empty(conn)
        seed_history_if_empty(conn, sim, minutes=43200)
    finally:
        conn.close()

    print("[STARTUP] Zapusk simulyatora traffika i transporta...")
    sim.start()
    veh_sim.start()
    
    print("[STARTUP] Zapusk AI Worker (background process)...")
    import sys
    worker_process = subprocess.Popen([sys.executable, "-m", "app.ai_worker"])
    
    yield

    print("[SHUTDOWN] Ostanovka servisov...")
    sim.stop()
    veh_sim.stop()
    if worker_process:
        worker_process.terminate()
        worker_process.wait()

app = FastAPI(
    title="AI Traffic Forecast API",
    description="Backend для прогноза пробок в Астане",
    version="2.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(traffic_router.router)
app.include_router(routing_router.router)
app.include_router(social_router.router)
app.include_router(admin_router.router)

@app.get("/")
def root():
    return {"status": "ok", "message": "AI Traffic Backend is running (Clean Architecture)"}
