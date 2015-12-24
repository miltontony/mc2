from django.core.exceptions import PermissionDenied
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser

from mock import patch, Mock

from mc2.organizations import context_processors
from mc2.organizations.tests.base import OrganizationTestCase
from mc2.organizations.utils import active_organization
from mc2.organizations.utils import org_permission_required
from mc2.organizations.models import (
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

        with patch('mc2.organizations.context_processors.active_organization',
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

    def test_org_permission_required(self):
        view_func = Mock(return_value='success')
        request = self.mk_request('get', '/')
        user = self.mk_user()
        request.user = user

        # test login redirect
        wrapped_view_func = org_permission_required(
            perm='organizations.change_organization',
            login_url='/login/')(view_func)
        response = wrapped_view_func(request)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, '/login/?next=http%3A//testserver/')

        # test that we can pass a list of perms
        wrapped_view_func = org_permission_required(
            perm=['organizations.change_organization',
                  'organizations.add_organization'],
            raise_exception=True)(view_func)
        self.assertRaises(PermissionDenied, wrapped_view_func, request)

        # test exception is raised
        wrapped_view_func = org_permission_required(
            perm='organizations.change_organization',
            raise_exception=True)(view_func)
        self.assertRaises(PermissionDenied, wrapped_view_func, request)

        self.grant_perms(user, 'organizations.change_organization')
        User = get_user_model()
        request.user = User.objects.get(id=user.pk)
        self.assertEqual(wrapped_view_func(request), 'success')

        self.revoke_perms(user, 'organizations.change_organization')
        request.user = User.objects.get(id=user.pk)
        self.assertRaises(PermissionDenied, wrapped_view_func, request)

        organization = self.mk_organization(users=[user])
        self.assertEqual(wrapped_view_func(request), 'success')

        request.session[ORGANIZATION_SESSION_KEY] = organization.pk
        self.assertEqual(wrapped_view_func(request), 'success')

        organization.organizationuserrelation_set.filter(
            user=user).update(is_admin=False)
        self.assertRaises(PermissionDenied, wrapped_view_func, request)
