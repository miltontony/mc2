from django import forms

from unicoremc.models import UserSettings


class UserSettingsForm(forms.ModelForm):
    settings_level = forms.ChoiceField(
        choices=UserSettings.SETTINGS_LEVEL_CHOICES,
        widget=forms.RadioSelect())

    class Meta:
        model = UserSettings
        fields = ('settings_level', )
