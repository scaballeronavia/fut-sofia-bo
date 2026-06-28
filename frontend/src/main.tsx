import React from "react";
import ReactDOM from "react-dom/client";
import { Activity, CalendarDays, ChevronDown, Database, Eye, Play, ShieldCheck, Sparkles, ThumbsDown, ThumbsUp } from "lucide-react";
import "./styles.css";
import { staticMatches, staticPredictions, staticSources } from "./staticData";

const API_BASE = import.meta.env.VITE_API_BASE ?? "/api/v1";
const STATIC_MODE = import.meta.env.VITE_STATIC_MODE === "true";

type Team = {
  id: string;
  name: string;
  code: string;
  flag: string;
  confederation: string;
};

type Match = {
  id: string;
  home_team: Team;
  away_team: Team;
  kickoff: string;
  venue: { city: string; country: string; stadium?: string; altitude_m?: number };
  group?: string;
  phase: string;
  status: string;
  knockout: boolean;
  data_freshness: {
    label: string;
    source_mode: "demo" | "external";
    last_updated: string;
    warnings: string[];
  };
};

type PredictionResult = {
  prediction_id: string;
  match_id: string;
  generated_at: string;
  model_version: string;
  data_cutoff: string;
  seed: number;
  simulations: number;
  primary_outcome: "home" | "draw" | "away";
  probabilities: { home_win: number; draw: number; away_win: number };
  most_likely_score: string;
  score_distribution: { score: string; probability: number }[];
  expected_goals_home: number;
  expected_goals_away: number;
  confidence: string;
  confidence_note: string;
  uncertainty_interval: string;
  qualification_probability_home?: number;
  qualification_probability_away?: number;
  extra_time_probability?: number;
  penalties_probability?: number;
  factors: { name: string; impact: number; direction: string; evidence: string }[];
  model_components: { name: string; weight: number; status: string; note: string }[];
  executive_summary: string;
  disclaimer: string;
};

type SourceStatus = {
  id: string;
  name: string;
  status: string;
  mode: string;
  last_updated: string;
  message: string;
};

type ProgressEvent = {
  step: string;
  status: "running" | "completed";
  progress: number;
  message: string;
  result?: PredictionResult;
};

function formatDate(value: string) {
  return new Intl.DateTimeFormat("es-BO", {
    dateStyle: "medium",
    timeStyle: "short"
  }).format(new Date(value));
}

function dateKey(value: string | Date) {
  return new Intl.DateTimeFormat("en-CA", {
    timeZone: "America/La_Paz",
    year: "numeric",
    month: "2-digit",
    day: "2-digit"
  }).format(typeof value === "string" ? new Date(value) : value);
}

const TODAY_KEY = dateKey(new Date());

function App() {
  const [matches, setMatches] = React.useState<Match[]>([]);
  const [sources, setSources] = React.useState<SourceStatus[]>([]);
  const [selectedPhase, setSelectedPhase] = React.useState("Todas");
  const [teamFilter, setTeamFilter] = React.useState("");
  const [selectedDate, setSelectedDate] = React.useState(TODAY_KEY);
  const [showFutureMatches, setShowFutureMatches] = React.useState(false);
  const [activeMatch, setActiveMatch] = React.useState<string | null>(null);

  React.useEffect(() => {
    let cancelled = false;
    let retryTimer: number | undefined;

    function loadData() {
      if (STATIC_MODE) {
        setMatches(staticMatches as Match[]);
        setSources(staticSources as SourceStatus[]);
        return;
      }

      Promise.all([
        fetch(`${API_BASE}/matches`).then((response) => response.json()),
        fetch(`${API_BASE}/data-sources/status`).then((response) => response.json())
      ])
        .then(([matchPayload, sourcePayload]) => {
          if (cancelled) return;
          setMatches(matchPayload.items);
          setSources(sourcePayload.items);
        })
        .catch(() => {
          if (cancelled) return;
          retryTimer = window.setTimeout(loadData, 1500);
        });
    }

    loadData();
    return () => {
      cancelled = true;
      if (retryTimer) window.clearTimeout(retryTimer);
    };
  }, []);

  const phases = ["Todas", ...Array.from(new Set(matches.map((match) => match.phase)))];
  const todayMatchesCount = matches.filter((match) => dateKey(match.kickoff) === TODAY_KEY).length;
  const futureMatchesCount = matches.filter((match) => dateKey(match.kickoff) >= TODAY_KEY).length;
  const filteredMatches = matches.filter((match) => {
    const phaseOk = selectedPhase === "Todas" || match.phase === selectedPhase;
    const text = `${match.home_team.name} ${match.away_team.name} ${match.home_team.code} ${match.away_team.code}`.toLowerCase();
    const teamOk = text.includes(teamFilter.toLowerCase());
    const matchDate = dateKey(match.kickoff);
    const dateOk = showFutureMatches ? matchDate >= TODAY_KEY : matchDate === selectedDate;
    return phaseOk && teamOk && dateOk;
  });
  const visibleMatches = activeMatch ? matches.filter((match) => match.id === activeMatch) : filteredMatches;

  return (
    <main>
      <PlanetaryBackground />
      <AppHeader sources={sources} />
      <section className="workspace" aria-label="Panel principal de Sof-IA BO">
        <DemoModeBanner />
        <TournamentFilters
          phases={phases}
          selectedPhase={selectedPhase}
          onPhaseChange={setSelectedPhase}
          teamFilter={teamFilter}
          onTeamFilterChange={setTeamFilter}
          selectedDate={selectedDate}
          onDateChange={(value) => {
            setSelectedDate(value);
            setShowFutureMatches(false);
            setActiveMatch(null);
          }}
          showFutureMatches={showFutureMatches}
          onToggleFutureMatches={() => {
            setShowFutureMatches((current) => !current);
            setActiveMatch(null);
          }}
          todayMatchesCount={todayMatchesCount}
          futureMatchesCount={futureMatchesCount}
        />
        <div className="content-grid">
          <section className="match-list" aria-label="Partidos">
            {activeMatch ? (
              <button className="show-all-button" onClick={() => setActiveMatch(null)}>
                Mostrar todos los partidos
              </button>
            ) : null}
            {visibleMatches.length === 0 ? <EmptyState /> : null}
            {visibleMatches.map((match) => (
              <MatchCard
                key={match.id}
                match={match}
                expanded={activeMatch === match.id}
                onToggle={() => setActiveMatch(activeMatch === match.id ? null : match.id)}
              />
            ))}
          </section>
          <aside className="insight-rail" aria-label="Metodología">
            <SystemFlowchart />
          </aside>
        </div>
      </section>
      <CommunityFooter />
    </main>
  );
}


function readStoredNumber(key: string, fallback: number) {
  const raw = window.localStorage.getItem(key);
  if (raw === null) return fallback;
  const parsed = Number.parseInt(raw, 10);
  return Number.isFinite(parsed) ? parsed : fallback;
}

function useAnimatedNumber(value: number) {
  const [displayValue, setDisplayValue] = React.useState(value);

  React.useEffect(() => {
    const start = displayValue;
    const distance = value - start;
    if (distance === 0) return;

    const startedAt = performance.now();
    const duration = 720;
    let frame = 0;

    function tick(now: number) {
      const progress = Math.min(1, (now - startedAt) / duration);
      const eased = 1 - Math.pow(1 - progress, 3);
      setDisplayValue(Math.round(start + distance * eased));
      if (progress < 1) frame = window.requestAnimationFrame(tick);
    }

    frame = window.requestAnimationFrame(tick);
    return () => window.cancelAnimationFrame(frame);
  }, [value]);

  return displayValue;
}

function CommunityFooter() {
  const [likes, setLikes] = React.useState(1284);
  const [dislikes, setDislikes] = React.useState(37);
  const [visitors, setVisitors] = React.useState(1000);
  const [reaction, setReaction] = React.useState<"like" | "dislike" | null>(null);
  const [flash, setFlash] = React.useState<"like" | "dislike" | "visit" | null>(null);

  React.useEffect(() => {
    const storedReaction = window.localStorage.getItem("sofia-community-reaction") as "like" | "dislike" | null;
    const nextLikes = readStoredNumber("sofia-community-likes", 1284);
    const nextDislikes = readStoredNumber("sofia-community-dislikes", 37);
    let nextVisitors = readStoredNumber("sofia-community-visitors", 1000);
    const visitKey = `sofia-community-visit-${dateKey(new Date())}`;

    if (!window.localStorage.getItem(visitKey)) {
      nextVisitors += 1;
      window.localStorage.setItem(visitKey, "1");
      window.localStorage.setItem("sofia-community-visitors", String(nextVisitors));
      setFlash("visit");
      window.setTimeout(() => setFlash(null), 900);
    }

    setReaction(storedReaction);
    setLikes(nextLikes);
    setDislikes(nextDislikes);
    setVisitors(nextVisitors);
  }, []);

  function chooseReaction(nextReaction: "like" | "dislike") {
    let nextLikes = likes;
    let nextDislikes = dislikes;
    let resolvedReaction: "like" | "dislike" | null = nextReaction;

    if (reaction === nextReaction) {
      resolvedReaction = null;
      if (nextReaction === "like") nextLikes -= 1;
      if (nextReaction === "dislike") nextDislikes -= 1;
    } else {
      if (nextReaction === "like") nextLikes += 1;
      if (nextReaction === "dislike") nextDislikes += 1;
      if (reaction === "like") nextLikes -= 1;
      if (reaction === "dislike") nextDislikes -= 1;
    }

    setReaction(resolvedReaction);
    setLikes(nextLikes);
    setDislikes(nextDislikes);
    setFlash(nextReaction);
    window.setTimeout(() => setFlash(null), 900);
    window.localStorage.setItem("sofia-community-likes", String(nextLikes));
    window.localStorage.setItem("sofia-community-dislikes", String(nextDislikes));
    if (resolvedReaction) {
      window.localStorage.setItem("sofia-community-reaction", resolvedReaction);
    } else {
      window.localStorage.removeItem("sofia-community-reaction");
    }
  }

  const animatedVisitors = useAnimatedNumber(visitors);
  const animatedLikes = useAnimatedNumber(likes);
  const animatedDislikes = useAnimatedNumber(dislikes);
  const approval = Math.round((likes / Math.max(1, likes + dislikes)) * 100);

  return (
    <footer className="community-footer" aria-label="Ranking social de Sof-IA BO">
      <div className="community-glow" aria-hidden="true" />
      <div className="community-copy">
        <p className="eyebrow"><Sparkles size={16} /> Comunidad Sof-IA BO</p>
        <h2>Ranking en vivo del sistema</h2>
        <p>Tu reacción ayuda a mejorar el modelo y medir la confianza de la comunidad.</p>
      </div>
      <div className="community-stats">
        <div className={`community-card visitors ${flash === "visit" ? "pulse" : ""}`}>
          <Eye size={22} />
          <span>Visitantes</span>
          <strong>{animatedVisitors.toLocaleString("es-BO")}</strong>
        </div>
        <button
          className={`community-card reaction-card like ${reaction === "like" ? "active" : ""} ${flash === "like" ? "pulse" : ""}`}
          type="button"
          onClick={() => chooseReaction("like")}
          aria-pressed={reaction === "like"}
        >
          <ThumbsUp size={22} />
          <span>Me gusta</span>
          <strong>{animatedLikes.toLocaleString("es-BO")}</strong>
          <small>{approval}% aprobación</small>
        </button>
        <button
          className={`community-card reaction-card dislike ${reaction === "dislike" ? "active" : ""} ${flash === "dislike" ? "pulse" : ""}`}
          type="button"
          onClick={() => chooseReaction("dislike")}
          aria-pressed={reaction === "dislike"}
        >
          <ThumbsDown size={22} />
          <span>No me gusta</span>
          <strong>{animatedDislikes.toLocaleString("es-BO")}</strong>
          <small>feedback visible</small>
        </button>
      </div>
    </footer>
  );
}

function PlanetaryBackground() {
  return (
    <div className="planetary-bg" aria-hidden="true">
      <div className="star-field" />
      <div className="orbit orbit-one" />
      <div className="orbit orbit-two" />
      <div className="planet-core" />
    </div>
  );
}

function AppHeader({ sources }: { sources: SourceStatus[] }) {
  const updatedAt = sources[0]?.last_updated;
  const healthy = sources.filter((source) => source.status === "healthy").length;
  return (
    <header className="app-header">
      <div>
        <p className="eyebrow"><Sparkles size={16} /> Sistema predictivo del Mundial 2026</p>
        <h1>Sof-IA BO <span className="title-flag" role="img" aria-label="Bandera de Bolivia">🇧🇴</span></h1>
        <p className="subtitle">El Tigre <span role="img" aria-label="Tigre">🐯</span></p>
      </div>
      <div className="status-stack">
        <DataSourceStatus label="Fuentes activas" value={`${healthy}/${sources.length || 0}`} icon={<Database size={18} />} />
        <DataSourceStatus label="Última actualización" value={updatedAt ? formatDate(updatedAt) : "Cargando"} icon={<CalendarDays size={18} />} />
      </div>
    </header>
  );
}

function DataSourceStatus({ label, value, icon }: { label: string; value: string; icon: React.ReactNode }) {
  return (
    <div className="status-pill">
      {icon}
      <span>{label}</span>
      <strong>{value}</strong>
    </div>
  );
}

function DemoModeBanner() {
  return (
    <section className="demo-banner">
      <ShieldCheck size={20} />
      <p>
        Datos de demostración. Las simulaciones validan el flujo técnico con metodología matemática aplicada; las variables deportivas avanzadas se habilitan al conectar proveedores oficiales.
      </p>
    </section>
  );
}

function TournamentFilters({
  phases,
  selectedPhase,
  onPhaseChange,
  teamFilter,
  onTeamFilterChange,
  selectedDate,
  onDateChange,
  showFutureMatches,
  onToggleFutureMatches,
  todayMatchesCount,
  futureMatchesCount
}: {
  phases: string[];
  selectedPhase: string;
  onPhaseChange: (phase: string) => void;
  teamFilter: string;
  onTeamFilterChange: (value: string) => void;
  selectedDate: string;
  onDateChange: (value: string) => void;
  showFutureMatches: boolean;
  onToggleFutureMatches: () => void;
  todayMatchesCount: number;
  futureMatchesCount: number;
}) {
  return (
    <section className="filters" aria-label="Filtros de torneo">
      <label>
        Fase
        <select value={selectedPhase} onChange={(event) => onPhaseChange(event.target.value)}>
          {phases.map((phase) => (
            <option key={phase}>{phase}</option>
          ))}
        </select>
      </label>
      <label>
        Selección
        <input value={teamFilter} onChange={(event) => onTeamFilterChange(event.target.value)} placeholder="Filtrar por nombre o código" />
      </label>
      <label>
        Fecha
        <input
          type="date"
          aria-label="Selector de fecha"
          value={selectedDate}
          min={TODAY_KEY}
          disabled={showFutureMatches}
          onChange={(event) => onDateChange(event.target.value)}
        />
      </label>
      <div className="date-filter-actions">
        <span>{showFutureMatches ? `${futureMatchesCount} partidos futuros` : `${todayMatchesCount} partido(s) de hoy`}</span>
        <button className="future-filter-button" type="button" onClick={onToggleFutureMatches}>
          {showFutureMatches ? "Ver solo hoy" : "Mostrar todos los futuros"}
        </button>
      </div>
    </section>
  );
}

function MatchCard({ match, expanded, onToggle }: { match: Match; expanded: boolean; onToggle: () => void }) {
  return (
    <article className="match-card">
      <div className="match-topline">
        <span>{match.group ?? match.phase}</span>
        <span>{match.data_freshness.label}</span>
      </div>
      <div className="teams-row">
        <TeamIdentity team={match.home_team} align="left" />
        <div className="versus"><span>⚽</span><strong>vs</strong></div>
        <TeamIdentity team={match.away_team} align="right" />
      </div>
      <div className="match-meta">
        <span>{formatDate(match.kickoff)}</span>
        <span>{match.venue.city}, {match.venue.country}</span>
        <span>{match.venue.stadium ?? "Estadio por confirmar"}</span>
        <span>{match.status}</span>
      </div>
      <button className="prediction-button" onClick={onToggle} aria-expanded={expanded}>
        <Play size={18} />
        Simular y predecir
        <ChevronDown size={18} />
      </button>
      {expanded ? <PredictionPanel match={match} /> : null}
    </article>
  );
}

function TeamIdentity({ team, align }: { team: Team; align: "left" | "right" }) {
  return (
    <div className={`team-identity ${align}`}>
      <span className="flag" role="img" aria-label={`Bandera de ${team.name}`}>{team.flag}</span>
      <div>
        <strong>{team.name}</strong>
        <span>{team.code} · {team.confederation}</span>
      </div>
    </div>
  );
}

function PredictionPanel({ match }: { match: Match }) {
  const [events, setEvents] = React.useState<ProgressEvent[]>([]);
  const [result, setResult] = React.useState<PredictionResult | null>(null);
  const [loading, setLoading] = React.useState(false);
  const [visualProgress, setVisualProgress] = React.useState(0);
  const [error, setError] = React.useState<string | null>(null);

  function runPrediction() {
    const loadingStartedAt = Date.now();
    const loadingDurationMs = 5000;
    const progressTimer = window.setInterval(() => {
      const elapsed = Date.now() - loadingStartedAt;
      setVisualProgress(Math.min(99, Math.floor((elapsed / loadingDurationMs) * 100)));
    }, 80);
    setLoading(true);
    setError(null);
    setEvents([]);
    setResult(null);
    setVisualProgress(0);

    if (STATIC_MODE) {
      const steps = [
        "Obteniendo snapshot del modelo",
        "Verificando scouting y calendario",
        "Aplicando Modelo B, Markov y Bellman",
        "Reproduciendo Monte Carlo calibrado",
        "Predicción completada"
      ];
      steps.forEach((step, index) => {
        window.setTimeout(() => {
          setEvents((current) => [...current, {
            step,
            status: index === steps.length - 1 ? "completed" : "running",
            progress: Math.round(((index + 1) / steps.length) * 100),
            message: step
          }]);
        }, Math.min(loadingDurationMs - 250, index * 850));
      });
      window.setTimeout(() => {
        window.clearInterval(progressTimer);
        setVisualProgress(100);
        setResult((staticPredictions[match.id] ?? null) as PredictionResult | null);
        setLoading(false);
      }, loadingDurationMs);
      return;
    }

    fetch(`${API_BASE}/matches/${match.id}/predictions`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ simulations: 50000 })
    })
      .then((response) => {
        if (!response.ok) throw new Error("No se pudo crear la predicción.");
        return response.json();
      })
      .then((run) => {
        const source = new EventSource(`${API_BASE}/predictions/${run.prediction_id}/stream`);
        source.addEventListener("prediction", (event) => {
          const payload = JSON.parse((event as MessageEvent).data) as ProgressEvent;
          setEvents((current) => [...current, payload]);
          if (payload.result) {
            const remainingLoadingMs = Math.max(0, loadingDurationMs - (Date.now() - loadingStartedAt));
            window.setTimeout(() => {
              window.clearInterval(progressTimer);
              setVisualProgress(100);
              setResult(payload.result ?? null);
              setLoading(false);
            }, remainingLoadingMs);
            source.close();
          }
        });
        source.onerror = () => {
          window.clearInterval(progressTimer);
          setError("La conexión SSE se interrumpió.");
          setLoading(false);
          source.close();
        };
      })
      .catch((reason: Error) => {
        window.clearInterval(progressTimer);
        setError(reason.message);
        setLoading(false);
      });
  }

  React.useEffect(() => {
    runPrediction();
  }, [match.id]);

  const latest = events.length > 0 ? events[events.length - 1] : undefined;

  return (
    <section className="prediction-panel">
      <button className="secondary-action" onClick={runPrediction} disabled={loading}>
        <Activity size={18} />
        {loading ? "Analizando partido..." : result ? "Volver a predecir" : "Ejecutar flujo predictivo"}
      </button>
      <PredictionProgress events={events} latest={latest} visualProgress={visualProgress} />
      {error ? <ErrorState message={error} /> : null}
      {result ? <PredictionResultView result={result} match={match} /> : null}
    </section>
  );
}

function PredictionProgress({ events, latest, visualProgress }: { events: ProgressEvent[]; latest?: ProgressEvent; visualProgress: number }) {
  return (
    <div className="progress-wrap" aria-live="polite">
      <div className="progress-heading">
        <span>{latest?.message ?? "Listo para iniciar"}</span>
        <strong>{visualProgress}%</strong>
      </div>
      <div className="progress-track"><span style={{ width: `${visualProgress}%` }} /></div>
      <ol className="progress-steps">
        {events.map((event, index) => (
          <li key={`${event.step}-${index}`}>{event.step}</li>
        ))}
      </ol>
    </div>
  );
}

function PredictionResultView({ result, match }: { result: PredictionResult; match: Match }) {
  const primaryLabel = result.primary_outcome === "draw" ? "Empate" : result.primary_outcome === "home" ? match.home_team.name : match.away_team.name;
  const primaryFlag = result.primary_outcome === "draw" ? `${match.home_team.flag} ${match.away_team.flag}` : result.primary_outcome === "home" ? match.home_team.flag : match.away_team.flag;
  const primaryProbability = result.primary_outcome === "draw"
    ? result.probabilities.draw
    : result.primary_outcome === "home"
      ? result.probabilities.home_win
      : result.probabilities.away_win;
  const probabilities = [
    { name: match.home_team.code, value: result.probabilities.home_win },
    { name: "EMP", value: result.probabilities.draw },
    { name: match.away_team.code, value: result.probabilities.away_win }
  ];
  return (
    <section className="result-grid">
      <div className="result-main">
        <p className="eyebrow">Predicción final</p>
        <div className="winner-callout">
          <span>{result.primary_outcome === "draw" ? "Hay empate" : "Gana"}</span>
          <div className="winner-flag" role="img" aria-label={result.primary_outcome === "draw" ? "Banderas de ambos países" : `Bandera de ${primaryLabel}`}>{primaryFlag}</div>
          <h2>{primaryLabel}</h2>
          <strong>{primaryProbability.toFixed(2)}%</strong>
        </div>
        <div className="probability-bars">
          {probabilities.map((item) => (
            <div key={item.name}>
              <span>{item.name}</span>
              <div><i style={{ width: `${item.value}%` }} /></div>
              <strong>{item.value.toFixed(2)}%</strong>
            </div>
          ))}
        </div>
        <p className="confidence">Confianza {result.confidence.replace("_", " ")} · {result.confidence_note}</p>
      </div>
      <div className="metric-grid">
        <Metric label="Marcador probable" value={result.most_likely_score} />
        <Metric label="Goles esperados" value={`${result.expected_goals_home} - ${result.expected_goals_away}`} />
        <Metric label="Simulaciones" value={result.simulations.toLocaleString("es-BO")} />
        <Metric label="Incertidumbre" value={result.uncertainty_interval} />
        <Metric label="Modelo" value={result.model_version} />
        <Metric label="Corte de datos" value={formatDate(result.data_cutoff)} />
      </div>
      {match.knockout ? (
        <div className="knockout-strip">
          <Metric label={`Avanza ${match.home_team.code}`} value={`${result.qualification_probability_home?.toFixed(2)}%`} />
          <Metric label={`Avanza ${match.away_team.code}`} value={`${result.qualification_probability_away?.toFixed(2)}%`} />
          <Metric label="Prórroga" value={`${result.extra_time_probability?.toFixed(2)}%`} />
          <Metric label="Penales" value={`${result.penalties_probability?.toFixed(2)}%`} />
        </div>
      ) : null}
      <ExecutiveSummary result={result} />
    </section>
  );
}

function Metric({ label, value }: { label: string; value: string }) {
  return (
    <div className="metric">
      <span>{label}</span>
      <strong>{value}</strong>
    </div>
  );
}

function ExecutiveSummary({ result }: { result: PredictionResult }) {
  return (
    <section className="executive-summary">
      <h3>Conclusión ejecutiva</h3>
      <p>{result.executive_summary}</p>
      <h3>Factores determinantes</h3>
      <ul>
        {result.factors.map((factor) => (
          <li key={factor.name}>
            <strong>{factor.name}: {factor.impact > 0 ? "+" : ""}{factor.impact}</strong>
            <span>{factor.evidence}</span>
          </li>
        ))}
      </ul>
      <p className="disclaimer">{result.disclaimer}</p>
    </section>
  );
}

function SystemFlowchart() {
  const nodes = [
    { title: "1. Datos", detail: "Partido, equipos, forma y sede." },
    { title: "2. Modelos", detail: "Elo, Poisson, Modelo B, Markov y Bellman." },
    { title: "3. Simulación", detail: "Monte Carlo prueba miles de escenarios." },
    { title: "4. Resultado", detail: "Ganador o empate con porcentaje." }
  ];
  return (
    <section className="rail-panel">
      <h2>Cómo se predice</h2>
      <div className="flowchart">
        {nodes.map((node) => (
          <span key={node.title}>
            <strong>{node.title}</strong>
            <small>{node.detail}</small>
          </span>
        ))}
      </div>
    </section>
  );
}

function ErrorState({ message }: { message: string }) {
  return <p className="error-state">{message}</p>;
}

function EmptyState() {
  return <p className="empty-state">No hay partidos que coincidan con los filtros actuales.</p>;
}

ReactDOM.createRoot(document.getElementById("root")!).render(<App />);
