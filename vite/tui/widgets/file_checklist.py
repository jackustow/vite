from pathlib import Path
from textual.app import ComposeResult
from textual.widget import Widget
from textual.widgets import Checkbox, Label
from textual.containers import VerticalScroll
from vite.tui.widgets.folder_picker import FolderPicker


class FileChecklist(Widget):
    """Lista de archivos Excel con checkboxes.

    Se actualiza automáticamente cuando FolderPicker emite CarpetaCambiada.
    El handler `on_folder_picker_carpeta_cambiada` se dispara porque el mensaje
    FolderPicker.CarpetaCambiada tiene handler_name == 'on_folder_picker_carpeta_cambiada'.
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._carpeta: Path | None = None
        self._archivos: list[Path] = []

    @property
    def archivos_seleccionados(self) -> list[Path]:
        """Retorna los archivos marcados con checkbox."""
        result = []
        for checkbox in self.query(Checkbox):
            if checkbox.value:
                idx_str = checkbox.id.split("-")[-1] if checkbox.id else None
                if idx_str is not None:
                    try:
                        idx = int(idx_str)
                        if idx < len(self._archivos):
                            result.append(self._archivos[idx])
                    except ValueError:
                        pass
        return result

    def compose(self) -> ComposeResult:
        with VerticalScroll(id="scroll-archivos"):
            yield Label(
                "(Seleccione una carpeta y haga clic en Refrescar)",
                id="label-vacio",
            )

    def on_folder_picker_carpeta_cambiada(self, event: FolderPicker.CarpetaCambiada) -> None:
        self._carpeta = event.carpeta
        self._refrescar()

    def _refrescar(self) -> None:
        if not self._carpeta:
            return
        self._archivos = sorted(
            list(self._carpeta.glob("*.xlsx")) + list(self._carpeta.glob("*.xls"))
        )
        scroll = self.query_one("#scroll-archivos", VerticalScroll)
        # remove_children() returns an AwaitRemove; calling without await is safe
        # in Textual 8.x — the removal is scheduled on the next frame.
        scroll.remove_children()
        if not self._archivos:
            scroll.mount(Label("No se encontraron archivos .xls/.xlsx en la carpeta"))
            return
        for idx, archivo in enumerate(self._archivos):
            scroll.mount(Checkbox(archivo.name, id=f"chk-{idx}"))
