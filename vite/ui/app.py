"""Interfaz Streamlit — VITE: Validación de Información de Terceros Exógena."""
from pathlib import Path

import streamlit as st
from loguru import logger

from vite.db.repositories import empresa_repo, periodo_repo
from vite.etl import ExtractionError, LoadError, TransformationError
from vite.etl import extractor, loader, transformer
from vite.utils.logging_config import setup_logging

# ---------------------------------------------------------------------------
# Estado de sesión
# ---------------------------------------------------------------------------

_DEFAULTS: dict = {
    "empresa_id": None,
    "empresa_desc": "",
    "periodo_id": None,
    "carpeta": None,
    "archivos_disponibles": [],
    "archivos_seleccionados": [],
    "etl_completado": False,
    "etl_error": None,
    "output_path": None,
}


def _init_state() -> None:
    for key, value in _DEFAULTS.items():
        if key not in st.session_state:
            st.session_state[key] = value


def _reset_state() -> None:
    for key in _DEFAULTS:
        st.session_state.pop(key, None)
    # Limpiar también las claves de widgets
    for key in list(st.session_state.keys()):
        if key.startswith(("_empresa_", "_periodo_", "_carpeta_", "_btn_", "_file_")):
            st.session_state.pop(key, None)


# ---------------------------------------------------------------------------
# Punto de entrada
# ---------------------------------------------------------------------------

def main() -> None:
    setup_logging()
    st.set_page_config(
        page_title="VITE - Validación de Terceros",
        page_icon="📊",
        layout="centered",
    )
    _init_state()

    st.title("VITE")
    st.caption(
        "Validación de Información de Terceros Exógena · "
        "Medios Magnéticos DIAN Colombia"
    )
    st.divider()

    if st.session_state.etl_completado or st.session_state.etl_error is not None:
        _vista_resultados()
    else:
        _vista_configuracion()


# ---------------------------------------------------------------------------
# Vista: configuración
# ---------------------------------------------------------------------------

def _vista_configuracion() -> None:
    _seccion_empresa()

    if st.session_state.empresa_id:
        _seccion_periodo()

    if st.session_state.periodo_id:
        _seccion_carpeta()

    if st.session_state.carpeta:
        _seccion_archivos()

    puede_iniciar = (
        st.session_state.empresa_id is not None
        and st.session_state.periodo_id is not None
        and st.session_state.carpeta is not None
        and len(st.session_state.archivos_seleccionados) > 0
    )

    st.divider()
    if st.button(
        "▶ Iniciar proceso",
        type="primary",
        disabled=not puede_iniciar,
        use_container_width=True,
    ):
        _ejecutar_etl()


def _seccion_empresa() -> None:
    st.subheader("1. Empresa")

    try:
        empresas = empresa_repo.get_all()
    except Exception as exc:
        logger.error("Error cargando empresas: {}", exc)
        st.error(f"No se pudo cargar la lista de empresas: {exc}")
        return

    if not empresas:
        st.warning("No hay empresas configuradas en la base de datos.")
        return

    opciones: dict[str, int | None] = {"": None} | {
        e["empresa_desc"]: e["empresa_id"] for e in empresas
    }

    def _on_change_empresa() -> None:
        sel = st.session_state["_empresa_sel"]
        nuevo_id = opciones.get(sel)
        if nuevo_id != st.session_state.empresa_id:
            st.session_state.empresa_id = nuevo_id
            st.session_state.empresa_desc = sel if nuevo_id else ""
            st.session_state.periodo_id = None
            st.session_state.carpeta = None
            st.session_state.archivos_disponibles = []
            st.session_state.archivos_seleccionados = []
            logger.info("Empresa seleccionada: {} (id={})", sel, nuevo_id)

    st.selectbox(
        "Seleccione la empresa",
        options=list(opciones.keys()),
        key="_empresa_sel",
        on_change=_on_change_empresa,
    )


def _seccion_periodo() -> None:
    st.subheader("2. Período")

    try:
        periodos = periodo_repo.get_all()
    except Exception as exc:
        logger.error("Error cargando períodos: {}", exc)
        st.error(f"No se pudo cargar la lista de períodos: {exc}")
        return

    if periodos:
        # periodos es list[int]: cada elemento es el año = periodo_id
        opciones_per: dict[str, int | None] = {"": None} | {
            str(p): p for p in periodos
        }
        opciones_lista = list(opciones_per.keys()) + ["+ Nuevo período"]

        def _on_change_periodo() -> None:
            sel = st.session_state["_periodo_sel"]
            if sel in ("", "+ Nuevo período"):
                nuevo_id = None
            else:
                nuevo_id = opciones_per.get(sel)
            if nuevo_id != st.session_state.periodo_id:
                st.session_state.periodo_id = nuevo_id
                st.session_state.carpeta = None
                st.session_state.archivos_disponibles = []
                st.session_state.archivos_seleccionados = []
                if nuevo_id:
                    logger.info("Período seleccionado: {}", nuevo_id)

        st.selectbox(
            "Seleccione el año",
            options=opciones_lista,
            key="_periodo_sel",
            on_change=_on_change_periodo,
        )

        if st.session_state.get("_periodo_sel") == "+ Nuevo período":
            _form_nuevo_periodo()
    else:
        st.warning("No hay períodos configurados. Cree uno para continuar.")
        _form_nuevo_periodo()


def _form_nuevo_periodo() -> None:
    with st.form("form_nuevo_periodo", clear_on_submit=True):
        anio = st.number_input(
            "Año", min_value=2000, max_value=2099, value=2024, step=1
        )
        if st.form_submit_button("Crear período"):
            try:
                periodo_repo.create(int(anio))
                st.session_state.periodo_id = int(anio)
                logger.info("Período {} creado.", anio)
                st.rerun()
            except Exception as exc:
                logger.error("Error creando período {}: {}", anio, exc)
                st.error(f"Error al crear el período: {exc}")


def _abrir_dialogo_carpeta() -> str:
    """Abre el explorador de carpetas nativo del sistema operativo."""
    import tkinter as tk
    from tkinter import filedialog

    root = tk.Tk()
    root.withdraw()
    root.wm_attributes("-topmost", 1)
    carpeta = filedialog.askdirectory(title="Seleccionar carpeta de archivos Excel")
    root.destroy()
    return carpeta


def _seccion_carpeta() -> None:
    st.subheader("3. Carpeta de archivos")

    if st.button("📁 Seleccionar carpeta...", key="_btn_carpeta"):
        ruta = _abrir_dialogo_carpeta()
        if ruta:
            p = Path(ruta)
            archivos = sorted(list(p.glob("*.xlsx")) + list(p.glob("*.xls")))
            st.session_state.carpeta = p
            st.session_state.archivos_disponibles = archivos
            st.session_state.archivos_seleccionados = []
            logger.info(
                "Carpeta seleccionada: {} ({} archivo(s) Excel encontrado(s))",
                p, len(archivos),
            )
            st.rerun()

    if st.session_state.carpeta:
        st.info(f"📂 **Carpeta seleccionada:** `{st.session_state.carpeta}`")
    else:
        st.caption("Ninguna carpeta seleccionada.")


def _seccion_archivos() -> None:
    st.subheader("4. Archivos Excel")
    archivos: list[Path] = st.session_state.archivos_disponibles

    if not archivos:
        st.warning(
            "No se encontraron archivos Excel (.xlsx / .xls) en la carpeta."
        )
        return

    todos = st.checkbox("Seleccionar todos", key="_file_todos")

    seleccionados: list[Path] = []
    for archivo in archivos:
        marcado = st.checkbox(
            archivo.name,
            key=f"_file_{archivo.stem}",
            value=todos,
        )
        if marcado:
            seleccionados.append(archivo)

    st.session_state.archivos_seleccionados = seleccionados

    st.caption(f"{len(seleccionados)} de {len(archivos)} archivo(s) seleccionado(s)")


# ---------------------------------------------------------------------------
# Ejecución ETL
# ---------------------------------------------------------------------------

def _ejecutar_etl() -> None:
    empresa_id: int = st.session_state.empresa_id
    periodo_id: int = st.session_state.periodo_id
    carpeta: Path = st.session_state.carpeta
    archivos: list[Path] = st.session_state.archivos_seleccionados

    logger.info(
        "ETL iniciado — empresa={}, periodo={}, archivos={}",
        empresa_id,
        periodo_id,
        [a.name for a in archivos],
    )

    with st.status("Ejecutando proceso ETL...", expanded=True) as status:
        try:
            st.write("**Fase 1 — Extracción de datos**")
            extractor.ejecutar(
                empresa_id,
                periodo_id,
                archivos,
                callback=lambda msg: st.write(f"→ {msg}"),
            )

            st.write("**Fase 2 — Transformación y validaciones**")
            transformer.ejecutar(
                empresa_id,
                periodo_id,
                callback=lambda msg: st.write(f"→ {msg}"),
            )

            st.write("**Fase 3 — Generación de informe**")
            output_path = loader.ejecutar(
                empresa_id,
                periodo_id,
                carpeta,
                callback=lambda msg: st.write(f"→ {msg}"),
            )

            status.update(label="ETL completado exitosamente ✔", state="complete")
            st.session_state.etl_completado = True
            st.session_state.output_path = output_path
            st.session_state.etl_error = None
            logger.info("ETL finalizado. Informe: {}", output_path)

        except (ExtractionError, TransformationError, LoadError) as exc:
            status.update(label="Error en el proceso ETL", state="error")
            st.session_state.etl_error = str(exc)
            st.session_state.etl_completado = False
            logger.error("Error ETL: {}", exc)

        except Exception as exc:
            status.update(label="Error inesperado", state="error")
            st.session_state.etl_error = f"Error inesperado: {exc}"
            st.session_state.etl_completado = False
            logger.exception("Error inesperado en ETL")

    st.rerun()


# ---------------------------------------------------------------------------
# Vista: resultados
# ---------------------------------------------------------------------------

def _vista_resultados() -> None:
    if st.session_state.etl_error:
        st.error("El proceso ETL terminó con errores")
        st.code(st.session_state.etl_error, language=None)
    else:
        st.success("Proceso ETL completado exitosamente")
        output_path: Path | None = st.session_state.output_path
        if output_path:
            output_path = Path(output_path)
            st.info(f"Informe generado: `{output_path}`")
            if output_path.exists():
                with open(output_path, "rb") as fh:
                    st.download_button(
                        label="⬇ Descargar informe Excel",
                        data=fh,
                        file_name=output_path.name,
                        mime=(
                            "application/vnd.openxmlformats-officedocument"
                            ".spreadsheetml.sheet"
                        ),
                        type="primary",
                    )

    st.divider()
    if st.button("↩ Volver al inicio", use_container_width=True):
        _reset_state()
        st.rerun()


# ---------------------------------------------------------------------------
# Ejecución del script por Streamlit
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    main()
