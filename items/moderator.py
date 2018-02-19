from moderation import moderation

from items.models import Item, Publisher, Catalogue

moderation.register(Item)  # Uses default moderation settings
moderation.register(Publisher)  # Uses default moderation settings
moderation.register(Catalogue)  # Uses default moderation settings
