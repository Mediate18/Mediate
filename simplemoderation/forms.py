from django import forms
from .models import *


class ModerationModelForm(forms.ModelForm):
    class Meta:
        model = Moderation
        fields = ['state', 'reason']
