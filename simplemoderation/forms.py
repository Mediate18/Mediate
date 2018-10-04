from django import forms
from .models import *


class ModerationModelForm(forms.ModelForm):
    state = forms.CharField(
        max_length=1,
        widget=forms.RadioSelect(choices=[(tag.value, tag.name) for tag in
                                          (ModerationState.APPROVED, ModerationState.REJECTED)])
    )

    class Meta:
        model = Moderation
        fields = ['state', 'reason']

    class Media:
        js = ('js/diff.js',)