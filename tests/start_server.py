import subprocess
import os

env = os.environ.copy()
env["PYTHONPATH"] = env.get("PYTHONPATH", "") + ":."
with open("api_logs.txt", "w") as f:
    subprocess.Popen(["python3", "-m", "app.api"], stdout=f, stderr=f, env=env, preexec_fn=os.setpgrp)
print("Server started in background.")
