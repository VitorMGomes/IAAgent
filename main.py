import subprocess
import time

api_process = subprocess.Popen(["uvicorn", "api:app", "--reload"])

time.sleep(2)

streamlit_process = subprocess.Popen(["streamlit", "run", "ui/Home.py"])

api_process.wait()
streamlit_process.wait()
