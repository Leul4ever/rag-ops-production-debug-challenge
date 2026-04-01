import os
import subprocess
import time
import shutil
import requests
import sys

BASE_DIR = r"d:\kifyaAi\rag-ops-production-debug-challenge\fix@metrics_pipeline.com"
TMP_DIR = r"d:\kifyaAi\rag-ops-production-debug-challenge\tmp_verify"

def cleanup():
    if os.path.exists(TMP_DIR):
        try:
            shutil.rmtree(TMP_DIR)
        except:
            pass

def setup():
    cleanup()
    os.makedirs(TMP_DIR)
    shutil.copytree(os.path.join(BASE_DIR, "environment"), os.path.join(TMP_DIR, "app"), dirs_exist_ok=True)
    shutil.copytree(os.path.join(BASE_DIR, "tests"), os.path.join(TMP_DIR, "tests"), dirs_exist_ok=True)
    
    # Patch settings.yaml for local Windows test (change /app/metrics.db to metrics.db)
    settings_path = os.path.join(TMP_DIR, "app", "settings.yaml")
    if os.path.exists(settings_path):
        with open(settings_path, 'r') as f:
            content = f.read()
        content = content.replace("/app/metrics.db", "metrics.db")
        with open(settings_path, 'w') as f:
            f.write(content)

def test_startup_fail():
    print("--- Testing Startup with Bugs ---")
    # Bug 2 is path: ./config/settings.yaml (not ./settings.yaml)
    process = subprocess.Popen([sys.executable, "app.py"], 
                               cwd=os.path.join(TMP_DIR, "app"),
                               stderr=subprocess.PIPE, stdout=subprocess.PIPE, text=True)
    time.sleep(3)
    if process.poll() is not None:
        stdout, stderr = process.communicate()
        print(f"App failed to start (Expected): {stderr}")
        # Expected error: FileNotFoundError for settings.yaml or ModuleNotFoundError for werkzeug conflict
        return "FileNotFoundError" in stderr or "ImportError" in stderr or "ModuleNotFoundError" in stderr or "OperationalError" in stderr
    else:
        process.terminate()
        print("App started unexpectedly! Bug 1 or 2 might be missing.")
        return False

def apply_fixes():
    print("--- Applying Fixes (Simulating solve.sh) ---")
    app_py_path = os.path.join(TMP_DIR, "app", "app.py")
    req_path = os.path.join(TMP_DIR, "app", "requirements.txt")
    
    with open(app_py_path, 'r') as f:
        content = f.read()
    
    # Fix Bug 2 (Path)
    content = content.replace("open('./config/settings.yaml'", "open('./settings.yaml'")
    # Fix Bug 3 (Logic)
    content = content.replace("range(1, len(values))", "range(len(values))")
    
    with open(app_py_path, 'w') as f:
        f.write(content)

def test_fixed_state():
    print("--- Testing Fixed State ---")
    # Note: Werkzeug/Flask conflict might still exist in the current python env 
    # but for local Windows logic verification we mainly care about Bug 2 and Bug 3.
    process = subprocess.Popen([sys.executable, "app.py"], 
                               cwd=os.path.join(TMP_DIR, "app"))
    time.sleep(3)
    
    try:
        # Run pytest
        test_file = os.path.join(TMP_DIR, "tests", "test_outputs.py")
        result = subprocess.run([sys.executable, "-m", "pytest", test_file, "-v"], 
                                capture_output=True, text=True)
        print(result.stdout)
        print(result.stderr)
        return result.returncode == 0
    finally:
        process.terminate()

if __name__ == "__main__":
    try:
        setup()
        if test_startup_fail():
            apply_fixes()
            if test_fixed_state():
                print("\nVerification SUCCESS: All bugs confirmed and fixed.")
            else:
                print("\nVerification FAILURE: Solution did not pass tests.")
        else:
            print("\nVerification FAILURE: Bugs not reachable/detected.")
    except Exception as e:
        print(f"Verification ERROR: {e}")
    finally:
        pass
