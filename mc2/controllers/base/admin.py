from django.contrib import admin

from mc2.controllers.base.models import Controller


class ControllerAdmin(admin.ModelAdmin):
    search_fields = ('state', 'name')
    list_filter = ('state',)
    list_display = ('name', 'state', 'organization')
    list_editable = ('organization',)
    readonly_fields = ('state', 'owner')

admin.site.register(Controller, ControllerAdmin)
