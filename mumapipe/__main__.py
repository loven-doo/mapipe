import sys
from mumapipe import run_mapipe
from mapipe.tools._inner_tools import _parse_cmd_args

if __name__ == "__main__":
    args = _parse_cmd_args(sys.argv[-1:], 1)
    run_mapipe(*args)
