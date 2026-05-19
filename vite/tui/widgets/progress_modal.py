from textual.app import ComposeResult
from textual.screen import ModalScreen
from textual.widgets import Label, LoadingIndicator
from textual.containers import Center, Vertical


class ProgressModal(ModalScreen):
    """Modal de progreso ETL. No tiene botón de cierre — se cierra programáticamente."""

    DEFAULT_CSS = """
    ProgressModal {
        align: center middle;
    }

    #modal-container {
        background: $surface;
        border: thick $primary;
        padding: 2 4;
        width: 60;
        height: auto;
        min-height: 10;
    }

    #modal-title {
        text-style: bold;
        color: $primary;
        text-align: center;
        margin-bottom: 0;
    }

    #modal-proceso {
        text-style: bold;
        color: $accent;
        text-align: center;
        margin: 1 0 0 0;
    }

    #modal-mensaje {
        text-align: center;
        color: $text;
        margin: 0;
    }
    """

    def compose(self) -> ComposeResult:
        with Center():
            with Vertical(id="modal-container"):
                yield Label("Procesando ETL...", id="modal-title")
                yield LoadingIndicator()
                yield Label("Proceso actual: Inicialización", id="modal-proceso")
                yield Label("Iniciando proceso ETL...", id="modal-mensaje")

    def update_status(self, proceso: str, mensaje: str) -> None:
        """Actualiza nombre de proceso y mensaje de progreso.

        Debe llamarse desde el hilo principal o vía call_from_thread().
        """
        try:
            self.query_one("#modal-proceso", Label).update(
                f"Proceso actual: {proceso}"
            )
            self.query_one("#modal-mensaje", Label).update(mensaje)
        except Exception:
            pass

    def update_message(self, mensaje: str) -> None:
        """Compatibilidad: actualiza solo el mensaje."""
        self.update_status("En ejecución", mensaje)
