"""Exchange-API.

Este módulo proporciona una API llamada Exchange-API, desarrollada utilizando FastAPI y BigQuery.
"""

import json
from datetime import datetime
from typing import Any, Dict, List

from fastapi import FastAPI, HTTPException
from google.cloud import bigquery
from pydantic import BaseModel

app = FastAPI()

# Cargar la configuración desde config.json
with open("config.json") as config_file:
    config = json.load(config_file)

PROJECT_ID = config.get("project_id")
DATASET_ID = config.get("dataset_id")
TABLE_NAME = config.get("table_name")


@app.get("/")
def health_check() -> Dict[str, str]:
    """Endpoint para verificar el estado de la API.

    Returns
    -------
        Dict[str, str]: Un diccionario que indica el estado de la API.

    """
    return {"status": "running"}


def get_bigquery_client() -> bigquery.Client:
    """Crea y retorna un cliente de BigQuery.

    Returns
    -------
        bigquery.Client: Cliente de BigQuery.

    """
    return bigquery.Client()


class ExchangeRate(BaseModel):
    """Modelo que representa una tasa de cambio.

    Attributes
    ----------
        buy_rate (float): Tasa de compra.
        sell_rate (float): Tasa de venta.
        closing_rate (float): Tasa de cierre.
        exchange_name (str): Nombre de la casa de cambio.
        currency (str): Moneda de la tasa de cambio.
        load_ts (datetime): Timestamp de la carga de datos.

    """

    buy_rate: float
    sell_rate: float
    closing_rate: float
    exchange_name: str
    currency: str
    load_ts: datetime


@app.get("/exchange-rates", response_model=List[Dict[str, Any]])
async def get_exchange_rates() -> List[Dict[str, Any]]:
    """Obtiene todas las tasas de cambio desde BigQuery.

    Returns
    -------
        List[Dict[str, Any]]: Lista de tasas de cambio almacenadas en BigQuery.

    Raises
    ------
        HTTPException: Si ocurre un error al obtener los datos desde BigQuery.

    """
    query: str = """
        SELECT *
        FROM `{}.{}.{}`
        LIMIT 100
    """
    params = (PROJECT_ID, DATASET_ID, TABLE_NAME)

    try:
        client: bigquery.Client = get_bigquery_client()
        query_job: bigquery.QueryJob = client.query(query.format(*params))
        results = query_job.result()
        rates: List[Dict[str, Any]] = [dict(row) for row in results]
        return rates

    except Exception as e:
        app.logger.error(f"Error al obtener tasas de cambio: {str(e)}")
        raise HTTPException(status_code=500, detail="Error interno del servidor") from e


@app.post("/exchange-rates", status_code=201)
async def insert_exchange_rate(exchange_rate: ExchangeRate) -> Dict[str, str]:
    """Inserta una nueva tasa de cambio en BigQuery.

    Args:
    ----
        exchange_rate (ExchangeRate): Datos de la tasa de cambio a insertar.

    Returns:
    -------
        Dict[str, str]: Mensaje de éxito.

    Raises:
    ------
        HTTPException: Si ocurre un error al insertar los datos en BigQuery.

    """
    try:
        data: Dict[str, Any] = exchange_rate.dict()
        client: bigquery.Client = get_bigquery_client()
        table_ref: str = f"{PROJECT_ID}.{DATASET_ID}.{TABLE_NAME}"
        errors: List[Dict[str, Any]] = client.insert_rows_json(table_ref, [data])

        if errors:
            app.logger.error(f"Error al insertar datos: {str(errors)}")
            raise HTTPException(status_code=500, detail="Error al insertar datos")

        return {"message": "Registro insertado exitosamente"}

    except Exception as e:
        app.logger.error(f"Error al insertar tasa de cambio: {str(e)}")
        raise HTTPException(status_code=500, detail="Error interno del servidor") from e
