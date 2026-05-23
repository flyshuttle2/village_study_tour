"""FastAPI Web 服务入口"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
import uvicorn

from config import OUTPUT_DIR
from models.input_schema import VillageInput
from output_coordinator import OutputCoordinator

app = FastAPI(title="乡村文旅研学解决方案生成器", version="1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class GenerateRequest(BaseModel):
    name: str
    province: str
    city: str
    county: str
    township: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    images: Optional[List[str]] = []
    videos: Optional[List[str]] = []
    custom_tags: Optional[List[str]] = []


@app.get("/")
async def root():
    return {"message": "乡村文旅研学解决方案生成器 v1.0", "docs": "/docs"}


@app.post("/generate")
async def generate(request: GenerateRequest):
    try:
        village = VillageInput(**request.model_dump())
        coordinator = OutputCoordinator()
        results = coordinator.run_full_pipeline(village)
        return {"status": "success", "data": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/output/{village_name}")
async def list_outputs(village_name: str):
    village_dir = OUTPUT_DIR / village_name
    if not village_dir.exists():
        raise HTTPException(status_code=404, detail="村庄不存在")
    files = list(village_dir.glob("*"))
    return {"village": village_name, "files": [f.name for f in files]}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
