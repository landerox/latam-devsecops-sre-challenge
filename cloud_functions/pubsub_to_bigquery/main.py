"""Cloud Function.

Este módulo implementa una Cloud Function que recibe mensajes de Pub/Sub con información sobre
tasas de cambio y los inserta en una tabla de BigQuery.

Funciones incluidas:
- load_config: Carga la configuración desde un archivo JSON.
- insert_into_bigquery: Inserta un registro de tasa de cambio en una tabla de BigQuery.
- main: Función principal que recibe el evento de Pub/Sub, procesa los datos e inserta
        el resultado en BigQuery.
"""

import base64
import json
import logging

from google.cloud import bigquery

# Configurar el logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()


def load_config(config_path: str = "config.json") -> dict:
    """Carga la configuración desde un archivo JSON."""
    try:
        with open(config_path, "r") as config_file:
            return json.load(config_file)
    except FileNotFoundError as e:
        raise RuntimeError(f"Archivo de configuración no encontrado: {config_path}") from e
    except json.JSONDecodeError as e:
        raise RuntimeError(f"Error al leer el archivo de configuración: {e}") from e


def check_if_record_exists(
    project_id: str, dataset_id: str, table_name: str, fecha_actualizacion: str, moneda: str
) -> bool:
    """Verifica si ya existe un registro en BigQuery con la misma fechaActualizacion y moneda.

    Args:
    ----
        project_id (str): El ID del proyecto en GCP.
        dataset_id (str): El ID del dataset en BigQuery.
        table_name (str): El ID de la tabla en BigQuery.
        fecha_actualizacion (str): El valor de la fechaActualizacion a verificar.
        moneda (str): El nombre de la moneda a verificar.

    Returns:
    -------
        bool: True si el registro ya existe, False de lo contrario.

    """
    client = bigquery.Client(project=project_id)

    # Definir la consulta de manera segura
    query = """
        SELECT COUNT(*) as total
        FROM `{table_ref}`
        WHERE load_ts = @fecha_actualizacion AND currency = @moneda
    """

    # Crear la referencia a la tabla completa
    table_ref = f"{project_id}.{dataset_id}.{table_name}"

    # Configurar los parámetros de la consulta
    job_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter("fecha_actualizacion", "STRING", fecha_actualizacion),
            bigquery.ScalarQueryParameter("moneda", "STRING", moneda),
        ]
    )

    # Ejecutar la consulta
    query_job = client.query(query.format(table_ref=table_ref), job_config=job_config)
    result = query_job.result()

    # Comprobar si ya existe el registro
    for row in result:
        return row.total > 0

    return False


def insert_into_bigquery(data: dict, project_id: str, dataset_id: str, table_name: str) -> None:
    """Inserta un registro en una tabla de BigQuery.

    Args:
    ----
        data (dict): El registro que se va a insertar en la tabla.
        project_id (str): ID del proyecto en GCP.
        dataset_id (str): ID del dataset en BigQuery.
        table_name (str): ID de la tabla en BigQuery.

    Raises:
    ------
        RuntimeError: Si ocurre un error durante la inserción.

    """
    client = bigquery.Client(project=project_id)
    table_ref = f"{project_id}.{dataset_id}.{table_name}"

    errors = client.insert_rows_json(table_ref, [data])
    if errors:
        raise RuntimeError(f"Error al insertar en BigQuery: {errors}")


def transform_data_for_bigquery(data: dict) -> dict:
    """Transforma los nombres de los campos para que coincidan con el esquema de BigQuery.

    Args:
    ----
        data (dict): El diccionario de datos recibido desde Pub/Sub.

    Returns:
    -------
        dict: Un diccionario con los nombres de campos transformados para BigQuery.

    """
    return {
        "buy_rate": data.get("compra", 0),
        "sell_rate": data.get("venta", 0),
        "closing_rate": data.get("ultimoCierre", 0),
        "exchange_name": data.get("nombre", ""),
        "currency": data.get("moneda", ""),
        "load_ts": data.get("fechaActualizacion", ""),
    }


def main(event: dict, _context: dict) -> None:
    """Función principal que recibe el evento de Pub/Sub e inserta los datos en BigQuery.

    Args:
    ----
        event (dict): El evento de Pub/Sub, que incluye los datos publicados en el tema.
        context (dict): El contexto del evento, contiene metadatos sobre el evento.

    """
    try:
        # Cargar la configuración
        config = load_config()

        # Decodificar el mensaje de Pub/Sub
        if "data" in event:
            pubsub_message = base64.b64decode(event["data"]).decode("utf-8")
            data_list = json.loads(pubsub_message)

            # Verificar si la respuesta es una lista
            if isinstance(data_list, list):
                project_id = config["project_id"]
                dataset_id = config["dataset_id"]
                table_name = config["table_name"]

                # Procesar cada tipo de cambio individualmente
                for data in data_list:
                    transformed_data = transform_data_for_bigquery(data)
                    fecha_actualizacion = transformed_data["load_ts"]
                    moneda = transformed_data["currency"]

                    if not check_if_record_exists(
                        project_id, dataset_id, table_name, fecha_actualizacion, moneda
                    ):
                        # Insertar los datos si no existe un registro duplicado.
                        insert_into_bigquery(transformed_data, project_id, dataset_id, table_name)
                        logger.info(f"Datos insertados en BigQuery para {moneda} exitosamente.")
                    else:
                        logger.info(
                            f"Registro para {moneda} y fecha {fecha_actualizacion} duplicado."
                        )
            else:
                logger.error("Formato de datos recibido inesperado. Se esperaba una lista.")
        else:
            logger.error("No se encontraron datos en el evento de Pub/Sub.")
    except Exception as e:
        logger.error(f"Error durante la ejecución: {e}")
