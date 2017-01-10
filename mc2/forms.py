from django import forms

from django.contrib.auth.models import User as user_model

from mc2.models import UserSettings
from django.utils.translation import ugettext_lazy as _


class UserSettingsForm(forms.ModelForm):
    settings_level = forms.ChoiceField(
        choices=UserSettings.SETTINGS_LEVEL_CHOICES,
        widget=forms.RadioSelect())

    class Meta:
        model = UserSettings
        fields = ('settings_level', )


class CreateAccountForm(forms.Form):
    """
    Form for creating a new user account.

    """
    username = forms.RegexField(
        regex=r'^\w+$',
        widget=forms.TextInput(
            attrs=dict(
                required=True,
                max_length=30,
            )
        ),
        label=_("Username"))

    password = forms.CharField(
        widget=forms.PasswordInput(
            attrs=dict(
                required=True,
                render_value=False,
                type='password',
            )
        ),
        label=_("Password"))

    confirm_password = forms.CharField(
        widget=forms.PasswordInput(
            attrs=dict(
                required=True,
                render_value=False,
                type='password',
            )
        ),
        label=_("Password Confirmation"))

    first_name = forms.CharField(required=False)
    last_name = forms.CharField(required=False)
    email = forms.EmailField(required=False)

    def clean_username(self):
        try:
            user_model.objects.get(
                username__iexact=self.cleaned_data['username'])
        except user_model.DoesNotExist:
            return self.cleaned_data['username']
        raise forms.ValidationError(_('Username already exists.'))

    def clean_password(self):
        password = self.cleaned_data.get('password', None)
        confirm_password = self.cleaned_data.get('confirm_password', None)
        if (password and confirm_password and
                (password == confirm_password)):
            return self.cleaned_data
        else:
            raise forms.ValidationError(_('Passwords do not match.'))

    def clean_email(self):
        '''
        Validate that the supplied email address is unique for the
        site.
        '''
        if user_model.objects.filter(
           email__iexact=self.cleaned_data['email']).exists():
            raise forms.ValidationError('This email address is already in use.'
                                        'Please supply a different'
                                        'email address.')
        return self.cleaned_data['email']
