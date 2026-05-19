from textual.app import ComposeResult
from textual.message import Message
from textual.widget import Widget
from textual.widgets import Select, Button, Input
from textual.containers import Horizontal
from vite.db.repositories import periodo_repo


class PeriodoSelector(Widget):
    """Widget para seleccionar o crear un período (año)."""

    _NO_PERIODOS_VALUE = "__NO_PERIODOS__"

    class PeriodoSeleccionado(Message):
        def __init__(self, periodo_id: int | None) -> None:
            super().__init__()
            self.periodo_id = periodo_id

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._periodo: int | None = None
        self._creando = False
        self._periodos: list[int] = []
        self._habilitado = False

    @property
    def periodo_seleccionado(self) -> int | None:
        return self._periodo

    def compose(self) -> ComposeResult:
        self._periodos = periodo_repo.get_all()
        opciones = self._build_options(self._periodos)
        with Horizontal():
            yield Select(opciones, prompt="Seleccione período...", id="select-periodo")
            yield Button("+ Nuevo", id="btn-nuevo-periodo", variant="default")
        yield Input(placeholder="Año (ej: 2026)", id="input-nuevo-periodo")
        yield Button("Crear", id="btn-crear-periodo", variant="primary")

    def on_mount(self) -> None:
        self.query_one("#input-nuevo-periodo").display = False
        self.query_one("#btn-crear-periodo").display = False
        self.set_enabled(self._habilitado)

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
                self.post_message(self.PeriodoSeleccionado(año))
            else:
                self.app.notify("Ingrese un año válido (2000-2100)", severity="error")
            event.stop()

    def _refrescar_periodos(self, seleccionar: int | None = None) -> None:
        self._periodos = periodo_repo.get_all()
        opciones = self._build_options(self._periodos)
        select = self.query_one("#select-periodo", Select)
        select.set_options(opciones)
        if seleccionar is not None and seleccionar in self._periodos:
            select.value = str(seleccionar)
            self._periodo = seleccionar
        else:
            self._periodo = None
        self.post_message(self.PeriodoSeleccionado(self._periodo))

    def refrescar_desde_cfg_periodo(self) -> None:
        """Recarga la lista de periodos desde la tabla cfg_periodo."""
        self._refrescar_periodos()

    def tiene_periodos(self) -> bool:
        return bool(self._periodos)

    def abrir_desplegable(self) -> None:
        """Enfoca y abre el desplegable de período."""
        if not self._habilitado:
            return
        select = self.query_one("#select-periodo", Select)
        select.focus()
        show_overlay = getattr(select, "action_show_overlay", None)
        if callable(show_overlay):
            show_overlay()

    def mostrar_creacion_periodo(self) -> None:
        """Muestra el input para crear período cuando no hay datos en cfg_periodo."""
        if not self._habilitado:
            return
        self._creando = True
        self.query_one("#input-nuevo-periodo").display = True
        self.query_one("#btn-crear-periodo").display = True
        self.query_one("#input-nuevo-periodo", Input).focus()

    def set_enabled(self, enabled: bool) -> None:
        self._habilitado = enabled
        if not self.is_mounted:
            return
        self.query_one("#select-periodo", Select).disabled = not enabled
        self.query_one("#btn-nuevo-periodo", Button).disabled = not enabled
        self.query_one("#input-nuevo-periodo", Input).disabled = not enabled
        self.query_one("#btn-crear-periodo", Button).disabled = not enabled

    def on_select_changed(self, event: Select.Changed) -> None:
        blank_value = getattr(Select, "NULL", None)
        value = event.value
        if value and value != blank_value and value != self._NO_PERIODOS_VALUE:
            try:
                self._periodo = int(value)
            except (ValueError, TypeError):
                self._periodo = None
        else:
            self._periodo = None
        self.post_message(self.PeriodoSeleccionado(self._periodo))

    def _build_options(self, periodos: list[int]) -> list[tuple[str, str]]:
        if not periodos:
            return [("No hay períodos en cfg_periodo (use + Nuevo)", self._NO_PERIODOS_VALUE)]
        return [(str(p), str(p)) for p in periodos]
