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
        margin-bottom: 1;
    }

    #modal-mensaje {
        text-align: center;
        color: $text;
        margin: 1 0;
    }
    """

    def compose(self) -> ComposeResult:
        with Center():
            with Vertical(id="modal-container"):
                yield Label("Procesando...", id="modal-title")
                yield LoadingIndicator()
                yield Label("Iniciando proceso ETL...", id="modal-mensaje")

    def update_message(self, mensaje: str) -> None:
        """Actualiza el mensaje de progreso.

        Debe llamarse desde el hilo principal o vía call_from_thread().
        """
        try:
            self.query_one("#modal-mensaje", Label).update(mensaje)
        except Exception:
            pass
