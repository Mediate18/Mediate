from moderation import moderation

from .models import Item, Publisher

moderation.register(Item)  # Uses default moderation settings
moderation.register(Publisher)  # Uses default moderation settings
