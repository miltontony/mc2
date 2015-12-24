from django import forms
from django.contrib.auth import get_user_model
from django.forms.models import inlineformset_factory, modelform_factory
from django.utils.translation import ugettext as _

from mc2.organizations.models import Organization


OrganizationForm = modelform_factory(Organization, fields=('name',))


class NewUserForm(forms.ModelForm):
    email = forms.EmailField()

    def clean_email(self):
        User = get_user_model()
        # TODO: handle non-unique email
        try:
            self.instance.user = User.objects.get(
                email=self.cleaned_data['email'])
        except User.DoesNotExist:
            raise forms.ValidationError(
                _('A user with this email does not exist.'),
                code='user_does_not_exist')
        return self.cleaned_data['email']

    class Meta:
        model = Organization.users.through
        fields = ('email', 'is_admin')


ExistingUserInlineFormSet = inlineformset_factory(
    Organization,
    Organization.users.through,
    fields=('is_admin',),
    extra=0)
NewUserInlineFormSet = inlineformset_factory(
    Organization,
    Organization.users.through,
    form=NewUserForm,
    extra=1,
    can_delete=False)


class OrganizationFormHelper(object):

    def __init__(self, data=None, files=None, instance=None,
                 prefix=None, initial={}):
        self.organization_form = OrganizationForm(
            data, files,
            instance=instance,
            prefix='organization')
        self.users_formset = ExistingUserInlineFormSet(
            data, files,
            instance=instance,
            prefix='users')
        self.new_users_formset = NewUserInlineFormSet(
            data, files,
            instance=instance,
            prefix='new_users',
            queryset=Organization.users.through.objects.none())

    def __iter__(self):
        yield self.organization_form
        yield self.users_formset
        yield self.new_users_formset

    def is_valid(self):
        return all(form.is_valid() for form in self)

    def save(self):
        return [form.save() for form in self]
