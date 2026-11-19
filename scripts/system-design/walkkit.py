"""The authoring helpers for walk-throughs live in scripts/walkthroughs/kit.py. This file keeps the old import path for walks_*.py."""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "walkthroughs"))
from kit import *  # noqa: E402,F401,F403
