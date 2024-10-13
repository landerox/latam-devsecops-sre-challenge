"""Cloud Function.

Este módulo implementa una Cloud Function que obtiene el valor del dólar estadounidense (USD)
desde una API externa y lo publica en un tema de Pub/Sub de Google Cloud. La función principal
coordina la obtención de los datos y su publicación, manejando excepciones y errores.

Funciones incluidas:
- load_config: Carga la configuración desde un archivo JSON.
- get_exchange_rate: Realiza una solicitud a una API para obtener el valor del dólar.
- publish_to_pubsub: Publica un mensaje en un tema de Pub/Sub.
- main: Función principal que coordina la ejecución.
"""

import json

import requests
from flask import Request, Response
from google.cloud import pubsub_v1


def load_config(config_path: str = "config.json") -> dict:
    """Carga la configuración desde un archivo JSON.

    Args:
    ----
        config_path (str): Ruta al archivo de configuración.

    Returns:
    -------
        dict: Un diccionario con los valores de configuración.

    Raises:
    ------
        RuntimeError: Si el archivo de configuración no se encuentra o tiene un formato inválido.

    """
    try:
        with open(config_path, "r") as config_file:
            return json.load(config_file)
    except FileNotFoundError as e:
        raise RuntimeError(f"Archivo de configuración no encontrado: {config_path}") from e
    except json.JSONDecodeError as e:
        raise RuntimeError(f"Error al leer el archivo de configuración: {e}") from e


def get_exchange_rates(api_url: str) -> list:
    """Obtiene las tasas de cambio de varias monedas desde una API externa.

    Args:
    ----
        api_url (str): La URL de la API para obtener las tasas de cambio.

    Returns:
    -------
        list: Una lista de diccionarios con los datos de las tasas de cambio
              obtenidos desde la API.

    Raises:
    ------
        RuntimeError: Si ocurre un error en la solicitud a la API o si el formato
        de la respuesta es incorrecto.

    """
    try:
        response = requests.get(api_url, timeout=5)
        response.raise_for_status()

        # Verifica si la respuesta es una lista válida
        data = response.json()
        if isinstance(data, list):
            return data
        else:
            raise ValueError(f"Formato de respuesta inesperado: {data}")
    except requests.exceptions.RequestException as e:
        raise RuntimeError(f"Error al obtener las tasas de cambio desde la API: {e}") from e
    except ValueError as e:
        raise RuntimeError(f"Error en el formato de la respuesta de la API: {e}") from e


def publish_to_pubsub(project_id: str, topic_id: str, message: list) -> None:
    """Publica un mensaje con todas las tasas de cambio en un tema de Pub/Sub.

    Args:
    ----
        project_id (str): ID del proyecto en GCP.
        topic_id (str): ID del tema de Pub/Sub.
        message (list): Lista de tasas de cambio a publicar en Pub/Sub.

    Raises:
    ------
        RuntimeError: Si ocurre un error al publicar el mensaje en Pub/Sub.

    """
    publisher = pubsub_v1.PublisherClient()
    topic_path = publisher.topic_path(project_id, topic_id)

    # Convertir el mensaje a formato JSON y codificarlo en UTF-8
    message_data = json.dumps(message, ensure_ascii=False).encode("utf-8")

    try:
        future = publisher.publish(topic_path, data=message_data)
        future.result()  # Esperar a que se publique el mensaje
    except Exception as e:
        raise RuntimeError(f"Error al publicar en Pub/Sub: {e}") from e


def main(_request: Request) -> Response:
    """Función principal que obtiene las tasas de cambio de varias monedas y las publica en Pub/Sub.

    Args:
    ----
        _request (Request): La solicitud HTTP que dispara la función.

    Returns:
    -------
        Response: Un objeto de respuesta HTTP indicando éxito o error.

    """
    try:
        # Cargar la configuración desde config.json
        config = load_config()

        # Extraer los valores de configuración
        project_id = config["project_id"]
        topic_id = config["pubsub_topic"]
        api_url = config["usd_api_url"]

        # Obtener las tasas de cambio desde la API
        exchange_rates = get_exchange_rates(api_url)

        # Publicar todas las tasas de cambio en un solo mensaje de Pub/Sub
        publish_to_pubsub(project_id, topic_id, exchange_rates)

        # Retornar respuesta exitosa
        return Response(
            json.dumps({"message": "Tasas de cambio publicadas exitosamente"}),
            status=200,
            mimetype="application/json",
        )
    except Exception as e:
        # Retornar el error en caso de que algo falle
        return Response(
            json.dumps({"error": "Error durante la ejecución", "detail": str(e)}),
            status=500,
            mimetype="application/json",
        )
