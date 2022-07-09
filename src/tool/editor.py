import os
import subprocess
import shlex


def open_in_editor(path: str) -> None:
    editor = os.environ.get("EDITOR")
    if editor is None:
        raise RuntimeError("EDITOR environmental variable must be defined.")

    subprocess.run([*shlex.split(editor), path], check=True)
