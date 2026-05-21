"""Cross-module usage: import compiled functions from other examples."""

import sys
from pathlib import Path

# Add examples dir to path so sibling imports work
sys.path.insert(0, str(Path(__file__).parent))

from operations import add
from printing import print_int

if __name__ == "__main__":
    result = add(10, 59)
    print_int(result)
