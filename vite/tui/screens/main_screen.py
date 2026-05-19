from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Button
from textual.containers import Container
from vite.tui.widgets.empresa_selector import EmpresaSelector
from vite.tui.widgets.periodo_selector import PeriodoSelector
from vite.tui.widgets.folder_picker import FolderPicker
from vite.tui.widgets.file_checklist import FileChecklist
from vite.tui.controllers.etl_controller import ETLController


class MainScreen(Screen):
    """Pantalla principal: selección de empresa, período, carpeta y archivos."""

    def compose(self) -> ComposeResult:
        with Container(id="main-container"):
            yield EmpresaSelector(id="empresa-selector")
            yield PeriodoSelector(id="periodo-selector")
            yield FolderPicker(id="folder-picker")
            yield FileChecklist(id="file-checklist")
            yield Button(
                "▶ Iniciar proceso",
                id="btn-iniciar",
                variant="primary",
                classes="primary-btn",
                disabled=True,
            )

    def on_mount(self) -> None:
        self.query_one("#periodo-selector", PeriodoSelector).set_enabled(False)
        self.query_one("#folder-picker", FolderPicker).set_enabled(False)
        self.query_one("#file-checklist", FileChecklist).set_enabled(False)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn-iniciar":
            self._iniciar_proceso()

    def on_empresa_selector_empresa_seleccionada(
        self, event: EmpresaSelector.EmpresaSeleccionada
    ) -> None:
        periodo_selector = self.query_one("#periodo-selector", PeriodoSelector)
        periodo_selector.set_enabled(event.empresa_id is not None)
        self._reset_flujo_desde_periodo()

        if event.empresa_id is None:
            self._actualizar_estado_iniciar()
            return

        periodo_selector.refrescar_desde_cfg_periodo()
        if periodo_selector.tiene_periodos():
            periodo_selector.abrir_desplegable()
            self.notify(
                "Empresa seleccionada. Ahora seleccione el año (cfg_periodo).",
                severity="information",
            )
            return

        periodo_selector.mostrar_creacion_periodo()
        self.notify(
            "No hay años configurados en cfg_periodo. Cree uno para continuar.",
            severity="warning",
        )

    def on_periodo_selector_periodo_seleccionado(
        self, event: PeriodoSelector.PeriodoSeleccionado
    ) -> None:
        folder_picker = self.query_one("#folder-picker", FolderPicker)
        habilitar = event.periodo_id is not None
        folder_picker.set_enabled(habilitar)
        if not habilitar:
            self._reset_flujo_desde_carpeta()
            self._actualizar_estado_iniciar()
            return
        folder_picker.enfocar_input()
        self.notify("Pegue la ruta completa de la carpeta y presione Enter o Refrescar.", severity="information")

    def on_folder_picker_carpeta_cambiada(
        self, event: FolderPicker.CarpetaCambiada
    ) -> None:
        checklist = self.query_one("#file-checklist", FileChecklist)
        checklist.set_enabled(True)
        checklist.cargar_desde_carpeta(event.carpeta)
        self.notify("Carpeta validada. Marque los Excel a procesar.", severity="information")
        self._actualizar_estado_iniciar()

    def on_file_checklist_seleccion_archivos_cambiada(
        self, event: FileChecklist.SeleccionArchivosCambiada
    ) -> None:
        _ = event
        self._actualizar_estado_iniciar()

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

    def _reset_flujo_desde_periodo(self) -> None:
        self.query_one("#folder-picker", FolderPicker).set_enabled(False)
        self._reset_flujo_desde_carpeta()

    def _reset_flujo_desde_carpeta(self) -> None:
        self.query_one("#folder-picker", FolderPicker).limpiar()
        checklist = self.query_one("#file-checklist", FileChecklist)
        checklist.set_enabled(False)
        checklist.cargar_desde_carpeta(None)

    def _actualizar_estado_iniciar(self) -> None:
        empresa_id = self.query_one("#empresa-selector", EmpresaSelector).empresa_id_seleccionado
        periodo_id = self.query_one("#periodo-selector", PeriodoSelector).periodo_seleccionado
        carpeta = self.query_one("#folder-picker", FolderPicker).carpeta_seleccionada
        archivos = self.query_one("#file-checklist", FileChecklist).archivos_seleccionados
        habilitar = (
            empresa_id is not None
            and periodo_id is not None
            and carpeta is not None
            and len(archivos) > 0
        )
        self.query_one("#btn-iniciar", Button).disabled = not habilitar
