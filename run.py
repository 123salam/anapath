import os
import subprocess
import sys

def main():
    # Chemin vers votre script Streamlit
    script_path = os.path.join(os.path.dirname(__file__), "app.py")
    
    # Lancer Streamlit en sous-processus
    subprocess.run([sys.executable, "-m", "streamlit", "run", script_path])

if __name__ == "__main__":
    main()