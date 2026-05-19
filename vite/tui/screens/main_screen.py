from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Header, Footer, Button, Label
from textual.containers import Container
from vite.tui.widgets.empresa_selector import EmpresaSelector
from vite.tui.widgets.periodo_selector import PeriodoSelector
from vite.tui.widgets.folder_picker import FolderPicker
from vite.tui.widgets.file_checklist import FileChecklist
from vite.tui.controllers.etl_controller import ETLController


class MainScreen(Screen):
    """Pantalla principal: selección de empresa, período, carpeta y archivos."""

    def compose(self) -> ComposeResult:
        yield Header()
        with Container(id="main-container"):
            yield Label("Empresa:", classes="section-title")
            yield EmpresaSelector(id="empresa-selector")

            yield Label("Período:", classes="section-title")
            yield PeriodoSelector(id="periodo-selector")

            yield Label("Carpeta de archivos:", classes="section-title")
            yield FolderPicker(id="folder-picker")

            yield Label("Archivos a procesar:", classes="section-title")
            yield FileChecklist(id="file-checklist")

            yield Button("▶ Iniciar proceso", id="btn-iniciar", variant="primary", classes="primary-btn")
        yield Footer()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn-iniciar":
            self._iniciar_proceso()

    def _iniciar_proceso(self) -> None:
        empresa_selector = self.query_one("#empresa-selector", EmpresaSelector)
        periodo_selector = self.query_one("#periodo-selector", PeriodoSelector)
        folder_picker = self.query_one("#folder-picker", FolderPicker)
        file_checklist = self.query_one("#file-checklist", FileChecklist)

        empresa_id = empresa_selector.empresa_id_seleccionado
        periodo_id = periodo_selector.periodo_seleccionado
        carpeta = folder_picker.carpeta_seleccionada
        archivos = file_checklist.archivos_seleccionados

        if not empresa_id:
            self.notify("Seleccione una empresa", severity="error")
            return
        if not periodo_id:
            self.notify("Seleccione un período", severity="error")
            return
        if not carpeta:
            self.notify("Seleccione una carpeta", severity="error")
            return
        if not archivos:
            self.notify("Seleccione al menos un archivo", severity="error")
            return

        controller = ETLController(self.app)
        controller.ejecutar(empresa_id, periodo_id, carpeta, archivos)
