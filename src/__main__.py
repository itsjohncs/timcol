import sys
import os
import platform

if sys.version_info < (3, 11):
    raise RuntimeError(
        f"This script must be run with Python 3.11 or greater (found {platform.python_version()})"
    )

if __name__ == "__main__":
    original_cwd = os.environ.get("TIMCOL_ORIGINAL_CWD")
    if original_cwd:
        os.chdir(original_cwd)

    from .tool.main import main

    main(sys.argv)
