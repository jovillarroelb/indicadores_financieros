from pydantic import BaseModel
from typing import Optional

class Indicator(BaseModel):
    nombre: str
    codigo: str
    unidad_medida: str
    valor: float
    fecha: str
    variacion_diaria: float = 0.0
    variacion_semanal: float = 0.0
    variacion_mensual: float = 0.0
    valor_ayer: float = 0.0
    valor_semana: float = 0.0
    valor_mes: float = 0.0

class IndicatorsResponse(BaseModel):
    uf: Indicator
    dolar: Indicator
    euro: Indicator
    utm: Indicator
