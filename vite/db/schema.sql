-- ============================================================
-- VITE - Validación de Información de Terceros Exógena
-- DDL PostgreSQL - Esquema completo
-- ============================================================

-- ============================================================
-- TABLAS DE CONFIGURACIÓN
-- ============================================================

CREATE TABLE IF NOT EXISTS cfg_empresa (
    empresa_id  SERIAL PRIMARY KEY,
    empresa_desc VARCHAR(200) NOT NULL
);

CREATE TABLE IF NOT EXISTS cfg_periodo (
    periodo_id INTEGER PRIMARY KEY
);

CREATE TABLE IF NOT EXISTS cfg_campos_terceros (
    campo_id    VARCHAR(10) PRIMARY KEY,
    campo_desc  VARCHAR(200)
);

CREATE TABLE IF NOT EXISTS cfg_campos_terceros_empresas (
    campo_id        VARCHAR(10) NOT NULL REFERENCES cfg_campos_terceros(campo_id),
    empresa_id      INTEGER     NOT NULL REFERENCES cfg_empresa(empresa_id),
    empresa_campo   VARCHAR(200) NOT NULL,
    PRIMARY KEY (campo_id, empresa_id)
);

CREATE TABLE IF NOT EXISTS cfg_campos_requeridos (
    campo_id    VARCHAR(10) NOT NULL REFERENCES cfg_campos_terceros(campo_id),
    formato_id  INTEGER     NOT NULL,
    aplica      BOOLEAN     NOT NULL DEFAULT FALSE,
    PRIMARY KEY (campo_id, formato_id)
);

CREATE TABLE IF NOT EXISTS cfg_prioridad_importacion (
    formato_id  INTEGER PRIMARY KEY,
    prioridad   INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS cfg_nomenclatura (
    nomenclatura_id             VARCHAR(10) PRIMARY KEY,
    nomenclatura_palabras_clave TEXT
);

CREATE TABLE IF NOT EXISTS cfg_paises (
    pais_id     VARCHAR(5) PRIMARY KEY,
    pais_nombre VARCHAR(200)
);

CREATE TABLE IF NOT EXISTS cfg_geografia (
    pais_id     VARCHAR(5)  NOT NULL,
    dpto_id     VARCHAR(5)  NOT NULL,
    dpto_nombre VARCHAR(200),
    mpio_id     VARCHAR(10) NOT NULL,
    mpio_nombre VARCHAR(200),
    PRIMARY KEY (pais_id, dpto_id, mpio_id)
);

CREATE TABLE IF NOT EXISTS cfg_validaciones (
    codigo      VARCHAR(20) PRIMARY KEY,
    descripcion TEXT
);

CREATE TABLE IF NOT EXISTS cfg_validaciones_formatos (
    codigo      VARCHAR(20) NOT NULL REFERENCES cfg_validaciones(codigo),
    formato_id  INTEGER     NOT NULL,
    PRIMARY KEY (codigo, formato_id)
);

-- ============================================================
-- TABLAS DE MOVIMIENTO
-- ============================================================

CREATE TABLE IF NOT EXISTS mov_terceros_importados (
    empresa_id  INTEGER     NOT NULL REFERENCES cfg_empresa(empresa_id),
    periodo_id  INTEGER     NOT NULL REFERENCES cfg_periodo(periodo_id),
    ts          TIMESTAMPTZ DEFAULT now(),
    tpdoc       VARCHAR(5),
    nmdoc       VARCHAR(20) NOT NULL,
    dv          VARCHAR(2),
    ap1         VARCHAR(100),
    ap2         VARCHAR(100),
    nm1         VARCHAR(100),
    nm2         VARCHAR(100),
    rz          VARCHAR(500),
    dir         VARCHAR(500),
    dpto        VARCHAR(5),
    mpio        VARCHAR(10),
    pais        VARCHAR(5),
    PRIMARY KEY (empresa_id, periodo_id, nmdoc)
);

CREATE TABLE IF NOT EXISTS mov_terceros_importados_formato (
    empresa_id  INTEGER     NOT NULL,
    periodo_id  INTEGER     NOT NULL,
    nmdoc       VARCHAR(20) NOT NULL,
    formato     INTEGER     NOT NULL,
    PRIMARY KEY (empresa_id, periodo_id, nmdoc, formato),
    FOREIGN KEY (empresa_id, periodo_id, nmdoc)
        REFERENCES mov_terceros_importados(empresa_id, periodo_id, nmdoc)
);

CREATE TABLE IF NOT EXISTS mov_terceros_log (
    log_id              SERIAL      PRIMARY KEY,
    empresa_id          INTEGER     NOT NULL,
    periodo_id          INTEGER     NOT NULL,
    nmdoc               VARCHAR(20) NOT NULL,
    tipo_accion         VARCHAR(10) NOT NULL
                            CHECK (tipo_accion IN ('ACTINF', 'VALRES', 'INFOOK')),
    codigo_validacion   VARCHAR(20),
    descripcion         TEXT,
    ts                  TIMESTAMPTZ DEFAULT now()
);

-- ============================================================
-- ÍNDICES DE PERFORMANCE
-- ============================================================

CREATE INDEX IF NOT EXISTS idx_log_empresa_periodo
    ON mov_terceros_log(empresa_id, periodo_id);

CREATE INDEX IF NOT EXISTS idx_mti_empresa_periodo
    ON mov_terceros_importados(empresa_id, periodo_id);

CREATE INDEX IF NOT EXISTS idx_mtif_empresa_periodo
    ON mov_terceros_importados_formato(empresa_id, periodo_id, nmdoc);
