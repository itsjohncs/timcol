import pathlib
import sys

if __name__ == "__main__":
    sys.path.insert(0, str(pathlib.Path(__file__).parent.absolute()))
    import tool.main

    tool.main.main(sys.argv)
