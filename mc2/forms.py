from django import forms

from mc2.models import UserSettings


class UserSettingsForm(forms.ModelForm):
    settings_level = forms.ChoiceField(
        choices=UserSettings.SETTINGS_LEVEL_CHOICES,
        widget=forms.RadioSelect())

    class Meta:
        model = UserSettings
        fields = ('settings_level', )
