from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class Envio:
    id: int
    destinatario: str
    direccion: str
    tipo: str
    estado: str
    sucursal: str = "Central"
    fecha: str = field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d %H:%M"))
    lat: float | None = None
    lng: float | None = None
    clima: str | None = None
