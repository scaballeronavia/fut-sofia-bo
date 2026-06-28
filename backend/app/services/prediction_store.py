from app.domain.schemas import PredictionRun


class PredictionStore:
    def __init__(self) -> None:
        self._by_id: dict[str, PredictionRun] = {}
        self._by_key: dict[str, str] = {}

    def get_by_id(self, prediction_id: str) -> PredictionRun | None:
        return self._by_id.get(prediction_id)

    def get_by_key(self, key: str) -> PredictionRun | None:
        prediction_id = self._by_key.get(key)
        if prediction_id is None:
            return None
        return self._by_id.get(prediction_id)

    def upsert(self, run: PredictionRun) -> PredictionRun:
        self._by_id[run.prediction_id] = run
        self._by_key[run.idempotency_key] = run.prediction_id
        return run


prediction_store = PredictionStore()
