"""Allow running the CLI as a module: python -m wetwire_github.cli"""

import sys

from .main import main

if __name__ == "__main__":
    sys.exit(main())
