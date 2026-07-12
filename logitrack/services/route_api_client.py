import time
from typing import ClassVar

import requests

from logitrack.logger import get_logger

_log = get_logger("api.route")

_CODIGOS_WMO: dict[int, str] = {
    0: "Despejado",
    1: "Mayormente despejado",
    2: "Parcialmente nublado",
    3: "Nublado",
    45: "Niebla",
    48: "Niebla helada",
    51: "Llovizna leve",
    53: "Llovizna moderada",
    55: "Llovizna intensa",
    61: "Lluvia leve",
    63: "Lluvia moderada",
    65: "Lluvia intensa",
    71: "Nevada leve",
    73: "Nevada moderada",
    75: "Nevada intensa",
    80: "Chubascos leves",
    81: "Chubascos moderados",
    82: "Chubascos intensos",
    95: "Tormenta",
    96: "Tormenta con granizo",
    99: "Tormenta intensa con granizo",
}


class RouteApiClient:
    """Enriquece envíos con geocodificación (Nominatim) y clima (Open-Meteo)."""

    NOMINATIM = "https://nominatim.openstreetmap.org/search"
    OPENMETEO = "https://api.open-meteo.com/v1/forecast"
    TIMEOUT = 8
    INTENTOS = 3        # intentos totales (1 original + 2 reintentos)
    PAUSA_REINTENTO = 1.2
    _MIN_PAUSA_NOMINATIM: ClassVar[float] = 1.1  # política de uso: 1 req/seg

    _HEADERS = {"User-Agent": "LogiTrack/1.0 (proyecto-integrador)"}

    def __init__(self) -> None:
        self._ultimo_nominatim: float = 0.0  # monotonic timestamp

    # ── API pública ───────────────────────────────────────────────────

    def obtener_datos_ruta(self, direccion: str) -> dict | None:
        """
        Retorna dict con claves lat, lng, clima, estado_red.
        Retorna None si falla la geocodificación.
        """
        # Nominatim exige ≥ 1 req/seg; esperamos si es necesario antes de llamar
        transcurrido = time.monotonic() - self._ultimo_nominatim
        if transcurrido < self._MIN_PAUSA_NOMINATIM:
            espera = self._MIN_PAUSA_NOMINATIM - transcurrido
            _log.debug("Nominatim cooldown %.2fs para '%s'", espera, direccion)
            time.sleep(espera)

        _log.info("Geocodificando dirección: '%s'", direccion)
        resp = self._get(self.NOMINATIM, {
            "q": direccion, "format": "json", "limit": 1,
            "accept-language": "es",
        })
        self._ultimo_nominatim = time.monotonic()

        if resp is None:
            _log.warning("Nominatim no respondió para '%s'", direccion)
            return None

        resultados = resp.json()
        if not resultados:
            _log.warning("Nominatim sin resultados para '%s'", direccion)
            return None

        lat = float(resultados[0]["lat"])
        lng = float(resultados[0]["lon"])
        _log.info("Geocodificación OK → lat=%.4f, lng=%.4f", lat, lng)

        clima_str = self._obtener_clima(lat, lng)

        estado_red = "ok" if clima_str else "ok_parcial"
        _log.info("Enriquecimiento completo — estado_red=%s, clima=%s", estado_red, clima_str)
        return {
            "lat": lat,
            "lng": lng,
            "clima": clima_str,
            "estado_red": estado_red,
        }

    # ── Helpers internos ──────────────────────────────────────────────

    def _obtener_clima(self, lat: float, lng: float) -> str | None:
        _log.info("Consultando clima en lat=%.4f, lng=%.4f", lat, lng)
        resp = self._get(self.OPENMETEO, {
            "latitude": lat,
            "longitude": lng,
            "current_weather": "true",
        })
        if resp is None:
            _log.warning("Open-Meteo no respondió para lat=%.4f, lng=%.4f", lat, lng)
            return None
        weather = resp.json().get("current_weather", {})
        codigo = weather.get("weathercode", -1)
        temp = weather.get("temperature")
        descripcion = _CODIGOS_WMO.get(codigo, f"Código {codigo}")
        resultado = f"{descripcion}, {temp}°C" if temp is not None else descripcion
        _log.info("Clima OK → %s (código WMO %s)", resultado, codigo)
        return resultado

    def _get(self, url: str, params: dict) -> requests.Response | None:
        dominio = url.split("/")[2]
        for intento in range(self.INTENTOS):
            t0 = time.monotonic()
            try:
                resp = requests.get(
                    url, params=params,
                    timeout=self.TIMEOUT,
                    headers=self._HEADERS,
                )
                latencia = (time.monotonic() - t0) * 1000
                resp.raise_for_status()
                _log.debug(
                    "GET %s → HTTP %d  (%.0fms, intento %d/%d)",
                    dominio, resp.status_code, latencia, intento + 1, self.INTENTOS,
                )
                return resp
            except requests.exceptions.HTTPError as exc:
                codigo = exc.response.status_code if exc.response is not None else 0
                _log.warning(
                    "GET %s → HTTP %d (intento %d/%d)",
                    dominio, codigo, intento + 1, self.INTENTOS,
                )
                if 400 <= codigo < 500 and codigo != 429:
                    break
            except requests.exceptions.Timeout:
                _log.warning(
                    "GET %s → Timeout tras %.0fms (intento %d/%d)",
                    dominio, (time.monotonic() - t0) * 1000, intento + 1, self.INTENTOS,
                )
            except requests.exceptions.ConnectionError as exc:
                _log.warning(
                    "GET %s → ConnectionError (intento %d/%d): %s",
                    dominio, intento + 1, self.INTENTOS, exc,
                )
            except requests.exceptions.RequestException as exc:
                _log.error("GET %s → error irrecuperable: %s", dominio, exc)
                break
            if intento < self.INTENTOS - 1:
                _log.debug("Reintentando en %.1fs…", self.PAUSA_REINTENTO)
                time.sleep(self.PAUSA_REINTENTO)
        _log.error("GET %s → agotados %d intentos, sin respuesta", dominio, self.INTENTOS)
        return None
