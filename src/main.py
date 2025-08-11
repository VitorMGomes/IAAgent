import subprocess
import time
import requests
import os
import platform

def kill_processes_on_ports():
    """Mata processos usando as portas 8000 e 8501 - multiplataforma"""
    try:
        system = platform.system().lower()
        
        if system == "windows":
            # Windows: usa taskkill e netstat
            subprocess.run(["taskkill", "/f", "/im", "uvicorn.exe"], capture_output=True, check=False)
            subprocess.run(["taskkill", "/f", "/im", "streamlit.exe"], capture_output=True, check=False)
            # Mata processos específicos nas portas (Windows)
            for port in [8000, 8501]:
                try:
                    result = subprocess.run(
                        ["netstat", "-ano"], 
                        capture_output=True, text=True, check=False
                    )
                    lines = result.stdout.split('\n')
                    for line in lines:
                        if f":{port}" in line and "LISTENING" in line:
                            parts = line.strip().split()
                            if len(parts) > 4:
                                pid = parts[-1]
                                subprocess.run(["taskkill", "/f", "/pid", pid], capture_output=True, check=False)
                except Exception:
                    pass
        else:
            # Linux/macOS: usa pkill e fuser
            subprocess.run(["pkill", "-f", "uvicorn.*src.api:app"], capture_output=True, check=False)
            subprocess.run(["pkill", "-f", "streamlit.*src/ui/Home.py"], capture_output=True, check=False)
            subprocess.run(["fuser", "-k", "8000/tcp"], capture_output=True, check=False)
            subprocess.run(["fuser", "-k", "8501/tcp"], capture_output=True, check=False)
            
        time.sleep(2)
    except Exception as e:
        print(f"Aviso: Erro ao finalizar processos anteriores: {e}")

# Define o diretório base do projeto
project_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src_dir = os.path.join(project_dir, "src")
venv_dir = os.path.join(project_dir, "venv")

# Detecta o sistema operacional
system = platform.system().lower()
is_windows = system == "windows"

# Caminhos para executáveis do ambiente virtual (multiplataforma)
if is_windows:
    scripts_dir = os.path.join(venv_dir, "Scripts")
    python_executable = os.path.join(scripts_dir, "python.exe")
    uvicorn_executable = os.path.join(scripts_dir, "uvicorn.exe")
    streamlit_executable = os.path.join(scripts_dir, "streamlit.exe")
    path_separator = ";"
else:
    bin_dir = os.path.join(venv_dir, "bin")
    python_executable = os.path.join(bin_dir, "python")
    uvicorn_executable = os.path.join(bin_dir, "uvicorn")
    streamlit_executable = os.path.join(bin_dir, "streamlit")
    path_separator = ":"

# Verifica se o ambiente virtual existe
if not os.path.exists(python_executable):
    print(f"ERRO: Ambiente virtual não encontrado em {venv_dir}")
    if is_windows:
        print("Execute: python -m venv venv && venv\\Scripts\\activate && pip install -r requirements.txt")
    else:
        print("Execute: python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt")
    exit(1)

# Verifica se arquivos críticos existem
csv_path = os.path.join(src_dir, "data", "Dados.csv")
env_path = os.path.join(project_dir, ".env")
chroma_path = os.path.join(project_dir, "chrome_langchain_db")

if not os.path.exists(csv_path):
    print(f"ERRO: Arquivo CSV não encontrado em {csv_path}")
    exit(1)

if not os.path.exists(env_path):
    print(f"AVISO: Arquivo .env não encontrado em {env_path}")

if not os.path.exists(chroma_path):
    print(f"AVISO: Diretório Chroma não encontrado em {chroma_path}")

# Libera as portas que serão usadas
print("Verificando e liberando portas 8000 e 8501...")
kill_processes_on_ports()

# Configura o ambiente
env = os.environ.copy()
env["PYTHONPATH"] = project_dir + path_separator + src_dir

# Muda para o diretório do projeto para garantir caminhos relativos corretos
os.chdir(project_dir)

print("Iniciando API FastAPI...")
api_process = subprocess.Popen(
    [uvicorn_executable, "src.api:app", "--reload", "--host", "127.0.0.1", "--port", "8000"],
    env=env,
    cwd=project_dir
)

for attempt in range(30):  # Aumenta tentativas para 30 segundos
    try:
        response = requests.get("http://127.0.0.1:8000/dados", timeout=5)
        if response.status_code == 200:
            print("API está respondendo corretamente!")
            break
    except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
        print(f"Tentativa {attempt + 1}/30: Aguardando API inicializar...")
        time.sleep(1)
else:
    print("API não respondeu após 30 segundos. Encerrando.")
    api_process.terminate()
    api_process.wait()
    exit(1)

print("Iniciando interface Streamlit...")
streamlit_process = subprocess.Popen(
    [streamlit_executable, "run", "src/ui/Home.py", "--server.port", "8501"],
    env=env,
    cwd=project_dir
)

print("Ambos os serviços foram iniciados com sucesso!")
print("API FastAPI: http://127.0.0.1:8000")
print("Interface Streamlit: http://127.0.0.1:8501")

try:
    api_process.wait()
    streamlit_process.wait()
except KeyboardInterrupt:
    print("\nEncerrando aplicação...")
    api_process.terminate()
    streamlit_process.terminate()
    api_process.wait()
    streamlit_process.wait()
    print("Aplicação encerrada.")
