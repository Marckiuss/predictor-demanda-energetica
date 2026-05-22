# Predictor de demanda para redes eléctricas

Proyecto para el **Curso de Especialización en IA y Big Data - IES San Andrés**. 

El objetivo de este proyecto es montar un sistema automático que recoja información de la Red Eléctrica de España (REE), datos del clima y el calendario de festivos. Con todo esto bien ordenado y limpio, preparamos el terreno para poder entrenar un modelo que sea capaz de predecir el consumo eléctrico en nuestro país.

## Arquitectura del Proyecto

Todo el proceso sigue los pasos de la metodología **CRISP-DM** y organiza los datos en tres niveles (Arquitectura Medallón), repartiendo el trabajo entre la nube y nuestro ordenador:

* **Capa Bronce (AWS S3):** Datos en bruto.
* **Capa Plata (Local):** Datos procesados: limpieza de errores, transformación de columnas y organización por carpetas usando Python y Pandas.
* **Capa Oro (Local HDFS):** Datos finales en formato Parquet para el modelo predictivo, almacenados de forma segura en un servidor Hadoop levantado en local con Docker.

## Fuentes de Datos

Para este proyecto se han cruzado tres piezas de información clave:
1. **Consumo eléctrico (ESIOS):** La demanda energética real de la península con granularidad horaria obtenida directamente de la API de la Red Eléctrica Nacional.
2. **El clima (AEMET):** Histórico de temperaturas, viento y lluvia de la península que descargamos desde *datosclima.es*.
3. **Calendario de festivos:**

## Estructura del Repositorio

Dentro de este repositorio te vas a encontrar lo siguiente:

* `/scripts/`: Ficheros python encargados de ejecutar las acciones necesarias para el desarrollo del proyecto:
    * `01-lambda_s3_ingesta_esios_bronze.py`: Descarga el consumo y lo sube a AWS.
    * `02-lambda_s3_ingesta_festivos.py`: carga el calendario en AWS.
    * `03-Integracion_datasets_clima.py`:   Ordena los ficheros del clima en nuestro ordenador y los prepara para la subida a AWS.
    * `04-preparacion_capas_plata_y_oro.ipynb`: Cuaderno de trabajo donde se realiza la limpieza y transformación de los diferentes conjuntos de datos.
* `/documentacion/`: Memoria detallada del proyecto siguiendo las fases CRISP-DM y el diccionario de datos explicando cada columna de la tabla final.
* `/dashboard/`: Cuadro de mando visual y capturas de los resultados.
* `docker-compose.yml`: Archivo de configuración para arrancar Hadoop.

## Cómo ejecutar el proyecto

**1. Encender el almacenamiento local**
Teniendo Docker instalado en tu ordenador, abre una terminal en la carpeta raíz del proyecto y ejecuta docker-compose up -d para arrancar hadoop