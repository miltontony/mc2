from django import forms
from controllers.base.models import Controller


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
