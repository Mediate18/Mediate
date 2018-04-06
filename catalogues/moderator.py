from moderation import moderation

from .models import Catalogue

moderation.register(Catalogue)  # Uses default moderation settings