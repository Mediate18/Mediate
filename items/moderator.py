from moderation import moderation

from items.models import BookItem, Publisher, Catalogue

moderation.register(BookItem)  # Uses default moderation settings
moderation.register(Publisher)  # Uses default moderation settings
moderation.register(Catalogue)  # Uses default moderation settings
