from __future__ import annotations
import json
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from app.core.config import HealthStatus, get_settings
from app.data.demo_dataset import get_data_sources, get_demo_match, get_demo_matches
from app.domain.schemas import ModelMetric, PredictionRequest, PredictionRun
from app.services.prediction_engine import build_idempotency_key, stream_prediction
from app.services.prediction_store import prediction_store

router = APIRouter()


@router.get("/system/health", response_model=HealthStatus)
def health() -> HealthStatus:
    settings = get_settings()
    return HealthStatus(
        status="ok",
        app=settings.app_name,
        environment=settings.environment,
        demo_mode=settings.demo_mode,
        model_version=settings.model_version,
    )


@router.get("/matches")
def list_matches(group: str | None = None, phase: str | None = None, team: str | None = None):
    matches = get_demo_matches()
    if group:
        matches = [match for match in matches if match.group == group]
    if phase:
        matches = [match for match in matches if match.phase == phase]
    if team:
        normalized = team.lower()
        matches = [
            match
            for match in matches
            if normalized in match.home_team.name.lower()
            or normalized in match.away_team.name.lower()
            or normalized in match.home_team.code.lower()
            or normalized in match.away_team.code.lower()
        ]
    return {"items": matches, "demo_mode": True}


@router.get("/matches/{match_id}")
def get_match(match_id: str):
    match = get_demo_match(match_id)
    if match is None:
        raise HTTPException(status_code=404, detail="Match not found")
    return match


@router.post("/matches/{match_id}/predictions", response_model=PredictionRun)
def create_prediction(match_id: str, payload: PredictionRequest):
    settings = get_settings()
    match = get_demo_match(match_id)
    if match is None:
        raise HTTPException(status_code=404, detail="Match not found")
    seed = payload.seed if payload.seed is not None else settings.default_seed
    key = build_idempotency_key(match, settings, seed, payload.simulations)
    existing = prediction_store.get_by_key(key)
    if existing is not None:
        return existing
    prediction_id = key[:16]
    run = PredictionRun(prediction_id=prediction_id, match_id=match.id, status="queued", idempotency_key=key, seed=seed, simulations=payload.simulations)
    return prediction_store.upsert(run)


@router.get("/predictions/{prediction_id}", response_model=PredictionRun)
def get_prediction(prediction_id: str):
    run = prediction_store.get_by_id(prediction_id)
    if run is None:
        raise HTTPException(status_code=404, detail="Prediction not found")
    return run


@router.get("/predictions/{prediction_id}/explanation")
def get_prediction_explanation(prediction_id: str):
    run = prediction_store.get_by_id(prediction_id)
    if run is None:
        raise HTTPException(status_code=404, detail="Prediction not found")
    if run.result is None:
        return {"status": run.status, "message": "La explicación estará disponible al completar la simulación."}
    return {
        "prediction_id": prediction_id,
        "executive_summary": run.result.executive_summary,
        "factors": run.result.factors,
        "disclaimer": run.result.disclaimer,
    }


@router.get("/predictions/{prediction_id}/stream")
async def prediction_events(prediction_id: str):
    settings = get_settings()
    run = prediction_store.get_by_id(prediction_id)
    if run is None:
        raise HTTPException(status_code=404, detail="Prediction not found")
    match = get_demo_match(run.match_id)
    if match is None:
        raise HTTPException(status_code=404, detail="Match not found")
    if run.result is not None:
        async def completed():
            payload = {"step": "Predicción completada", "status": "completed", "progress": 100, "message": "Resultado recuperado de memoria.", "result": run.result.model_dump(mode="json")}
            yield f"event: prediction\n"
            yield f"data: {json.dumps(payload, ensure_ascii=False)}\n\n"
        return StreamingResponse(completed(), media_type="text/event-stream")

    async def event_generator():
        run.status = "running"
        prediction_store.upsert(run)
        async for event in stream_prediction(match, settings, seed=run.seed, simulations=run.simulations):
            payload = event.model_dump(mode="json")
            if event.result is not None:
                run.status = "completed"
                run.result = event.result
                prediction_store.upsert(run)
            yield "event: prediction\n"
            yield f"data: {json.dumps(payload, ensure_ascii=False)}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")


@router.get("/models")
def list_models():
    settings = get_settings()
    return {
        "items": [
            {
                "version": settings.model_version,
                "mode": "demo",
                "components": ["Elo + forma", "Scouting titulares/xG", "Poisson", "Modelo B bayesiano", "Monte Carlo", "Markov/Bellman"],
                "calibration_status": "demo_scouting_calibrated",
            }
        ]
    }


@router.get("/models/metrics", response_model=list[ModelMetric])
def model_metrics():
    return [
        ModelMetric(name="Accuracy", value=None, split="test", status="not_available_demo_mode", note="Requiere backtesting temporal con datos históricos reales."),
        ModelMetric(name="Brier Score", value=None, split="test", status="not_available_demo_mode", note="No se reporta como real en modo demo."),
        ModelMetric(name="Log Loss", value=None, split="test", status="not_available_demo_mode", note="Pendiente de validación walk-forward."),
        ModelMetric(name="Expected Calibration Error", value=None, split="test", status="not_available_demo_mode", note="No existe muestra suficiente para alta confianza."),
    ]


@router.get("/data-sources/status")
def data_sources_status():
    return {"items": get_data_sources(), "demo_mode": True}
