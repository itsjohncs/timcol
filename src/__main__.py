import sys
import platform

if sys.version_info < (3, 11):
    raise RuntimeError(
        f"This script must be run with Python 3.11 or greater (found {platform.python_version()})"
    )

if __name__ == "__main__":
    from .tool.main import main

    main(sys.argv)
