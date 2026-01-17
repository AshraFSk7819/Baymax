import subprocess, time, webbrowser, sys

ai = subprocess.Popen([sys.executable, "-m", "uvicorn", "AI.AI:app"])
report = subprocess.Popen([sys.executable, "Report_analyzer/image.py"])

time.sleep(2)
webbrowser.open("index.html")

try:
    ai.wait()
    report.wait()
except KeyboardInterrupt:
    ai.terminate()
    report.terminate()
