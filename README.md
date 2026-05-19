# VITE — Validación de Información de Terceros Exógena

Aplicación de escritorio (TUI) para validar los datos de terceros que se reportan en medios magnéticos a la **DIAN Colombia**. Carga archivos Excel de los formatos 1001, 1003, 1004, 1005, 1006, 1007, 1008 y 2276, ejecuta un pipeline ETL completo y genera un informe de validaciones en Excel.

---

## Requisitos previos

| Herramienta | Versión mínima |
|-------------|---------------|
| Conda (Miniconda / Anaconda) | cualquiera reciente |
| PostgreSQL | 14+ corriendo en `localhost:5432` |
| Git | cualquiera |

---

## Instalación

### 1. Clonar el repositorio

```bash
git clone <url-del-repositorio>
cd vite
```

### 2. Crear el entorno Conda

```bash
conda env create -f environment.yml
conda activate vite
```

### 3. Instalar el paquete en modo editable

```bash
pip install -e .
```

### 4. Instalar Chromium para Playwright

```bash
playwright install chromium
```

### 5. Crear la base de datos PostgreSQL

Conectarse a PostgreSQL como superusuario y ejecutar:

```sql
CREATE USER vite WITH PASSWORD 'vite12345';
CREATE DATABASE vite OWNER vite;
```

### 6. Crear el esquema

```bash
psql -U vite -d vite -f vite/db/schema.sql
```

### 7. Cargar los datos iniciales

```bash
psql -U vite -d vite -f vite/db/seed.sql
```

Los datos de catálogo (países, geografía de Colombia, nomenclaturas de direcciones) se cargan desde los archivos en `docs/`.

---

## Configuración de empresas y períodos

Los datos de empresa se gestionan directamente en la tabla `cfg_empresa` de la base de datos:

```sql
-- Agregar una empresa
INSERT INTO cfg_empresa (empresa_desc) VALUES ('Mi Empresa S.A.S.');

-- Agregar los nombres de campo personalizados que usa esa empresa en sus Excel
-- (campo_id: TPDOC, NMDOC, DV, AP1, AP2, NM1, NM2, RZ, DIR, DPTO, MPIO, PAIS)
INSERT INTO cfg_campos_terceros_empresas (campo_id, empresa_id, empresa_campo)
VALUES ('NMDOC', 1, 'NIT'), ('AP1', 1, 'Primer Apellido'), ...;
```

Los períodos (años) se crean desde la misma aplicación usando el botón **"+ Nuevo período"**.

---

## Ejecución

```bash
conda activate vite
python -m vite
```

O, si el paquete está instalado:

```bash
vite
```

---

## Flujo de uso

1. **Seleccionar empresa** en el selector desplegable.
2. **Seleccionar período** (año). Si el período no existe, usar **"+ Nuevo período"**.
3. **Seleccionar carpeta** que contiene los archivos Excel a procesar.
4. **Marcar los archivos** de la lista que deben incluirse en el proceso.
5. Pulsar **"▶ Iniciar proceso"**.
6. Esperar a que el pipeline ETL finalice (pantalla de progreso).
7. El informe `Informe_validacion_terceros_YYYYMMDD_HHMMSS.xlsx` se genera en la misma carpeta de los archivos de entrada.

**Tecla `Q`** — salir de la aplicación en cualquier momento.

---

## Formatos de archivo Excel soportados

Los nombres de archivo deben contener el número de formato en el nombre:

| Formato | Ejemplo de nombre de archivo |
|---------|------------------------------|
| 1001 | `Formato_1001_2024.xlsx` |
| 1003 | `reporte1003.xls` |
| 1004 | `1004_empresa.xlsx` |
| 1005 | `datos_1005.xlsx` |
| 1006 | `1006.xlsx` |
| 1007 | `1007_terceros.xlsx` |
| 1008 | `1008_dic2024.xlsx` |
| 2276 | `2276_anual.xlsx` |

Los archivos cuyo nombre no contenga un número de formato válido se rechazarán antes de iniciar el proceso.

---

## Informe de salida

El archivo Excel generado contiene:

- **Hoja 1 — Informe de validaciones:** una fila por acción registrada.
  - Fondo **amarillo** → corrección automática (ACTINF)
  - Fondo **rojo** → error que requiere corrección manual (VALRES)
  - Fondo **verde** → registro sin observaciones (INFOOK)

- **Hoja 2 — Datos limpios:** exporta todos los terceros procesados con sus campos corregidos. **Solo se genera si no existen errores VALRES**, es decir, si todos los registros están listos para presentar a la DIAN.

---

## Pruebas unitarias

```bash
conda activate vite
pytest tests/ -v
```

---

## Estructura del proyecto

```
vite/
├── docs/                   # Especificaciones y datos de catálogo
├── vite/                   # Paquete Python principal
│   ├── config/             # Constantes y configuración
│   ├── db/                 # Conexión, esquema SQL y repositorios
│   ├── etl/                # Pipeline ETL + reglas de negocio
│   ├── services/           # Excel parser y scraper DIAN
│   ├── tui/                # Interfaz TUI (Textual)
│   └── utils/              # Logging
├── tests/                  # Pruebas unitarias
├── environment.yml         # Entorno Conda
└── pyproject.toml          # Metadatos del paquete
```

---

## Notas técnicas

- **NMDOC siempre como texto:** los NIT se almacenan como `VARCHAR` para preservar ceros a la izquierda.
- **Proceso idempotente:** se puede re-ejecutar sobre los mismos archivos sin crear duplicados.
- **Caché DIAN:** cada NIT se consulta en MUISCA una sola vez por sesión.
- **TPDOC inferido:** si el campo TPDOC llega vacío, se infiere por longitud del NMDOC (9 dígitos → jurídica=31, resto → natural=13).
- **DV calculado:** el dígito de verificación se recalcula automáticamente para personas jurídicas usando el algoritmo oficial de la DIAN.
