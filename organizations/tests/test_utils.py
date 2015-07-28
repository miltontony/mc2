from django.contrib.auth.models import AnonymousUser

from organizations.tests.base import OrganizationTestCase
from organizations.utils import active_organization
from organizations.models import (
    ORGANIZATION_SESSION_KEY, OrganizationUserRelation)


class TestUtils(OrganizationTestCase):

    def test_active_organization(self):
        request = self.mk_request('get', '/')
        request.user = AnonymousUser()
        self.assertIs(active_organization(request), None)

        user = self.mk_user()
        request.user = user
        self.assertIs(active_organization(request), None)

        organization = self.mk_organization()
        request.session[ORGANIZATION_SESSION_KEY] = organization.pk
        self.assertIs(active_organization(request), None)

        OrganizationUserRelation.objects.create(
            user=user, organization=organization)
        self.assertEqual(active_organization(request), organization)
