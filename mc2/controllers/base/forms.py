from django import forms
from mc2.controllers.base.models import Controller, EnvVariable


class ControllerForm(forms.ModelForm):
    name = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control'}))
    marathon_cmd = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control'}))
    marathon_cpus = forms.FloatField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'}))
    marathon_mem = forms.FloatField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'}))
    marathon_instances = forms.IntegerField(
        required=False,
        min_value=0,
        widget=forms.TextInput(attrs={'class': 'form-control'}))

    class Meta:
        model = Controller
        fields = (
            'name', 'marathon_cpus', 'marathon_mem', 'marathon_instances',
            'marathon_cmd')


class EnvVariableForm(forms.ModelForm):
    key = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control'}))
    value = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control'}))

    class Meta:
        model = EnvVariable
        fields = ('key', 'value')


EnvVariableInlineFormSet = forms.inlineformset_factory(
    Controller,
    EnvVariable,
    form=EnvVariableForm,
    extra=0,
    can_delete=True,
    can_order=False
)
