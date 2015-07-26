from django.contrib import admin

from organizations.models import Organization


class OrganizationUserRelationInline(admin.StackedInline):
    model = Organization.users.through
    extra = 0
    verbose_name = 'user'
    verbose_name_plural = 'users'


class OrganizationAdmin(admin.ModelAdmin):
    list_display = ('name', 'user_count')
    inlines = (OrganizationUserRelationInline, )

    def user_count(self, obj):
        return obj.users.count()
    user_count.short_description = 'Number of users'


admin.site.register(Organization, OrganizationAdmin)
