import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

# chains.py builds the Claude clients at import time, so a key must exist.
os.environ.setdefault("ANTHROPIC_API_KEY", "test-key")
os.environ.setdefault("NEWS_API_KEY", "test-key")
