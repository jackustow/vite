import subprocess
import sys
from pathlib import Path


def main() -> None:
    app_path = Path(__file__).parent / "ui" / "app.py"
    sys.exit(subprocess.call([sys.executable, "-m", "streamlit", "run", str(app_path)]))


if __name__ == "__main__":
    main()
