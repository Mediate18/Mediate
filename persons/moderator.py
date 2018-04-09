from moderation import moderation
import importlib
import inspect

from . import models

# Set all models as moderated
models = importlib.import_module(models.__name__)
for name, obj in inspect.getmembers(models, inspect.isclass):
    if obj.__module__ == models.__name__:
        moderation.register(obj)