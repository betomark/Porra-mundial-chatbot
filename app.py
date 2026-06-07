import os
from fastapi import FastAPI, BackgroundTasks
from pydantic import BaseModel
from utils.mongo_client import MongoDBClient
from porra.gemini import gemini as Gemini
from porra.world_cup_extractor import run_extractor

app = FastAPI(
    title="Porra Mundial API",
    description="Servicio REST para extracción de datos y generación de predicciones deportivas.",
    version="0.1.0"
)

mongo = MongoDBClient()


class PredictRequest(BaseModel):
    event_id: str
    team_a_id: str
    team_b_id: str
    api_key: str | None = None
    model: str | None = None


class ExtractRequest(BaseModel):
    headless: bool = True


@app.get("/health")
def health():
    try:
        mongo.client.admin.command("ping")
        return {"status": "ok", "mongo": True}
    except Exception as exc:
        return {"status": "error", "mongo": False, "detail": str(exc)}


@app.get("/collections")
def list_collections():
    collections = mongo.database.list_collection_names()
    return {"collections": collections}


@app.post("/extract")
def extract(request: ExtractRequest, background_tasks: BackgroundTasks):
    os.environ["HEADLESS"] = "true" if request.headless else "false"
    background_tasks.add_task(run_extractor)
    return {"status": "queued", "headless": request.headless}


@app.post("/predict")
def predict(request: PredictRequest):
    if request.api_key:
        # Override only for this request
        predictor = Gemini(api_key=request.api_key, model=request.model)
    else:
        predictor = Gemini(model=request.model)

    result = predictor.generate_prediction(request.event_id, request.team_a_id, request.team_b_id)
    return {"prediction": result}
