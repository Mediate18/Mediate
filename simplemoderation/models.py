from django.db import models
from django.contrib.auth.models import User

import uuid

class Moderation(models.Model):
    """
    
    """
    ACTIONS = (
        ('C', 'create'),
        ('U', 'update'),
        ('D', 'delete'),
    )
    STATES = (
        ('P', 'pending'),
        ('A', 'approved'),
        ('R', 'rejected'),
    )

    editor = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="moderated_edits")
    datetime = models.DateTimeField(auto_now_add=True)
    action = models.CharField(max_length=1, choices=ACTIONS, default='C')
    state = models.CharField(max_length=1, choices=STATES, default='P')
    data = models.TextField()
    object_uuid = models.CharField(max_length=36, blank=True, default="")
    datetime_state_change = models.DateTimeField(null=True)
    moderator = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="handled_moderations")
    reason = models.TextField(blank=True)