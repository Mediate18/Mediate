from django import forms
from .models import *


class ModerationModelForm(forms.ModelForm):
    approved = forms.BooleanField(label="State", required=False,
                                  widget=forms.CheckboxInput(attrs={'data-toggle': 'toggle', 'data-on': 'Approved',
                                                                    'data-off': 'Rejected', 'data-onstyle': 'success',
                                                                    'data-offstyle': 'danger'}))

    class Meta:
        model = Moderation
        fields = ['approved', 'reason']

    class Media:
        js = ('js/diff.js', 'https://gitcdn.github.io/bootstrap-toggle/2.2.2/js/bootstrap-toggle.min.js')
        css = {
            'all': ('https://gitcdn.github.io/bootstrap-toggle/2.2.2/css/bootstrap-toggle.min.css',)
        }

    def save(self, commit=True):
        """
        Turns the 'approved' boolean field into a correct state
        :param commit: 
        :return: 
        """
        self.instance.state = ModerationState.APPROVED.value if self['approved'].value() \
                                                                else ModerationState.REJECTED.value
        return super().save(commit)
