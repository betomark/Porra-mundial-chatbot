import os
from fastapi import FastAPI, BackgroundTasks, HTTPException, Query
from pydantic import BaseModel
from utils.mongo_client import MongoDBClient
from porra.gemini import gemini as Gemini
from porra.world_cup_extractor import run_extractor

app = FastAPI(
    title="World Cup Pool API",
    description="REST service for extracting data and generating sports predictions.",
    version="0.1.0"
)

mongo = MongoDBClient()


class PredictRequest(BaseModel):
    """Request schema for prediction API calls."""
    event_id: str
    team_a_id: str
    team_b_id: str
    api_key: str | None = None
    model: str | None = None


class ExtractRequest(BaseModel):
    """Request schema for extractor API calls."""
    headless: bool = True


@app.get("/health")
def health():
    """Return the application health and MongoDB connectivity status."""
    try:
        mongo.client.admin.command("ping")
        return {"status": "ok", "mongo": True}
    except Exception as exc:
        return {"status": "error", "mongo": False, "detail": str(exc)}


@app.get("/collections")
def list_collections():
    """Return the list of MongoDB collections in the configured database."""
    collections = mongo.database.list_collection_names()
    return {"collections": collections}


def serialize_document(document: dict) -> dict:
    """Serialize MongoDB document IDs into JSON-safe strings."""
    if "_id" in document:
        try:
            document["_id"] = str(document["_id"])
        except Exception:
            document["_id"] = repr(document["_id"])
    return document


@app.get("/documents")
def get_documents(
    collection: str = Query(..., description="MongoDB collection name"),
    field: str | None = Query(None, description="Optional field name to filter by"),
    value: str | None = Query(None, description="Optional field value to filter by"),
    limit: int = Query(50, ge=1, le=1000, description="Maximum number of documents to return")
):
    """Return documents from a MongoDB collection, optionally filtered by field."""
    if field is not None and value is None:
        raise HTTPException(status_code=400, detail="A value is required when filtering by field")

    query = {}
    if field is not None and value is not None:
        query[field] = value

    documents = mongo.find_many(collection, query=query, limit=limit)
    return {
        "collection": collection,
        "query": query,
        "documents": [serialize_document(doc) for doc in documents],
    }


@app.post("/extract")
def extract(request: ExtractRequest, background_tasks: BackgroundTasks):
    """Queue the extraction pipeline in a background task."""
    os.environ["HEADLESS"] = "true" if request.headless else "false"
    background_tasks.add_task(run_extractor)
    return {"status": "queued", "headless": request.headless}


@app.post("/predict")
def predict(request: PredictRequest):
    """Generate a match prediction using the Gemini predictor."""
    if request.api_key:
        # Override only for this request
        predictor = Gemini(api_key=request.api_key, model=request.model)
    else:
        predictor = Gemini(model=request.model)

    result = predictor.generate_prediction(request.event_id, request.team_a_id, request.team_b_id)
    return {"prediction": result}
