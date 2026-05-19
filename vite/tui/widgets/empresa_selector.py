from textual.app import ComposeResult
from textual.message import Message
from textual.widget import Widget
from textual.widgets import Select
from vite.db.repositories import empresa_repo


class EmpresaSelector(Widget):
    """Widget para seleccionar empresa desde la BD."""

    class EmpresaSeleccionada(Message):
        """Evento emitido cuando cambia la empresa seleccionada."""

        def __init__(self, empresa_id: int | None) -> None:
            super().__init__()
            self.empresa_id = empresa_id

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._empresa_id: int | None = None

    @property
    def empresa_id_seleccionado(self) -> int | None:
        return self._empresa_id

    def compose(self) -> ComposeResult:
        empresas = empresa_repo.get_all()
        # Select options format: list[tuple[label, value]]
        opciones = [(e["empresa_desc"], str(e["empresa_id"])) for e in empresas]
        if not opciones:
            opciones = [("(Sin empresas configuradas)", "")]
        yield Select(opciones, prompt="Seleccione empresa...", id="select-empresa")

    def on_select_changed(self, event: Select.Changed) -> None:
        blank_value = getattr(Select, "NULL", None)
        value = event.value
        if value and value != blank_value:
            try:
                self._empresa_id = int(value)
            except (ValueError, TypeError):
                self._empresa_id = None
        else:
            self._empresa_id = None
        self.post_message(self.EmpresaSeleccionada(self._empresa_id))
