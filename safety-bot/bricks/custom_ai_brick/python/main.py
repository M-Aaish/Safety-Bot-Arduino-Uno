import os
import subprocess
import time
import urllib.request
import shutil
import stat

print("=== STARTING PYTHON 3.11 BOOTSTRAPPER ===", flush=True)

app_dir = "/app"
python_dir = os.path.join(app_dir, "python")
venv_dir = os.path.join(app_dir, "venv311")
cache_dir = os.path.join(app_dir, ".cache")

os.environ["UV_CACHE_DIR"] = cache_dir

# 1. Download `uv` (Fast Python package manager)
uv_bin = os.path.join(app_dir, "uv")
if not os.path.exists(uv_bin):
    print("Downloading uv (Python 3.11 builder)...", flush=True)
    req = urllib.request.Request(
        "https://github.com/astral-sh/uv/releases/latest/download/uv-aarch64-unknown-linux-gnu.tar.gz",
        headers={'User-Agent': 'Mozilla/5.0'}
    )
    with urllib.request.urlopen(req) as response, open(os.path.join(app_dir, "uv.tar.gz"), 'wb') as out_file:
        shutil.copyfileobj(response, out_file)
    
    os.system(f"tar -xzf {os.path.join(app_dir, 'uv.tar.gz')} -C {app_dir}")
    shutil.move(os.path.join(app_dir, "uv-aarch64-unknown-linux-gnu", "uv"), uv_bin)
    os.chmod(uv_bin, os.stat(uv_bin).st_mode | stat.S_IEXEC)

# 2. Create Python 3.11 Environment
if not os.path.exists(venv_dir):
    print(f"Creating portable Python 3.11 environment at {venv_dir}...", flush=True)
    os.system(f"{uv_bin} venv --python 3.11 {venv_dir}")

# 3. Install latest depthai and dependencies (NO version constraint!)
print("Installing latest depthai into 3.11 environment...", flush=True)
os.system(f"{uv_bin} pip install --upgrade --python {venv_dir} depthai==2.28.0  opencv-python-headless python-socketio websocket-client requests")

python_bin = os.path.join(venv_dir, "bin", "python")

# 4. Run the Camera Script
runner_script = "/app/python/camera_runner.py"

print("Environment Ready! Launching camera runner...", flush=True)

while True:
    print(f"Executing {runner_script}...", flush=True)
    process = subprocess.run([python_bin, runner_script])
    print(f"Camera runner crashed with code {process.returncode}. Restarting in 10s...", flush=True)
    time.sleep(10)