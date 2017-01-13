from django import forms

from django.contrib.auth.models import User as user_model
from django.contrib.auth.forms import UserCreationForm

from mc2.models import UserSettings


class UserSettingsForm(forms.ModelForm):
    settings_level = forms.ChoiceField(
        choices=UserSettings.SETTINGS_LEVEL_CHOICES,
        widget=forms.RadioSelect())

    class Meta:
        model = UserSettings
        fields = ('settings_level', )


class CreateAccountForm(UserCreationForm):
    """
    Form for creating a new user account.

    """
    first_name = forms.CharField(required=False)
    last_name = forms.CharField(required=False)
    email = forms.EmailField(required=True)

    def clean_email(self):
        '''
        Validate that the supplied email address is unique for the
        site.
        '''
        if user_model.objects.filter(
           email__iexact=self.cleaned_data['email']).exists():
            raise forms.ValidationError('This email address is already in use.'
                                        ' Please supply a different'
                                        ' email address.')
        return self.cleaned_data['email']
