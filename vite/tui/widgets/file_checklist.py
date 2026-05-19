from pathlib import Path
from textual.app import ComposeResult
from textual.message import Message
from textual.widget import Widget
from textual.widgets import SelectionList
from textual.widgets.selection_list import Selection


class FileChecklist(Widget):
    """Lista de archivos Excel con selección múltiple."""

    class SeleccionArchivosCambiada(Message):
        def __init__(self, archivos: list[Path]) -> None:
            super().__init__()
            self.archivos = archivos

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._archivos: list[Path] = []
        self._habilitado = False

    @property
    def archivos_seleccionados(self) -> list[Path]:
        if not self.is_mounted:
            return []
        selected = self.query_one("#selection-archivos", SelectionList).selected
        return list(selected)

    def compose(self) -> ComposeResult:
        yield SelectionList[Path](id="selection-archivos", disabled=True)

    def set_enabled(self, enabled: bool) -> None:
        self._habilitado = enabled
        if self.is_mounted:
            self.query_one("#selection-archivos", SelectionList).disabled = not enabled

    def cargar_desde_carpeta(self, carpeta: Path | None) -> None:
        if not self.is_mounted:
            return
        selection = self.query_one("#selection-archivos", SelectionList)
        selection.clear_options()
        self._archivos = []
        if carpeta is None:
            self.post_message(self.SeleccionArchivosCambiada([]))
            return

        self._archivos = sorted(list(carpeta.glob("*.xlsx")) + list(carpeta.glob("*.xls")))
        if not self._archivos:
            self.post_message(self.SeleccionArchivosCambiada([]))
            return

        selection.add_options(
            [Selection(archivo.name, archivo) for archivo in self._archivos]
        )
        self.post_message(self.SeleccionArchivosCambiada([]))

    def on_mount(self) -> None:
        self.query_one("#selection-archivos", SelectionList).disabled = not self._habilitado

    def on_selection_list_selected_changed(
        self, event: SelectionList.SelectedChanged[Path]
    ) -> None:
        if event.control.id != "selection-archivos":
            return
        self.post_message(self.SeleccionArchivosCambiada(self.archivos_seleccionados))
