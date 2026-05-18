import subprocess
print("Starting rig...")
result = subprocess.run(["pytest", "tests/safety_rig/router_leak_test.py", "-v"], capture_output=True, text=True)
print(result.stdout)
print(result.stderr)
