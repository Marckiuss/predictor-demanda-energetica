import json
import boto3
import os
import urllib3
import time
import calendar
import logging
from botocore.exceptions import ClientError

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def lambda_handler(event, context):
    logger.info(
        "Iniciando ingesta histórica de demanda de ESIOS (Datos Crudos 10-min)..."
    )

    BUCKET_NAME = os.environ["BUCKET_NAME"]
    ESIOS_TOKEN = os.environ["ESIOS_TOKEN"]

    # Conexión con S3
    try:
        s3_client = boto3.client("s3")
    except ClientError as e:
        # Si falla la conexión a S3
        logger.error(f"Error crítico de conexión con S3: {e}")
        return {"statusCode": 500, "body": "Error de conexión S3"}

    # Timeout de 5 segundos para conectar a la web y 15 para recibir el JSON
    http = urllib3.PoolManager(timeout=urllib3.Timeout(connect=5.0, read=15.0))

    # Preparamos el token de acceso
    headers_esios = {
        "x-api-key": ESIOS_TOKEN,
        "Accept": "application/json",
        "Content-Type": "application/json",
    }

    # Seleccionamos el rango de años a extraer
    anios_a_extraer = range(2014, 2026)

    for anio in anios_a_extraer:
        for mes in range(1, 13):

            # Calculamos si el mes tiene 28, 30 o 31 días
            _, ultimo_dia = calendar.monthrange(anio, mes)

            # Damos el formato de fecha exacto
            start_date = f"{anio}-{mes:02d}-01T00:00:00"
            end_date = f"{anio}-{mes:02d}-{ultimo_dia:02d}T23:59:59"

            url_peticion = f"https://api.esios.ree.es/indicators/1293?start_date={start_date}&end_date={end_date}&geo_ids[]=8741"

            logger.info(f"Descargando año {anio} mes {mes:02d}...")

            try:
                respuesta = http.request("GET", url_peticion, headers=headers_esios)

                if respuesta.status == 200:
                    datos_json = json.loads(respuesta.data.decode("utf-8"))
                    texto_a_guardar = json.dumps(datos_json)

                    # Preparamos la ruta de carpetas
                    carpeta_s3 = f"bronze/esios/year={anio}/month={mes:02d}/"
                    nombre_archivo_s3 = f"{carpeta_s3}demanda_{anio}_{mes:02d}.json"

                    try:
                        # Subimos el JSON al bucket
                        s3_client.put_object(
                            Bucket=BUCKET_NAME,
                            Key=nombre_archivo_s3,
                            Body=texto_a_guardar,
                            ContentType="application/json",
                        )
                        logger.info(f"Guardado OK: {nombre_archivo_s3}")
                    except ClientError as e:
                        # Si AWS S3 bloquea la escritura
                        logger.error(
                            f"Fallo al escribir en S3 {nombre_archivo_s3}: {e}"
                        )
                        break

                    # Pausa para no saturar los servidores de ESIOS
                    time.sleep(2)

                else:
                    logger.warning(
                        f"Error en {anio}-{mes:02d}: Código HTTP {respuesta.status}"
                    )
                    break

            except urllib3.exceptions.TimeoutError:
                # Si se excede el timeout de lectura capturamos la excepción
                logger.error(
                    f"Timeout: La API de ESIOS no responde en {anio}-{mes:02d}."
                )
                break
            except Exception as e:
                # Capturamos otros posibles fallos
                logger.error(f"Fallo técnico inesperado: {e}")
                break

    logger.info("¡Ingesta completada de forma segura!")

    return {
        "statusCode": 200,
        "body": json.dumps(
            "Histórico procesado y guardado correctamente en la capa Bronze"
        ),
    }
