<div align="right">

![Version](https://img.shields.io/badge/Version-0.0.1-blue?style=flat) 
![License](https://img.shields.io/badge/License-MIT-blue?style=flat) 
![Python](https://img.shields.io/badge/Language-Python-blue?style=flat) 

</div>

# Desafío DevSecOps/SRE LATAM Airlines

Este repositorio contiene la solución para el desafío DevSecOps/SRE de LATAM Airlines. La arquitectura está diseñada para ser serverless y basada en eventos, procesando diariamente las tasas de cambio de diferentes monedas desde una API pública externa y exponiendo los datos procesados a través de una API REST.

## 1. Descripción General de la Solución

La solución está diseñada para ingerir, procesar y exponer tasas de cambio de una API pública externa. La arquitectura es impulsada por eventos y utiliza componentes serverless de Google Cloud.

## 2. Diagrama de la Arquitectura

El diagrama de la arquitectura del sistema, que describe el flujo de ingesta y exposición de datos, el despliegue y almacenamiento, lo puedes encontrar [aquí](drawio/arquitectura_devsecops_latam_airlines.jpg).

## Componentes Principales de la Arquitectura

1. **Cloud Function: `api_to_pubsub`**
   - Esta Cloud Function consume una API pública externa que proporciona las tasas de cambio de diferentes monedas. Los datos obtenidos se envían al tópico de Pub/Sub llamado `currency-exchange-rate-topic`, donde estarán disponibles para su posterior procesamiento.

2. **Tópico Pub/Sub: `currency-exchange-rate-topic`**
   - Este tópico actúa como un canal de mensajería en el que se publican los datos de las tasas de cambio. Los mensajes publicados en este tópico son procesados por suscriptores como la función `pubsub_to_bigquery`.

3. **Cloud Function: `pubsub_to_bigquery`**
   - Esta Cloud Function se suscribe al tópico `currency-exchange-rate-topic`. Procesa los datos y los ingresa en una tabla particionada de BigQuery, facilitando la consulta y análisis diario de las tasas de cambio.

4. **API REST (desplegada en Cloud Run)**
   - La API REST, desplegada en Cloud Run, permite acceder a los datos almacenados en BigQuery a través de dos endpoints:
     - **GET**: Recupera las tasas de cambio almacenadas en la tabla de BigQuery.
     - **POST**: Inserta nuevos registros de tasas de cambio en BigQuery.
   - **Cloud Run** proporciona escalabilidad y alta disponibilidad sin la necesidad de gestión manual de infraestructura.

5. **Artifact Registry**
   - Las imágenes Docker que utiliza Cloud Run para desplegar la API REST son almacenadas en Artifact Registry, asegurando una gestión eficiente y segura de los contenedores.

6. **Pipeline CI/CD (GitHub Actions + Terraform)**
   - El proceso de despliegue de la infraestructura y aplicaciones es gestionado automáticamente mediante un pipeline CI/CD en GitHub Actions, que se encarga de:
     - Construir la imagen Docker de la API.
     - Almacenar la imagen en Artifact Registry.
     - Desplegar las Cloud Functions, la API en Cloud Run y los componentes de infraestructura utilizando Terraform.

## 3. Diseño de la Solución

### Flujo de Ingesta de Datos

1. La función `api_to_pubsub` consume la API externa de tasas de cambio y publica los datos en un tópico de Pub/Sub.
2. La función `pubsub_to_bigquery` se suscribe al tópico de Pub/Sub y almacena los datos en BigQuery.
3. La API REST, desplegada en Cloud Run, expone los datos a través de dos endpoints: **GET** y **POST**.

### Infraestructura como Código (IaC)

Toda la infraestructura se aprovisiona utilizando Terraform, lo que garantiza reproducibilidad y control de versiones.

### Pipeline CI/CD

El pipeline automatiza el despliegue, desde la construcción de la imagen Docker hasta la aplicación de las configuraciones de Terraform para gestionar la infraestructura.

## Pruebas de Integración y Puntos Críticos de Calidad

Se ha implementado una prueba básica en el pipeline CI/CD para verificar que la API expone correctamente los datos desde la base de datos (BigQuery o Cloud SQL):

1. **Verificación de Exposición de Datos desde la API**
   - **Implementación**: Se realiza una solicitud `GET` al endpoint `/exchange-rates` de la API y se verifica que responde con éxito (código 200).
   - **Objetivo**: Asegurar que la API REST está consultando y exponiendo los datos correctamente desde la base de datos.

### Propuestas para Extender las Pruebas de Integración

2. **Prueba de Inserción de Datos**
   - **Propuesta**: Realizar una solicitud `POST` para insertar nuevos registros de tasas de cambio en la base de datos y verificar que los datos se han insertado correctamente.

3. **Verificación de Procesamiento de Mensajes en Pub/Sub**
   - **Propuesta**: Publicar un mensaje en Pub/Sub y verificar que es procesado por la función `pubsub_to_bigquery` y almacenado en BigQuery.

4. **Prueba de Escalabilidad y Autoescalado**
   - **Propuesta**: Simular una carga alta en la API y verificar que el sistema escale automáticamente (Cloud Run o Cloud Functions) para manejar la carga.

### Puntos Críticos del Sistema

1. **Fallo en la Conectividad con la Base de Datos:**
   - **Posible fallo**: La API podría perder conectividad con la base de datos (BigQuery o Cloud SQL), afectando la exposición de los datos.
   - **Propuesta de prueba**: Simular la desconexión de la base de datos y observar cómo la API maneja el fallo.
   - **Forma de medición**: Evaluar la respuesta de la API y las alertas generadas.

2. **Latencia en las Consultas a la Base de Datos:**
   - **Posible fallo**: Las consultas podrían volverse lentas a medida que aumenta el volumen de datos.
   - **Propuesta de prueba**: Ejecutar pruebas de carga en las consultas y evaluar la latencia.
   - **Forma de medición**: Medir el tiempo de respuesta de las consultas bajo carga.

3. **Sobrecarga en el Procesamiento de Mensajes en Pub/Sub:**
   - **Posible fallo**: La función `pubsub_to_bigquery` podría no procesar a tiempo todos los mensajes si la tasa de publicación es muy alta.
   - **Propuesta de prueba**: Simular una carga elevada de mensajes y observar el procesamiento.
   - **Forma de medición**: Monitorear la latencia en Pub/Sub y la tasa de procesamiento en BigQuery.

### Robustecimiento Técnico del Sistema

1. **Circuit Breaker y Retry Mechanism**: Implementar un "circuit breaker" y un mecanismo de reintentos para manejar desconexiones temporales.
2. **Caché para Consultas Frecuentes**: Implementar Cloud Memorystore (Redis) para reducir la carga en la base de datos.
3. **Autoescalado de Cloud Run y Cloud Functions**: Configurar escalado automático en función de métricas de latencia y procesamiento.

## 4. Endpoints de la API REST

La API REST está expuesta en el siguiente URL:

- **URL**: [https://exchange-api-73859077778.us-central1.run.app/exchange-rates](https://exchange-api-73859077778.us-central1.run.app/exchange-rates)
- **Método**: GET
- **Descripción**: Recupera las tasas de cambio almacenadas en la base de datos (BigQuery o Cloud SQL).

### Cómo probar el endpoint:

Para probar el endpoint desde la terminal o Cloud Shell, puedes usar el siguiente comando `curl`:

```bash
curl -X GET https://exchange-api-73859077778.us-central1.run.app/exchange-rates
```

## 5. Métricas y Monitoreo

### Métricas Críticas

1. **Latencia de las Consultas a la Base de Datos**: Medir el tiempo desde la API REST hasta BigQuery o Cloud SQL.
2. **Tasa de Fallos en las Funciones Serverless**: Monitorear el porcentaje de fallos en las ejecuciones de Cloud Functions.
3. **Tiempo de Procesamiento de Mensajes en Pub/Sub**: Medir el tiempo desde la publicación hasta el almacenamiento en la base de datos.

### Herramienta de Visualización

Google Cloud Monitoring ofrece integración nativa con Pub/Sub, Cloud Functions, y BigQuery. No se requiere mucha configuración adicional, solo asegurarte de que los servicios están vinculados y las métricas relevantes se están recolectando y visualizando adecuadamente en los paneles de control.

Google Cloud Monitoring para configurar gráficos que visualicen:
- Latencia promedio de consultas.
- Tasa de fallos en funciones.
- Tiempo de procesamiento de Pub/Sub.

### Visualización con Mayor Escalabilidad

Al escalar a 50 sistemas similares:
- Agregar agregaciones y promedios para observar globalmente.
- Agrupar por regiones o proyectos para aislar problemas específicos.
- Nuevas métricas como CPU y memoria serán más importantes.

### Dificultades de Escalabilidad

- **Ruido en las Alertas**: Aumentan las alertas innecesarias si no se configuran bien.
- **Aislamiento de Problemas**: Sin etiquetas adecuadas, será difícil identificar problemas.
- **Costos de Monitoreo**: El monitoreo de muchos sistemas incrementa los costos.

## 6. Alertas y SRE

### Reglas de Alertas

1. **Latencia en Pub/Sub**: Si el tiempo de procesamiento supera los 500ms, disparar alerta.
2. **Errores en Cloud Functions**: Si la tasa de errores excede el 1%, disparar alerta.
3. **Latencia de la API**: Si el tiempo de respuesta supera los 2 segundos para el 95% de las solicitudes, disparar alerta.

### SLIs y SLOs

- **Disponibilidad de la API** (SLO: 99.9%).
- **Latencia de la API** (SLO: 95% de las solicitudes en menos de 2 segundos).
- **Tasa de éxito de Pub/Sub** (SLO: 99.5% de mensajes procesados sin errores).

## 7. Configuración de GitHub Secrets para CI/CD

Se utilizan **GitHub Secrets** para gestionar credenciales y variables sensibles en Google Cloud Platform. Estos secretos se integran automáticamente en el flujo CI/CD definido en el archivo `cicd.yaml`.

### Secretos Configurados:

1. `GCP_BUCKET`: Nombre del bucket de Google Cloud.
2. `GCP_LOCATION`: Ubicación geográfica.
3. `GCP_PROJECT_ID`: ID del proyecto.
4. `GCP_REGION`: Región de despliegue.
5. `GCP_SERVICE_ACCOUNT`: Credenciales de la cuenta de servicio (JSON).
6. `GCP_SERVICE_ACCOUNT_EMAIL`: Correo electrónico de la cuenta de servicio.
7. `GCP_TERRAFORM_STATE`: Prefijo para el almacenamiento de Terraform State.

Estos secretos permiten la autenticación y configuración segura del pipeline CI/CD.

### Proceso del Pipeline CI/CD:

1. Autenticación en Google Cloud.
2. Construcción y despliegue de la imagen Docker a **Artifact Registry**.
3. Ejecución de Terraform para desplegar la infraestructura.
4. Aplicación del plan de Terraform con las variables configuradas en los secretos de GitHub.

## 8. Herramientas de Desarrollo

El repositorio cuenta con **Poetry** y **Pre-commit** configurados para manejar dependencias y mejorar el proceso de desarrollo y testeo local. Además, el uso de **GitHub Actions** permite integrar y probar la aplicación en un ambiente de desarrollo.

El repositorio también incluye un archivo **.devcontainer**, el cual permite a los desarrolladores configurar de manera automática las extensiones y herramientas necesarias en **VSCode** para trabajar en un entorno de desarrollo homogéneo y preconfigurado. Esto asegura que las dependencias, las versiones de las herramientas y los entornos estén alineados para todos los colaboradores del proyecto.

### Herramientas incluidas en el **.devcontainer**:
- **Poetry**: Manejo de dependencias y virtual environments.
- **Pre-commit**: Automatización de chequeos previos a los commits.
- **Extensiones de VSCode**: Se incluyen extensiones esenciales para trabajar con **Terraform**, **Python**, y **Docker** en un entorno optimizado.

### Recomendaciones:
Es importante generar una cuenta de servicio y configurar la clave para activar **GitHub Actions**, lo cual permitirá integrar fácilmente el pipeline de CI/CD y facilitar el desarrollo local. Además, se recomienda utilizar **VSCode** con **Remote - Containers** para aprovechar al máximo la configuración del **.devcontainer**.
