from django.db import models
from django.contrib.auth import get_user_model


class OrganizationManager(models.Manager):
    use_for_related_fields = True

    def for_admin_user(self, user):
        qs = self.get_queryset()
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


class OrganizationUserRelation(models.Model):
    organization = models.ForeignKey(Organization)
    user = models.ForeignKey(get_user_model())
    is_admin = models.BooleanField(default=False)

    class Meta:
        unique_together = (('organization', 'user'),)

    def __unicode__(self):
        return u'%s%s' % (
            self.user.get_short_name() or self.user.email,
            ' (admin)' if self.is_admin else '')
