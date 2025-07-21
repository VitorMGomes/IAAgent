import subprocess
import time

# Inicia o servidor FastAPI com uvicorn apontando para src.api:app
api_process = subprocess.Popen(["uvicorn", "src.api:app", "--reload"])

# Aguarda a API subir antes de iniciar o Streamlit
time.sleep(2)

# Inicia o Streamlit apontando para src/ui/Home.py
streamlit_process = subprocess.Popen(["streamlit", "run", "src/ui/Home.py"])

# Aguarda os dois processos finalizarem
api_process.wait()
streamlit_process.wait()
