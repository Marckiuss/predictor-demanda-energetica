import json
import boto3
import os
from datetime import datetime
import urllib3
import logging
from botocore.exceptions import ClientError

# Configuramos el logger
logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context):
    logger.info("Iniciando el módulo de ingesta de festivos oficiales...")

    BUCKET_NAME = os.environ['BUCKET_NAME']
    
    # Conexión a S3
    try:
        s3_client = boto3.client('s3')
        logger.info("Conexión exitosa con AWS S3 establecida.")
    except ClientError as e:
        # capturamos errores de permisos en S3 y detenemos la ejecución
        logger.error(f"Error crítico en las credenciales o conexión inicial con AWS S3: {e}")
        return {"statusCode": 500, "body": "Error de conexión S3"}

    # Timeout de 5 segundos para el tiempo conexión y 15 para lectura
    http = urllib3.PoolManager(timeout=urllib3.Timeout(connect=5.0, read=15.0))
    
    year_actual = datetime.now().year
    
    # Rango de años a extraer
    anios_a_extraer = range(2014, year_actual + 1)
    
    for anio in anios_a_extraer:
        url_peticion = f"https://date.nager.at/api/v3/PublicHolidays/{anio}/ES"
        logger.info(f"Solicitando datos a la API: Festivos de España - Año {anio}")
        
        try:
            respuesta = http.request('GET', url_peticion)
            
            if respuesta.status == 200:
                datos_json = json.loads(respuesta.data.decode('utf-8'))
                texto_a_guardar = json.dumps(datos_json)
                
                nombre_archivo_s3 = f"bronze/festivos/year={anio}/festivos_ES.json"
                
                try:
                    # Guardamos el archivo en el bucket
                    s3_client.put_object(
                        Bucket=BUCKET_NAME,
                        Key=nombre_archivo_s3,
                        Body=texto_a_guardar,
                        ContentType='application/json'
                    )
                    logger.info(f"Guardado OK: s3://{BUCKET_NAME}/{nombre_archivo_s3}")
                except ClientError as e:
                    # Capturamos errores si S3 rechaza la escritura por cuotas o políticas
                    logger.error(f"Fallo de escritura S3 en el año {anio}: {e}")
                    raise e
                
            else:
                # Capturamos si la API responde con error
                logger.warning(f"Error en API Nager.Date para el año {anio}: Código HTTP {respuesta.status}")
                raise Exception(f"API HTTP Error {respuesta.status}")
                
        except urllib3.exceptions.TimeoutError:
            # Controlamos errores por timeout en la conexión de la web externa
            logger.error(f"Timeout: La API de festivos ha tardado demasiado en responder para el año {anio}.")
            raise Exception("Timeout abortando ingesta")
        except Exception as e:
            # Capturamos cualquier otro error inesperado durante el procesamiento
            logger.error(f"Fallo técnico al procesar el año {anio}: {e}")
            raise Exception(f"Error técnico abortando ingesta: {str(e)}")

    logger.info("Ingesta de calendario festivo finalizada con éxito")
    
    return {
        'statusCode': 200,
        'body': json.dumps('Ingesta de calendario festivo finalizada con éxito')
    }