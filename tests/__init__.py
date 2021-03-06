import logging
import os
import sys

logging.basicConfig(level=logging.INFO, stream=sys.stdout)
test_dir = os.path.abspath(os.path.dirname(__file__))
sys.path.insert(0, os.path.abspath(os.path.join(test_dir, '..')))
