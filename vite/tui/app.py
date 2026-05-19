from textual.app import App, ComposeResult
from textual.binding import Binding
from vite.tui.screens.main_screen import MainScreen
from vite.utils.logging_config import setup_logging


class ViteApp(App):
    """VITE - Validación de Información de Terceros Exógena"""

    TITLE = "VITE - Validación de Terceros Exógena"
    SUB_TITLE = "Medios Magnéticos DIAN Colombia"

    CSS = """
    Screen {
        background: $surface;
    }

    .section-title {
        text-style: bold;
        color: $primary;
        margin: 0 0;
        padding: 0 0;
    }

    .error-label {
        color: $error;
    }

    Button.primary-btn {
        background: $primary;
        margin: 0 0;
    }

    #main-container {
        layout: vertical;
        overflow-y: auto;
        padding: 0 0;
    }

    #empresa-selector,
    #periodo-selector,
    #folder-picker {
        margin: 0 0;
        padding: 0 0;
        height: auto;
    }

    #file-checklist {
        height: 16;
        padding: 0 0;
        margin: 0 0;
    }

    #selection-archivos {
        height: 1fr;
    }

    #folder-picker {
        margin: 0 0;
        padding: 0 0;
    }

    #btn-iniciar {
        margin: 0 0;
        padding: 0 0;
    }
    """

    BINDINGS = [
        Binding("q", "quit", "Salir", priority=True),
    ]

    def on_mount(self) -> None:
        self.push_screen(MainScreen())


def main() -> None:
    setup_logging()
    app = ViteApp()
    app.run()


if __name__ == "__main__":
    main()
