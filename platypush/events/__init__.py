import importlib
import sys

# Alias platypush.events to platypush.message.event
_target = importlib.import_module("platypush.message.event")
sys.modules[__name__] = _target
