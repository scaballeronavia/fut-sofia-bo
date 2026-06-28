from __future__ import annotations
from datetime import datetime
from typing import Literal
from pydantic import BaseModel, Field


ConfidenceLabel = Literal["alta", "media", "baja"]
MatchStatus = Literal["scheduled", "in_progress", "finished"]
PredictionOutcome = Literal["home", "draw", "away"]


class Team(BaseModel):
    id: str
    name: str
    code: str
    flag: str
    confederation: str
    elo: float
    attack_strength: float
    defense_strength: float
    recent_form: float


class Venue(BaseModel):
    city: str
    country: str
    stadium: str | None = None
    altitude_m: int | None = None


class DataFreshness(BaseModel):
    label: str
    source_mode: Literal["demo", "external"]
    last_updated: datetime
    cutoff: datetime
    warnings: list[str] = Field(default_factory=list)


class Match(BaseModel):
    id: str
    home_team: Team
    away_team: Team
    kickoff: datetime
    venue: Venue
    group: str | None = None
    phase: str
    status: MatchStatus
    knockout: bool = False
    data_freshness: DataFreshness


class PredictionRequest(BaseModel):
    simulations: int = Field(default=50_000, ge=1_000, le=100_000)
    seed: int | None = None


class ProbabilitySet(BaseModel):
    home_win: float
    draw: float
    away_win: float


class ScoreProbability(BaseModel):
    score: str
    probability: float


class FactorContribution(BaseModel):
    name: str
    impact: float
    direction: Literal["home", "away", "neutral"]
    evidence: str


class ModelComponent(BaseModel):
    name: str
    weight: float
    status: str
    note: str


class PredictionResult(BaseModel):
    prediction_id: str
    match_id: str
    generated_at: datetime
    model_version: str
    data_cutoff: datetime
    seed: int
    simulations: int
    primary_outcome: PredictionOutcome
    probabilities: ProbabilitySet
    most_likely_score: str
    score_distribution: list[ScoreProbability]
    expected_goals_home: float
    expected_goals_away: float
    confidence: ConfidenceLabel
    confidence_note: str
    uncertainty_interval: str
    qualification_probability_home: float | None = None
    qualification_probability_away: float | None = None
    extra_time_probability: float | None = None
    penalties_probability: float | None = None
    factors: list[FactorContribution]
    model_components: list[ModelComponent]
    executive_summary: str
    disclaimer: str


class PredictionRun(BaseModel):
    prediction_id: str
    match_id: str
    status: Literal["queued", "running", "completed", "failed"]
    idempotency_key: str
    seed: int
    simulations: int
    result: PredictionResult | None = None


class DataSourceStatus(BaseModel):
    id: str
    name: str
    status: Literal["healthy", "degraded", "offline"]
    mode: Literal["demo", "external"]
    last_updated: datetime
    message: str


class ModelMetric(BaseModel):
    name: str
    value: float | None
    split: str
    status: str
    note: str


class StreamEvent(BaseModel):
    step: str
    status: Literal["running", "completed"]
    progress: int
    message: str
    result: PredictionResult | None = None
