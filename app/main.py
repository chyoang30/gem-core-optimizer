from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from app.routers import gems, cores, optimize

app = FastAPI(
    title="젬 최적화 API",
    description="MMORPG 코어 젬 배치를 최적화하는 RESTful API",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(gems.router, prefix="/api/gems", tags=["젬 관리"])
app.include_router(cores.router, prefix="/api/cores", tags=["코어 관리"])
app.include_router(optimize.router, prefix="/api/optimize", tags=["최적화"])

app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/", include_in_schema=False)
def serve_frontend():
    return FileResponse("static/index.html")
