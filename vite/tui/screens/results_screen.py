from pathlib import Path
from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Header, Footer, Button, Label
from textual.containers import Container


class ResultsScreen(Screen):
    """Pantalla de resultados post-proceso ETL."""

    def __init__(self, output_path: Path | None, error: str | None = None, **kwargs):
        super().__init__(**kwargs)
        self._output_path = output_path
        self._error = error

    def compose(self) -> ComposeResult:
        yield Header()
        with Container(id="results-container"):
            if self._error:
                yield Label("El proceso terminó con errores", classes="section-title error-label")
                yield Label(self._error)
            else:
                yield Label("Proceso ETL completado exitosamente", classes="section-title")
                if self._output_path:
                    yield Label(f"Informe generado: {self._output_path}")

            yield Button("Volver al inicio", id="btn-volver", variant="primary")
        yield Footer()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn-volver":
            self.app.pop_screen()
