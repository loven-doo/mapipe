import sys
from mapipe import get_counts
from mapipe.tools._inner_tools import _parse_cmd_args

if __name__ == "__main__":
    args = _parse_cmd_args(sys.argv[1:])
    get_counts(*args)
