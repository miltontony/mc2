from django.test import TransactionTestCase
from django.db.models import Q
from django.test.client import RequestFactory
from django.utils.text import slugify
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission

from mc2.organizations.models import Organization, OrganizationUserRelation


class OrganizationTestCase(TransactionTestCase):

    def mk_user(self, username='foobar', email='foobar@gmail.com',
                password='password', **kwargs):
        User = get_user_model()
        return User.objects.create_user(username, email, password, **kwargs)

    def mk_organization(self, name='Foo', users=[], **kwargs):
        fields = {
            'name': name,
            'slug': slugify(unicode(name))
        }
        fields.update(kwargs)
        org = Organization.objects.create(**fields)
        for user in users:
            OrganizationUserRelation.objects.create(
                user=user,
                organization=org,
                is_admin=True)
        return org

    def mk_request(self, method, *args, **kwargs):
        request = RequestFactory()
        request = getattr(request, method)(*args, **kwargs)
        request.session = {}
        return request

    def get_perms(self, perm):
        if isinstance(perm, basestring):
            perms = (perm,)
        else:
            perms = perm
        perms = [p.split('.', 1) for p in perms]
        filter_clauses = [
            Q(content_type__app_label=p[0], codename=p[1])
            for p in perms]
        perms_qs = Permission.objects.filter(
            reduce(lambda x, y: x | y, filter_clauses))
        if len(perms_qs) != len(perms):
            raise Permission.DoesNotExist
        return perms_qs

    def grant_perms(self, obj, perm):
        perms_field = ('permissions'
                       if isinstance(obj, Group)
                       else 'user_permissions')
        perms = list(self.get_perms(perm))
        getattr(obj, perms_field).add(*perms)

    def revoke_perms(self, obj, perm):
        perms_field = ('permissions'
                       if isinstance(obj, Group)
                       else 'user_permissions')
        perms = list(self.get_perms(perm))
        getattr(obj, perms_field).remove(*perms)
