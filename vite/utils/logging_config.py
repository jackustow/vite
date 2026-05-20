import sys
from pathlib import Path
from loguru import logger

_configured = False


def setup_logging(level: str = "INFO") -> None:
    global _configured
    if _configured:
        return

    logger.remove()

    logger.add(
        sys.stderr,
        level=level,
        format=(
            "<green>{time:HH:mm:ss}</green> | "
            "<level>{level: <8}</level> | "
            "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
            "<level>{message}</level>"
        ),
        colorize=True,
    )

    log_dir = Path.home() / ".vite" / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    logger.add(
        log_dir / "vite_{time:YYYYMMDD}.log",
        level="DEBUG",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        rotation="00:00",
        retention="30 days",
        encoding="utf-8",
    )

    _configured = True
    logger.info("Logging inicializado. Nivel: {}. Directorio de logs: {}", level, log_dir)


def get_logger(name: str):
    return logger.bind(name=name)
