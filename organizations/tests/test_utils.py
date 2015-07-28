from django.contrib.auth.models import AnonymousUser

from mock import patch

from organizations import context_processors
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

    def test_org_context_processor(self):
        user = self.mk_user()
        organization = self.mk_organization(users=[user])
        request = self.mk_request('get', '/')
        request.user = user
        request.session[ORGANIZATION_SESSION_KEY] = organization.pk
        context = context_processors.org(request)
        self.assertEqual(context['active_organization'], organization)
        self.assertEqual(set(context['organizations']), set([organization]))
        self.assertTrue(context['is_active_organization_admin'])

        with patch('organizations.context_processors.active_organization',
                   return_value=None):
            context = context_processors.org(request)
            self.assertEqual(context['active_organization'], None)
            self.assertEqual(
                set(context['organizations']), set([organization]))
            self.assertFalse(context['is_active_organization_admin'])

        organization.organizationuserrelation_set.filter(
            user=user).update(is_admin=False)
        context = context_processors.org(request)
        self.assertEqual(context['active_organization'], organization)
        self.assertEqual(set(context['organizations']), set([organization]))
        self.assertFalse(context['is_active_organization_admin'])

        request.user = AnonymousUser()
        context = context_processors.org(request)
        self.assertEqual(context['active_organization'], None)
        self.assertEqual(context['organizations'], [])
        self.assertFalse(context['is_active_organization_admin'])
