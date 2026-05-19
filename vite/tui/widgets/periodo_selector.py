from textual.app import ComposeResult
from textual.widget import Widget
from textual.widgets import Select, Button, Input
from textual.containers import Horizontal
from vite.db.repositories import periodo_repo


class PeriodoSelector(Widget):
    """Widget para seleccionar o crear un período (año)."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._periodo: int | None = None
        self._creando = False

    @property
    def periodo_seleccionado(self) -> int | None:
        return self._periodo

    def compose(self) -> ComposeResult:
        periodos = periodo_repo.get_all()
        # Select options format: list[tuple[label, value]]
        opciones = [(str(p), str(p)) for p in periodos]
        if not opciones:
            opciones = [("(Sin períodos)", "")]
        with Horizontal():
            yield Select(opciones, prompt="Seleccione período...", id="select-periodo")
            yield Button("+ Nuevo", id="btn-nuevo-periodo", variant="default")
        yield Input(placeholder="Año (ej: 2026)", id="input-nuevo-periodo")
        yield Button("Crear", id="btn-crear-periodo", variant="primary")

    def on_mount(self) -> None:
        self.query_one("#input-nuevo-periodo").display = False
        self.query_one("#btn-crear-periodo").display = False

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn-nuevo-periodo":
            mostrar = not self._creando
            self._creando = mostrar
            self.query_one("#input-nuevo-periodo").display = mostrar
            self.query_one("#btn-crear-periodo").display = mostrar
            event.stop()

        elif event.button.id == "btn-crear-periodo":
            input_widget = self.query_one("#input-nuevo-periodo", Input)
            año_str = input_widget.value.strip()
            if año_str.isdigit() and 2000 <= int(año_str) <= 2100:
                año = int(año_str)
                periodo_repo.create(año)
                self._refrescar_periodos(año)
                input_widget.value = ""
                self.query_one("#input-nuevo-periodo").display = False
                self.query_one("#btn-crear-periodo").display = False
                self._creando = False
                self.app.notify(f"Período {año} creado", severity="information")
            else:
                self.app.notify("Ingrese un año válido (2000-2100)", severity="error")
            event.stop()

    def _refrescar_periodos(self, seleccionar: int | None = None) -> None:
        periodos = periodo_repo.get_all()
        # set_options accepts Iterable[tuple[RenderableType, SelectType]]
        opciones = [(str(p), str(p)) for p in periodos]
        select = self.query_one("#select-periodo", Select)
        select.set_options(opciones)
        if seleccionar is not None:
            select.value = str(seleccionar)
            self._periodo = seleccionar

    def on_select_changed(self, event: Select.Changed) -> None:
        if event.value and event.value != Select.BLANK:
            try:
                self._periodo = int(event.value)
            except (ValueError, TypeError):
                self._periodo = None
        else:
            self._periodo = None
