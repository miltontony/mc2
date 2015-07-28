from django.test import TransactionTestCase
from django.test.client import RequestFactory
from django.utils.text import slugify
from django.contrib.auth import get_user_model

from organizations.models import Organization, OrganizationUserRelation


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
