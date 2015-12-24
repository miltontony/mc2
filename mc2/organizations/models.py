from django.db import models
from django.db.models import Q
from django.conf import settings
from django.contrib.auth.models import Permission
from django.utils.translation import ugettext as _


ORGANIZATION_SESSION_KEY = 'org_id'


class OrganizationManager(models.Manager):
    use_for_related_fields = True

    def for_user(self, user):
        qs = self.get_queryset()
        if not user.is_active:
            return qs.none()
        if user.is_superuser:
            return qs
        return qs.filter(users=user)

    def for_admin_user(self, user):
        qs = self.get_queryset()
        if not user.is_active:
            return qs.none()
        if user.is_superuser:
            return qs
        return qs.filter(
            organizationuserrelation__user=user,
            organizationuserrelation__is_admin=True)


class Organization(models.Model):
    objects = OrganizationManager()

    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255)
    users = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        through='OrganizationUserRelation')

    def __unicode__(self):
        return self.name

    def has_admin(self, user):
        return self.__class__.objects.for_admin_user(
            user).filter(pk=self.pk).exists()

    def has_perms(self, user, perm_list, obj=None):
        try:
            relation = self.organizationuserrelation_set.get(user=user)
            return relation.has_perms(perm_list, obj=obj)
        except self.users.through.DoesNotExist:
            # user permissions supersede user-organization permissions
            return user.has_perms(perm_list, obj=obj)


class OrganizationUserRelation(models.Model):
    organization = models.ForeignKey(Organization)
    user = models.ForeignKey(settings.AUTH_USER_MODEL)
    is_admin = models.BooleanField(
        default=False,
        help_text=_('This allows the user to manage the'
                    ' organization and its users.'))
    groups = models.ManyToManyField('auth.Group', blank=True)
    user_permissions = models.ManyToManyField('auth.Permission', blank=True)
    # TODO: add auth token

    class Meta:
        unique_together = (('organization', 'user'),)

    def __unicode__(self):
        return u'%s%s' % (
            self.user.get_short_name() or self.user.email,
            ' (admin)' if self.is_admin else '')

    def permissions(self):
        permissions = Permission.objects.filter(
            Q(group__organizationuserrelation=self) |
            Q(organizationuserrelation=self)).values_list(
            'content_type__app_label',
            'codename')
        return ['%s.%s' % (ct, codename) for ct, codename in permissions]

    def has_perms(self, perm_list, obj=None):
        if not self.user.is_active:
            return False
        # user permissions supersede user-organization permissions
        if self.user.has_perms(perm_list, obj=obj):
            return True
        if obj and getattr(obj, 'organization', None) != self.organization:
            return False
        if self.is_admin:
            return True
        if set(perm_list) <= set(self.permissions()):
            return True
        return False
