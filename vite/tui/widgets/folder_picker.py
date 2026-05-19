from pathlib import Path
from textual.app import ComposeResult
from textual.widget import Widget
from textual.widgets import Input, Button
from textual.containers import Horizontal
from textual.message import Message


class FolderPicker(Widget):
    """Widget para ingresar ruta de carpeta y botón Refrescar."""

    class CarpetaCambiada(Message):
        """Emitido cuando el usuario confirma una carpeta válida."""

        def __init__(self, carpeta: Path) -> None:
            super().__init__()
            self.carpeta = carpeta

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._carpeta: Path | None = None

    @property
    def carpeta_seleccionada(self) -> Path | None:
        return self._carpeta

    def compose(self) -> ComposeResult:
        with Horizontal():
            yield Input(placeholder="Ingrese la ruta de la carpeta...", id="input-carpeta")
            yield Button("↺ Refrescar", id="btn-refrescar", variant="default")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn-refrescar":
            self._validar_y_emitir()
            event.stop()

    def on_input_submitted(self, event: Input.Submitted) -> None:
        self._validar_y_emitir()

    def _validar_y_emitir(self) -> None:
        ruta = self.query_one("#input-carpeta", Input).value.strip()
        if ruta:
            carpeta = Path(ruta)
            if carpeta.is_dir():
                self._carpeta = carpeta
                self.post_message(self.CarpetaCambiada(carpeta))
            else:
                self.app.notify(f"Carpeta no encontrada: {ruta}", severity="error")
