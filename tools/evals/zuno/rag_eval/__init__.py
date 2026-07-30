import sys
from pathlib import Path
curr = Path(__file__).resolve()
while curr.name != "Zuno" and curr.parent != curr:
    curr = curr.parent
ROOT_DIR = curr
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))
"""RAG evaluation helpers."""
