from django.db import models


class PermissionContainer(models.Model):
    """
    Temporary model to contain permissions that are not bound to a content type.
    TODO: Upgrade Django >= 2.1 to have automatic view permissions.
    """
    class Meta:
        managed = False  # No database table creation or deletion operations will be performed for this model.

        permissions = (
            ('view_all', 'View all data'),
        )
