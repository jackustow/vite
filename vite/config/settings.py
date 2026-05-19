import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parents[2] / ".env")

# Base de datos PostgreSQL
DB_HOST     = os.getenv("DB_HOST", "localhost")
DB_PORT     = int(os.getenv("DB_PORT", "5432"))
DB_NAME     = os.getenv("DB_NAME", "vite")
DB_USER     = os.getenv("DB_USER", "vite")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")
DB_MIN_CONN = int(os.getenv("DB_MIN_CONN", "1"))
DB_MAX_CONN = int(os.getenv("DB_MAX_CONN", "10"))

# Formatos de medios magnéticos soportados
FORMATOS_SOPORTADOS = [1001, 1003, 1004, 1005, 1006, 1007, 1008, 2276]
FORMATO_REGEX = r'\b(1001|1003|1004|1005|1006|1007|1008|2276)\b'

# Tipos de documento
TPDOC_NATURAL  = "13"   # Persona natural (cédula)
TPDOC_JURIDICA = "31"   # Persona jurídica (NIT)

# URL MUISCA DIAN para consulta de terceros
DIAN_URL = "https://muisca.dian.gov.co/WebGestionmasiva/DefSelPublicacionesExterna.faces"

# País Colombia
PAIS_COLOMBIA = "169"

# Tipos de acción ETL (log)
TIPO_ACTINF = "ACTINF"   # Actualización de información (Alerta)
TIPO_VALRES = "VALRES"   # Validación restrictiva (Error)
TIPO_INFOOK = "INFOOK"   # Información correcta (Info)

# Campos canónicos de terceros (en orden)
CAMPOS_TERCEROS = ["TPDOC", "NMDOC", "DV", "AP1", "AP2", "NM1", "NM2", "RZ", "DIR", "DPTO", "MPIO", "PAIS"]

# Longitud mínima de dirección válida (en caracteres)
DIR_MIN_LENGTH = 8
