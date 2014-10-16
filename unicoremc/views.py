from django.contrib import admin
from django.shortcuts import render


@admin.site.register_view('apps/', 'Apps')
def apps_view(request, *args, **kwargs):
    context = {
        'supervisor_configs': [],  # List of apps configured via supervisor
    }
    return render(request, 'admin/unicoremc/apps.html', context)
