from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import ugettext as _


ORGANIZATION_SESSION_KEY = 'org_id'


class OrganizationManager(models.Manager):
    use_for_related_fields = True

    def for_user(self, user):
        qs = self.get_queryset()
        if not user.is_active:
            return qs.none()
        return qs.filter(users=user)

    def for_admin_user(self, user):
        qs = self.get_queryset()
        if not user.is_active:
            return qs.none()
        return qs.filter(
            organizationuserrelation__user=user,
            organizationuserrelation__is_admin=True)


class Organization(models.Model):
    objects = OrganizationManager()

    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255)
    users = models.ManyToManyField(
        get_user_model(),
        through='OrganizationUserRelation')

    def __unicode__(self):
        return self.name

    def has_admin(self, user):
        return self.__class__.objects.for_admin_user(
            user).filter(pk=self.pk).exists()


class OrganizationUserRelation(models.Model):
    organization = models.ForeignKey(Organization)
    user = models.ForeignKey(get_user_model())
    is_admin = models.BooleanField(
        default=False,
        help_text=_('This allows the user to manage the'
                    ' organization and its users.'))

    class Meta:
        unique_together = (('organization', 'user'),)

    def __unicode__(self):
        return u'%s%s' % (
            self.user.get_short_name() or self.user.email,
            ' (admin)' if self.is_admin else '')
