import subprocess
import sys

def run_streamlit_app():
    """Startet die Streamlit-App app.py mit dem aktiven Python-Interpreter."""
    subprocess.run([sys.executable, "-m", "streamlit", "run", "app.py"])

if __name__ == "__main__":
    run_streamlit_app()
