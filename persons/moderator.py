from moderation import moderation
from moderation.moderator import GenericModerator
import importlib
import inspect

from . import models


class GlobalModerator(GenericModerator):
    keep_history = True
    auto_approve_for_staff = False


# Set all models as moderated
models = importlib.import_module(models.__name__)
for name, obj in inspect.getmembers(models, inspect.isclass):
    if obj.__module__ == models.__name__:
        moderation.register(obj, GlobalModerator)