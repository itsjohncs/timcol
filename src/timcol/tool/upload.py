import os
import subprocess


def run_upload(log_path: str):
    log_dir_path = os.path.dirname(log_path)
    sync_path = os.path.join(log_dir_path, "upload")
    try:
        subprocess.run(sync_path, check=True)
    except FileNotFoundError:
        print(f"Does not exist: {sync_path}")
    except PermissionError:
        print(f"Not executable: {sync_path}")
