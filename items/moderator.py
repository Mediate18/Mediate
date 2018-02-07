from moderation import moderation

from items.models import BookItem, Publisher

moderation.register(BookItem)  # Uses default moderation settings
moderation.register(Publisher)  # Uses default moderation settings
