from pathlib import Path
from vite.etl import extractor, transformer, loader
from vite.etl import ExtractionError, TransformationError, LoadError
from vite.tui.widgets.progress_modal import ProgressModal
from vite.tui.screens.results_screen import ResultsScreen


class ETLController:
    """Ejecuta el pipeline ETL completo en un worker thread de Textual.

    Usa run_worker(thread=True) para no bloquear el event loop de Textual.
    La comunicación de vuelta al hilo principal se hace con call_from_thread().
    """

    def __init__(self, app):
        self._app = app

    def ejecutar(
        self,
        empresa_id: int,
        periodo_id: int,
        carpeta: Path,
        archivos: list[Path],
    ) -> None:
        """Abre el modal de progreso e inicia el proceso ETL en background."""
        modal = ProgressModal()
        self._app.push_screen(modal)

        def _run():
            output_path: Path | None = None
            error_msg: str | None = None

            def on_progress(msg: str) -> None:
                # call_from_thread es thread-safe en Textual 8.x
                self._app.call_from_thread(modal.update_message, msg)

            try:
                extractor.ejecutar(empresa_id, periodo_id, archivos, callback=on_progress)
                transformer.ejecutar(empresa_id, periodo_id, callback=on_progress)
                output_path = loader.ejecutar(
                    empresa_id, periodo_id, carpeta, callback=on_progress
                )
            except (ExtractionError, TransformationError, LoadError) as exc:
                error_msg = str(exc)
            except Exception as exc:
                error_msg = f"Error inesperado: {exc}"

            # Finalizar siempre desde el hilo principal
            self._app.call_from_thread(self._finalizar, modal, output_path, error_msg)

        # run_worker signature: (work, ..., thread=False)
        self._app.run_worker(_run, thread=True, name="etl-worker")

    def _finalizar(
        self,
        modal: ProgressModal,
        output_path: Path | None,
        error_msg: str | None,
    ) -> None:
        """Cierra el modal y muestra la pantalla de resultados (ejecutado en el hilo principal)."""
        self._app.pop_screen()  # cierra ProgressModal
        self._app.push_screen(ResultsScreen(output_path, error_msg))
