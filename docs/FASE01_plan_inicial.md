# FASE01 - Plan Inicial: VITE - Validación de Información de Terceros Exógena

## Contexto

**¿Qué es este proyecto?**  
VITE es una aplicación ETL de escritorio (TUI) para validar la información de terceros reportada en medios magnéticos a la DIAN (Colombia). Los usuarios cargan archivos Excel de distintos formatos (1001, 1003, 1004, 1005, 1006, 1007, 1008, 2276), el sistema extrae los datos, los valida y corrige según las reglas de la DIAN, y genera un informe de salida.

**¿Por qué existe?**  
El proceso de validación de terceros para medios magnéticos es manual, propenso a errores y repetitivo. Esta herramienta automatiza la detección de inconsistencias en los datos de identificación de terceros (nombres, NIT, DV, direcciones) antes de presentar la información a la DIAN.

**Resultado esperado:**  
Una aplicación Python con TUI (Textual) que ejecuta el pipeline ETL completo y entrega al usuario un Excel con el informe de validaciones.

**Aclaraciones confirmadas por el usuario:**
- El campo `empresa_id` duplicado en las tablas `mov_*` es un typo: se elimina la columna duplicada
- `VAL_DV_01` dice "si TPDOC=13" pero es un typo; la validación correcta es "si TPDOC=31"
- Se debe crear la tabla `mov_terceros_log` para persistir el log de acciones (ACTINF/VALRES/INFOOK)
- El plan cubre el desarrollo completo (Extracción + Transformación + Carga)

---

## Stack Tecnológico

| Componente | Tecnología |
|------------|------------|
| Lenguaje | Python (última versión estable) |
| Interfaz | Textual (TUI por Textualize) |
| Base de datos | PostgreSQL 5432 — db: `vite`, user: `vite`, pass: `vite12345` |
| Excel (lectura) | Pandas + xlrd (`.xls`) + openpyxl (`.xlsx`) |
| Excel (escritura) | openpyxl |
| Web scraping DIAN | Playwright (headless Chromium) |
| Entorno virtual | Conda — entorno: `vite` |
| Arquitectura | Monolito modular |

---

## Estructura de Carpetas del Proyecto

```
vite/                                   # Raíz del repositorio
├── docs/                               # Especificaciones (ya existe)
│   ├── cfg_geografia.csv
│   ├── cfg_nomenclatura.md
│   ├── cfg_paises.csv
│   ├── FASE00_Instrucciones_iniciales_proyecto.md
│   └── FASE01_plan_inicial.md          # Este plan
│
├── vite/                               # Paquete Python principal
│   ├── __init__.py
│   ├── config/
│   │   ├── __init__.py
│   │   └── settings.py                 # Constantes: DSN, formatos, URLs, TPDOC_NATURAL=13, TPDOC_JURIDICA=31
│   │
│   ├── db/
│   │   ├── __init__.py
│   │   ├── connection.py               # Pool psycopg2 ThreadedConnectionPool + context manager
│   │   ├── schema.sql                  # DDL completo (todas las tablas)
│   │   ├── seed.sql                    # DML: datos iniciales desde docs/
│   │   └── repositories/
│   │       ├── __init__.py
│   │       ├── empresa_repo.py         # get_all(), get_by_id()
│   │       ├── periodo_repo.py         # get_all(), create(year)
│   │       ├── config_repo.py          # Lectura de todas las tablas cfg_*
│   │       ├── terceros_repo.py        # upsert, get, update de mov_terceros_*
│   │       └── log_repo.py             # insert_log() para mov_terceros_log
│   │
│   ├── etl/
│   │   ├── __init__.py                 # ViteError, ExtractionError, TransformationError, LoadError
│   │   ├── extractor.py                # Fase 1: Excel → PostgreSQL
│   │   ├── transformer.py              # Fase 2: ACTINF + VALRES + INFOOK
│   │   ├── loader.py                   # Fase 3: PostgreSQL → Excel informe
│   │   └── rules/
│   │       ├── __init__.py
│   │       ├── actinf_tpdoc.py         # inferir_tpdoc(nmdoc) → int
│   │       ├── actinf_dv.py            # calcular_dv_colombia(nit) → int
│   │       ├── actinf_direccion.py     # normalizar_direccion(dir, nomenclaturas) → (str, bool)
│   │       ├── actinf_nombres.py       # redistribuir_nombres(tercero) → dict
│   │       └── valres.py               # validar_*() + dispatcher ejecutar_validaciones()
│   │
│   ├── services/
│   │   ├── __init__.py
│   │   ├── dian_scraper.py             # Playwright → MUISCA DIAN
│   │   └── excel_parser.py             # Pandas read + openpyxl write
│   │
│   ├── tui/
│   │   ├── __init__.py
│   │   ├── app.py                      # ViteApp(App): entry point Textual
│   │   ├── screens/
│   │   │   ├── __init__.py
│   │   │   ├── main_screen.py          # Pantalla selección empresa/periodo/archivos
│   │   │   └── results_screen.py       # Pantalla resultados post-proceso
│   │   ├── widgets/
│   │   │   ├── __init__.py
│   │   │   ├── empresa_selector.py
│   │   │   ├── periodo_selector.py     # Select + botón "Crear período"
│   │   │   ├── folder_picker.py        # Input ruta + botón "Refrescar"
│   │   │   ├── file_checklist.py       # ListView con checkboxes por archivo Excel
│   │   │   └── progress_modal.py       # Modal loading con mensaje de fase actual
│   │   └── controllers/
│   │       ├── __init__.py
│   │       └── etl_controller.py       # Puente TUI ↔ ETL (asyncio worker)
│   │
│   └── utils/
│       ├── __init__.py
│       └── logging_config.py
│
├── tests/
│   ├── __init__.py
│   ├── test_actinf_tpdoc.py
│   ├── test_actinf_dv.py
│   ├── test_actinf_direccion.py
│   ├── test_actinf_nombres.py
│   └── test_valres.py
│
├── environment.yml                     # Conda env "vite"
├── pyproject.toml                      # Metadatos + dependencias pip
└── README.md                           # Guía usuario + guía instalación
```

---

## Esquema de Base de Datos

### Tablas de Configuración

```sql
-- Empresas
cfg_empresa (empresa_id SERIAL PK, empresa_desc VARCHAR NOT NULL)

-- Períodos (años)
cfg_periodo (periodo_id INTEGER PK)  -- ej: 2024, 2025, 2026

-- Campos base de terceros
cfg_campos_terceros (campo_id VARCHAR(10) PK, campo_desc VARCHAR)
-- 12 campos: TPDOC, NMDOC, DV, AP1, AP2, NM1, NM2, RZ, DIR, DPTO, MPIO, PAIS

-- Nombres de campo personalizados por empresa
cfg_campos_terceros_empresas ((campo_id, empresa_id) PK, empresa_campo VARCHAR NOT NULL)

-- Campos requeridos por formato
cfg_campos_requeridos ((campo_id, formato_id) PK, aplica BOOLEAN)  -- 96 filas: 12 campos x 8 formatos

-- Prioridad de importación por formato
cfg_prioridad_importacion (formato_id INTEGER PK, prioridad INTEGER NOT NULL)

-- Nomenclaturas de direcciones
cfg_nomenclatura (nomenclatura_id VARCHAR(10) PK, nomenclatura_palabras_clave TEXT)
-- palabras_clave: múltiples valores separados por coma (ej: "Apartamento, Aparta, Apt")

-- Países (seeded desde docs/cfg_paises.csv)
cfg_paises (pais_id VARCHAR(5) PK, pais_nombre VARCHAR)

-- Geografía Colombia (seeded desde docs/cfg_geografia.csv)
cfg_geografia ((pais_id, dpto_id, mpio_id) PK, dpto_nombre VARCHAR, mpio_nombre VARCHAR)

-- Catálogo de validaciones
cfg_validaciones (codigo VARCHAR(20) PK, descripcion TEXT)
-- VAL_TPDOC_01/02/03, VAL_DV_01, VAL_DIR_01, VAL_PAIS_01, VAL_DPTO_01, VAL_MPIO_01

-- Validaciones por formato
cfg_validaciones_formatos ((codigo, formato_id) PK)
```

### Tablas de Movimiento

```sql
-- Terceros importados (PK: empresa_id + periodo_id + NMDOC)
mov_terceros_importados (
  empresa_id  INTEGER NOT NULL,
  periodo_id  INTEGER NOT NULL,
  timestamp   TIMESTAMPTZ DEFAULT now(),
  TPDOC       VARCHAR(5),
  NMDOC       VARCHAR(20) NOT NULL,   -- siempre VARCHAR, preservar ceros a la izquierda
  DV          VARCHAR(2),
  AP1, AP2, NM1, NM2, RZ, DIR, DPTO, MPIO, PAIS  -- todos NULLABLE
  PRIMARY KEY (empresa_id, periodo_id, NMDOC)
)

-- Asociación tercero-formato (PK: empresa_id + periodo_id + NMDOC + formato)
mov_terceros_importados_formato (
  empresa_id  INTEGER NOT NULL,
  periodo_id  INTEGER NOT NULL,
  NMDOC       VARCHAR(20) NOT NULL,
  formato     INTEGER NOT NULL,
  PRIMARY KEY (empresa_id, periodo_id, NMDOC, formato)
)

-- Log de acciones del ETL
mov_terceros_log (
  log_id            SERIAL PRIMARY KEY,
  empresa_id        INTEGER NOT NULL,
  periodo_id        INTEGER NOT NULL,
  NMDOC             VARCHAR(20) NOT NULL,
  tipo_accion       VARCHAR(10) NOT NULL,   -- 'ACTINF', 'VALRES', 'INFOOK'
  codigo_validacion VARCHAR(20),
  descripcion       TEXT,
  timestamp         TIMESTAMPTZ DEFAULT now()
)
```

---

## Flujo ETL Detallado

### Fase 1: Extracción (`extractor.py`)

1. Recibe `(empresa_id, periodo_id, archivos_seleccionados[], carpeta)`
2. Extrae número de formato de cada nombre de archivo con regex `\b(1001|1003|1004|1005|1006|1007|1008|2276)\b`
3. Si algún nombre no tiene formato → lanzar `ExtractionError` con detalle
4. Ordenar archivos por `cfg_prioridad_importacion` (1008 primero → 2276 último)
5. Por cada archivo en orden:
   - Leer con `excel_parser.read_excel(path)` → DataFrame (NaN → None)
   - Obtener mapeo `empresa_campo → campo_id` desde `cfg_campos_terceros_empresas` para `empresa_id`
   - Validar que todas las columnas requeridas del formato estén en el DataFrame
   - Si falta columna → `ExtractionError("Campo '{empresa_campo}' no encontrado en Formato {nro}")`
   - Renombrar columnas del DataFrame usando el mapeo
   - Por cada fila: `upsert` en `mov_terceros_importados` y `mov_terceros_importados_formato`
   - Usar `INSERT ... ON CONFLICT DO NOTHING` para idempotencia

### Fase 2: Transformación (`transformer.py`)

**Orden de ejecución obligatorio: primero ACTINF, luego VALRES, luego INFOOK**

Pre-carga en memoria (una sola vez): nomenclaturas, geografía, países válidos, validaciones por formato

**Por cada tercero en `mov_terceros_importados`:**

#### ACTINF — Actualizaciones

| # | Módulo | Acción | Log ACTINF |
|---|--------|--------|-----------|
| 1 | `actinf_tpdoc` | Inferir TPDOC por longitud de NMDOC: <9→13, =9→31, >9→13 | Si cambia el valor |
| 2 | `actinf_dv` | Calcular DV solo si TPDOC=31 usando `calcular_dv_colombia()` | Si cambia el valor |
| 3 | `actinf_direccion` | Uppercase + reemplazar nomenclaturas (palabras completas, más largas primero). Si < 8 chars después: no aplicar | Siempre que cambie; alerta si no se pudo aplicar |
| 4 | `actinf_nombres` | TPDOC=13: poblar AP1/NM1/AP2/NM2 desde RZ si aplica, RZ→null. TPDOC=31: concatenar AP1+AP2+NM1+NM2 en RZ, limpiar campos | Si redistribuye datos |
| 5 | `dian_scraper` | Solo si aún faltan campos obligatorios según TPDOC. Consultar MUISCA con NMDOC+DV calculado | Si actualiza desde DIAN |

Caché de consultas DIAN: `dict {nmdoc: resultado}` en memoria durante la sesión para evitar duplicados.

#### VALRES — Validaciones Restrictivas (generan "Error")

**Globales (todos los formatos):**
1. TPDOC y NMDOC no pueden ser NULL
2. TPDOC=13 → AP1 y NM1 obligatorios, RZ debe ser null
3. TPDOC=31 → RZ obligatorio, AP1/AP2/NM1/NM2 deben ser null

**Específicas por formato** (ver tabla en FASE00 sección "Validaciones restrictivas"):
- `VAL_TPDOC_01`: TPDOC in {13, 31}
- `VAL_TPDOC_02`: TPDOC=13 → AP1+NM1 obligatorios, RZ=null
- `VAL_TPDOC_03`: TPDOC=31 → RZ obligatorio, AP1/AP2/NM1/NM2=null
- `VAL_DV_01`: DV not null cuando **TPDOC=31** (corregido typo del spec original)
- `VAL_DIR_01`: len(DIR) > 8 caracteres
- `VAL_PAIS_01`: PAIS in `cfg_paises.pais_id`
- `VAL_DPTO_01`: si aplican DPTO+PAIS → verificar combinación en `cfg_geografia`; si solo DPTO → verificar con PAIS=169
- `VAL_MPIO_01`: si aplican MPIO+DPTO+PAIS → verificar en `cfg_geografia`; si solo MPIO → verificar con PAIS=169

#### INFOOK
Si el tercero no tiene ningún log ACTINF ni VALRES en este proceso → registrar INFOOK

### Fase 3: Carga (`loader.py`)

Genera `Informe_validacion_terceros_{YYYYMMDD_HHMMSS}.xlsx` en la carpeta del usuario.

**Hoja 1 — Informe de validaciones:**
- Una fila por registro en `mov_terceros_log`
- Columnas: NMDOC, TPDOC, tipo_accion, codigo_validacion, descripcion
- Colores: amarillo=ACTINF, rojo=VALRES, verde=INFOOK

**Hoja 2 — Datos limpios (condicional):**
- Se genera **SOLO** si no existe ninguna fila con `tipo_accion='VALRES'` en `mov_terceros_log` para el `(empresa_id, periodo_id)` actual
- Contiene todos los campos en orden canónico de `cfg_campos_terceros`

---

## Detalles de Módulos Clave

### `actinf_dv.py` — Función `calcular_dv_colombia`
Función pura especificada exactamente en FASE00. Coeficientes DIAN: `[3, 7, 13, 17, 19, 23, 29, 37, 41, 43, 47, 53, 59, 67, 71]`. Módulo 11. Resultado > 1 → 11 - residuo, else → residuo.

### `actinf_direccion.py` — Normalización
Proceso de ordenamiento de reemplazos: expandir palabras clave separadas por coma → ordenar de más larga a más corta → compilar regex combinado con `re.IGNORECASE` → reemplazar palabras completas (`\b{palabra}\b`).

### `dian_scraper.py` — Consulta MUISCA
URL: `https://muisca.dian.gov.co/WebGestionmasiva/DefSelPublicacionesExterna.faces`
1. Navegar → cerrar modal AYUDA si aparece
2. Rellenar NIT + DV calculado → clic "Buscar"
3. Si modal ERROR → retornar `None` (dejar valores actuales)
4. Si formulario con datos → extraer campos según TPDOC (13 o 31)
5. Manejar `TimeoutError` → retornar `None` sin abortar proceso

### `etl_controller.py` — Patrón Thread-safe con Textual
```
MainScreen "Iniciar" → ETLController.ejecutar()
  → Validación rápida de nombres de archivo (sync)
  → Si error → push ErrorModal, terminar
  → push ProgressModal
  → app.run_worker(_run_etl, thread=True)
      Worker thread:
        extractor.ejecutar(callback=on_progress)
        transformer.ejecutar(callback=on_progress)
        loader.ejecutar()
      on_progress(msg) → worker.call_from_thread(modal.update_message, msg)
      Al finalizar → call_from_thread(app.pop_screen) + call_from_thread(app.push_screen, ResultsScreen)
```

---

## Orden de Implementación

### Fase A — Fundamentos
- A1. `environment.yml` + `pyproject.toml` (dependencias: textual, psycopg2, pandas, openpyxl, xlrd, playwright)
- A2. `vite/config/settings.py`
- A3. `vite/db/schema.sql` + ejecutar en psql
- A4. `vite/db/connection.py` + verificar conexión
- A5. `vite/db/seed.sql` + cargar datos de `docs/`

### Fase B — Repositorios
- B1. `empresa_repo.py` + `periodo_repo.py`
- B2. `config_repo.py` (el más crítico: carga cfg_campos, cfg_prioridad, cfg_nomenclatura, cfg_validaciones, cfg_paises, cfg_geografia)
- B3. `terceros_repo.py` + `log_repo.py`

### Fase C — Servicios de Infraestructura
- C1. `excel_parser.py` (testear con un Excel real de muestra)
- C2. `dian_scraper.py` (testear con NIT 80100491/DV=3 y NIT 811022981/DV=7)

### Fase D — Reglas de Negocio (independientes entre sí)
- D1. `actinf_dv.py` — función pura, fácil de testear
- D2. `actinf_tpdoc.py` — función pura
- D3. `actinf_nombres.py` — casos borde: distribución de palabras
- D4. `actinf_direccion.py` — probar con ejemplo del spec
- D5. `valres.py` — implementar todas las validaciones + dispatcher

### Fase E — Motor ETL
- E1. `extractor.py` (depende de B, C1, D)
- E2. `transformer.py` (depende de B, C2, D)
- E3. `loader.py` (depende de B3 para leer logs)

### Fase F — TUI
- F1. `tui/app.py` — esqueleto mínimo, verificar que Textual levanta
- F2. `empresa_selector.py` + `periodo_selector.py` (widgets con BD)
- F3. `folder_picker.py` + `file_checklist.py`
- F4. `progress_modal.py`
- F5. `etl_controller.py` — integración TUI ↔ ETL
- F6. `main_screen.py` — ensambla todos los widgets
- F7. `results_screen.py`

### Fase G — Documentación y Pruebas
- G1. Tests unitarios para todas las reglas (`tests/`)
- G2. Test de integración end-to-end con datos de prueba
- G3. `README.md` con guía de usuario e instalación

---

## Consideraciones Técnicas Críticas

### NMDOC siempre como VARCHAR
Nunca convertir NMDOC a `int`. Almacenar y procesar siempre como `str` para preservar ceros a la izquierda.

### NaN → None en Pandas
Después de leer con Pandas: `df.where(pd.notna(df), None)`. psycopg2 convierte `None` → SQL `NULL`. Las reglas de negocio verifican `IS NULL`, no `IS NaN`.

### Upsert idempotente
`INSERT ... ON CONFLICT (pk) DO NOTHING` en todas las tablas `mov_*`. El proceso es re-ejecutable sin duplicados.

### Playwright en headless mode
Requiere instalación separada: `playwright install chromium`. Documentar en README. Usar `async_playwright` para compatibilidad con el event loop asyncio de Textual.

### Concurrencia en Textual
ETL corre en worker thread del OS vía `app.run_worker(..., thread=True)`. Toda comunicación del thread hacia la UI usa `worker.call_from_thread()`. psycopg2 con `ThreadedConnectionPool` gestiona las conexiones de forma thread-safe.

### Orden de reemplazos en direcciones
Expandir keywords separados por coma → ordenar por longitud descendente → compilar un solo regex combinado con `re.IGNORECASE`. Esto evita que "Avenida" coincida antes que "Avenida calle".

---

## Verificación End-to-End

1. **Setup**: `conda activate vite` → `python -c "import textual, psycopg2, pandas, playwright"` sin errores
2. **BD**: ejecutar `schema.sql` + `seed.sql` → verificar counts en todas las tablas cfg_*
3. **Reglas unitarias**: `python -m pytest tests/ -v` → 100% pass
4. **Extractor**: preparar 2 archivos Excel de prueba (Formato 1001 y 1003) → ejecutar extractor → verificar registros en `mov_terceros_importados`
5. **Transformer**: ejecutar sobre los datos importados → verificar `mov_terceros_log` con entradas ACTINF/VALRES/INFOOK
6. **DIAN scraper**: probar manualmente con NIT 80100491 (persona natural) y NIT 811022981 (persona jurídica)
7. **Loader**: ejecutar loader → verificar Excel generado con 2 hojas (o 1 si hay VALRES)
8. **TUI completo**: `python -m vite` → navegar el flujo completo desde la selección de empresa hasta la generación del informe

---

*Plan elaborado el 2026-05-18. Aprobado e implementado.*
