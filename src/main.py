import subprocess
import time
import requests
import os

src_dir = os.path.join(os.path.dirname(__file__))

env = os.environ.copy()
env["PYTHONPATH"] = src_dir

api_process = subprocess.Popen(
    ["uvicorn", "src.api:app", "--reload"],
    env=env
)

for _ in range(10):
    try:
        requests.get("http://127.0.0.1:8000/dados")
        break
    except requests.exceptions.ConnectionError:
        time.sleep(1)
else:
    print("API não respondeu. Encerrando.")
    api_process.kill()
    exit(1)

streamlit_process = subprocess.Popen(["streamlit", "run", "src/ui/Home.py"])

api_process.wait()
streamlit_process.wait()
