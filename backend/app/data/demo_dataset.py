from __future__ import annotations
from datetime import datetime
from zoneinfo import ZoneInfo
from app.domain.schemas import DataFreshness, DataSourceStatus, Match, Team, Venue

TZ = ZoneInfo("America/La_Paz")
DEMO_UPDATED_AT = datetime(2026, 7, 9, 10, 0, tzinfo=TZ)


TEAMS: dict[str, Team] = {
    "rsa": Team(id="rsa", name="Sudáfrica", code="RSA", flag="🇿🇦", confederation="CAF", elo=1622, attack_strength=1.03, defense_strength=1.08, recent_form=0.61),
    "can": Team(id="can", name="Canadá", code="CAN", flag="🇨🇦", confederation="CONCACAF", elo=1774, attack_strength=1.18, defense_strength=1.00, recent_form=0.64),
    "bra": Team(id="bra", name="Brasil", code="BRA", flag="🇧🇷", confederation="CONMEBOL", elo=2095, attack_strength=1.44, defense_strength=0.78, recent_form=0.78),
    "jpn": Team(id="jpn", name="Japón", code="JPN", flag="🇯🇵", confederation="AFC", elo=1832, attack_strength=1.20, defense_strength=0.95, recent_form=0.70),
    "ger": Team(id="ger", name="Alemania", code="GER", flag="🇩🇪", confederation="UEFA", elo=1995, attack_strength=1.38, defense_strength=0.86, recent_form=0.74),
    "par": Team(id="par", name="Paraguay", code="PAR", flag="🇵🇾", confederation="CONMEBOL", elo=1768, attack_strength=1.08, defense_strength=0.98, recent_form=0.64),
    "ned": Team(id="ned", name="Países Bajos", code="NED", flag="🇳🇱", confederation="UEFA", elo=2010, attack_strength=1.34, defense_strength=0.84, recent_form=0.73),
    "mar": Team(id="mar", name="Marruecos", code="MAR", flag="🇲🇦", confederation="CAF", elo=1848, attack_strength=1.16, defense_strength=0.90, recent_form=0.70),
    "civ": Team(id="civ", name="Costa de Marfil", code="CIV", flag="🇨🇮", confederation="CAF", elo=1716, attack_strength=1.09, defense_strength=1.02, recent_form=0.62),
    "nor": Team(id="nor", name="Noruega", code="NOR", flag="🇳🇴", confederation="UEFA", elo=1920, attack_strength=1.31, defense_strength=0.93, recent_form=0.72),
    "fra": Team(id="fra", name="Francia", code="FRA", flag="🇫🇷", confederation="UEFA", elo=2108, attack_strength=1.46, defense_strength=0.76, recent_form=0.80),
    "swe": Team(id="swe", name="Suecia", code="SWE", flag="🇸🇪", confederation="UEFA", elo=1840, attack_strength=1.18, defense_strength=0.94, recent_form=0.67),
    "mex": Team(id="mex", name="México", code="MEX", flag="🇲🇽", confederation="CONCACAF", elo=1790, attack_strength=1.17, defense_strength=0.98, recent_form=0.66),
    "ecu": Team(id="ecu", name="Ecuador", code="ECU", flag="🇪🇨", confederation="CONMEBOL", elo=1856, attack_strength=1.18, defense_strength=0.91, recent_form=0.69),
    "eng": Team(id="eng", name="Inglaterra", code="ENG", flag="🏴", confederation="UEFA", elo=2038, attack_strength=1.35, defense_strength=0.82, recent_form=0.76),
    "cod": Team(id="cod", name="RD Congo", code="COD", flag="🇨🇩", confederation="CAF", elo=1612, attack_strength=0.96, defense_strength=1.09, recent_form=0.55),
    "bel": Team(id="bel", name="Bélgica", code="BEL", flag="🇧🇪", confederation="UEFA", elo=1950, attack_strength=1.32, defense_strength=0.89, recent_form=0.71),
    "sen": Team(id="sen", name="Senegal", code="SEN", flag="🇸🇳", confederation="CAF", elo=1836, attack_strength=1.15, defense_strength=0.92, recent_form=0.68),
    "usa": Team(id="usa", name="Estados Unidos", code="USA", flag="🇺🇸", confederation="CONCACAF", elo=1812, attack_strength=1.22, defense_strength=0.97, recent_form=0.66),
    "bih": Team(id="bih", name="Bosnia y Herzegovina", code="BIH", flag="🇧🇦", confederation="UEFA", elo=1710, attack_strength=1.08, defense_strength=1.04, recent_form=0.61),
    "esp": Team(id="esp", name="España", code="ESP", flag="🇪🇸", confederation="UEFA", elo=2060, attack_strength=1.42, defense_strength=0.80, recent_form=0.78),
    "aut": Team(id="aut", name="Austria", code="AUT", flag="🇦🇹", confederation="UEFA", elo=1846, attack_strength=1.16, defense_strength=0.94, recent_form=0.68),
    "por": Team(id="por", name="Portugal", code="POR", flag="🇵🇹", confederation="UEFA", elo=2016, attack_strength=1.37, defense_strength=0.83, recent_form=0.78),
    "cro": Team(id="cro", name="Croacia", code="CRO", flag="🇭🇷", confederation="UEFA", elo=1888, attack_strength=1.13, defense_strength=0.91, recent_form=0.66),
    "sui": Team(id="sui", name="Suiza", code="SUI", flag="🇨🇭", confederation="UEFA", elo=1852, attack_strength=1.12, defense_strength=0.91, recent_form=0.68),
    "alg": Team(id="alg", name="Argelia", code="ALG", flag="🇩🇿", confederation="CAF", elo=1728, attack_strength=1.08, defense_strength=1.00, recent_form=0.63),
    "aus": Team(id="aus", name="Australia", code="AUS", flag="🇦🇺", confederation="AFC", elo=1715, attack_strength=1.07, defense_strength=1.03, recent_form=0.62),
    "egy": Team(id="egy", name="Egipto", code="EGY", flag="🇪🇬", confederation="CAF", elo=1748, attack_strength=1.10, defense_strength=0.99, recent_form=0.64),
    "arg": Team(id="arg", name="Argentina", code="ARG", flag="🇦🇷", confederation="CONMEBOL", elo=2148, attack_strength=1.48, defense_strength=0.72, recent_form=0.82),
    "cpv": Team(id="cpv", name="Cabo Verde", code="CPV", flag="🇨🇻", confederation="CAF", elo=1588, attack_strength=0.96, defense_strength=1.12, recent_form=0.58),
    "col": Team(id="col", name="Colombia", code="COL", flag="🇨🇴", confederation="CONMEBOL", elo=1946, attack_strength=1.25, defense_strength=0.88, recent_form=0.72),
    "gha": Team(id="gha", name="Ghana", code="GHA", flag="🇬🇭", confederation="CAF", elo=1664, attack_strength=1.02, defense_strength=1.05, recent_form=0.58),
}


def demo_freshness() -> DataFreshness:
    return DataFreshness(
        label="Fixture desde hoy · variables demo",
        source_mode="demo",
        last_updated=DEMO_UPDATED_AT,
        cutoff=DEMO_UPDATED_AT,
        warnings=[
            "Calendario actualizado al Mundial 2026 del 9 de julio de 2026: cuartos de final completos.",
            "La pantalla muestra primero los partidos del día actual; el backend mantiene los próximos cruces cargados.",
            "Fixture contrastado con cobertura deportiva actual; Elo, xG y titulares siguen como variables demo calibradas.",
        ],
    )


def knockout_match(match_id: str, home: str, away: str, year: int, month: int, day: int, hour: int, minute: int, city: str, stadium: str, altitude_m: int) -> Match:
    return Match(
        id=match_id,
        home_team=TEAMS[home],
        away_team=TEAMS[away],
        kickoff=datetime(year, month, day, hour, minute, tzinfo=TZ),
        venue=Venue(city=city, country="Estados Unidos" if city not in ("Monterrey", "Ciudad de México", "Toronto", "Vancouver") else ("México" if city in ("Monterrey", "Ciudad de México") else "Canadá"), stadium=stadium, altitude_m=altitude_m),
        group=None,
        phase="Cuartos de final · eliminación directa",
        status="scheduled",
        knockout=True,
        data_freshness=demo_freshness(),
    )


MATCHES: list[Match] = [
    knockout_match("today-mar-fra", "mar", "fra", 2026, 7, 9, 16, 0, "Boston", "Boston Stadium", 6),
    knockout_match("qf-esp-bel", "esp", "bel", 2026, 7, 10, 15, 0, "Los Ángeles", "Los Angeles Stadium", 93),
    knockout_match("qf-nor-eng", "nor", "eng", 2026, 7, 11, 17, 0, "Miami", "Miami Stadium", 2),
    knockout_match("qf-arg-sui", "arg", "sui", 2026, 7, 11, 21, 0, "Kansas City", "Kansas City Stadium", 270),
]


def get_demo_matches() -> list[Match]:
    return MATCHES


def get_demo_match(match_id: str) -> Match | None:
    return next((match for match in MATCHES if match.id == match_id), None)


def get_data_sources() -> list[DataSourceStatus]:
    return [
        DataSourceStatus(
            id="demo-local",
            name="DemoDataProvider",
            status="healthy",
            mode="demo",
            last_updated=DEMO_UPDATED_AT,
            message="Fixture actualizado desde hoy: 4 partidos de cuartos de final; la UI muestra primero la fecha actual.",
        ),
        DataSourceStatus(
            id="official-provider",
            name="OfficialTournamentProvider",
            status="offline",
            mode="external",
            last_updated=DEMO_UPDATED_AT,
            message="Pendiente de credenciales y licencia de uso.",
        ),
        DataSourceStatus(
            id="ranking-provider",
            name="RankingProvider",
            status="offline",
            mode="external",
            last_updated=DEMO_UPDATED_AT,
            message="Interfaz preparada; sin proveedor externo conectado.",
        ),
    ]
