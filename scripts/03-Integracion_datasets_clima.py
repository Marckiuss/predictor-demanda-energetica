### Unifica los archivos del conjunto de datos de histórico climático y lo estructura en formato Hive para carharlos en AWS.
import os
import glob
import shutil

CARPETA_LOCAL = "./data/bronze/clima/"
CARPETA_SALIDA = "./data/bronze/clima/clima_s3_preparado"

ficheros = glob.glob(f"{CARPETA_LOCAL}**/*.xls*", recursive=True)
print(f"Organizando {len(ficheros)} archivos localmente...\n")

archivos_movidos = 0

for ruta_local in ficheros:
    nombre_archivo = os.path.basename(ruta_local)

    try:
        fecha_str = nombre_archivo.replace("Aemet", "").split(".")[0]
        partes = fecha_str.split("-")

        if len(partes) == 3:
            year = partes[0]
            month = partes[1]
            day = partes[2]

            # Recreamos la estructura Hive para S3
            ruta_destino = os.path.join(
                CARPETA_SALIDA,
                f"year={year}",
                f"month={month}",
                f"day={day}",
            )

            # Crea las carpetas si no existen
            os.makedirs(ruta_destino, exist_ok=True)

            # Copia el archivo a su nueva carpeta
            shutil.copy2(ruta_local, os.path.join(ruta_destino, nombre_archivo))
            archivos_movidos += 1

    except Exception as e:
        print(f"Error al mover {nombre_archivo}: {e}")

print(
    f"\n Integración realizada con éxito. {archivos_movidos} archivos unificados."
)