"""
This module contains a very primitive view for importing Marathon app
definitions. There's very little validation or feedback, so it should only be
used by people who know what they're doing and have access to server logs to
see the inevitable stack traces.
"""

import json

from django import forms
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.shortcuts import render

from mc2.controllers.base.views import ControllerViewMixin
from mc2.controllers.docker.models import DockerController


class HiddenImportForm(forms.Form):
    name = forms.CharField()
    app_data = forms.CharField(widget=forms.Textarea)


class HiddenImportView(ControllerViewMixin):
    def get(self, request):
        form = HiddenImportForm()
        return render(request, 'hidden_import.html', {'form': form})

    def post(self, request):
        form = HiddenImportForm(request.POST)
        assert form.is_valid()
        DockerController.from_marathon_app_data(
            self.request.user, json.loads(form.cleaned_data['app_data']),
            form.cleaned_data['name'])
        messages.info(self.request, "App created: {name}".format(
            **form.cleaned_data))
        return HttpResponseRedirect('/')
