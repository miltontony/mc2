from django.core.urlresolvers import reverse
from django.utils.http import urlencode, urlquote

from mc2.organizations.tests.base import OrganizationTestCase
from mc2.organizations.models import ORGANIZATION_SESSION_KEY
from mc2.organizations.forms import OrganizationFormHelper


class TestViews(OrganizationTestCase):

    def setUp(self):
        self.user = self.mk_user()
        self.organization = self.mk_organization(users=[self.user])
        self.client.login(username=self.user.username, password='password')

    def test_select_active_organization(self):
        redirect_url = (
            "http://testserver/")
        url = '%s?%s' % (reverse(
            'organizations:select-active', args=(self.organization.slug,)),
            urlencode({'next': redirect_url}))

        self.client.logout()
        self.assertRedirects(self.client.get(url), '%s?next=%s' % (
            reverse('login'), urlquote(url)))

        self.client.login(username=self.user.username, password='password')
        response = self.client.get(url)
        self.assertRedirects(response, redirect_url)
        self.assertEqual(
            self.client.session.get(ORGANIZATION_SESSION_KEY),
            self.organization.pk)

        # check redirect for missing next param and external redirect
        url = reverse(
            'organizations:select-active', args=(self.organization.slug,))
        self.assertRedirects(self.client.get(url), reverse('home'))
        url = '%s?%s' % (reverse(
            'organizations:select-active', args=(self.organization.slug,)),
            urlencode({'next': 'http://google.com'}))
        self.assertRedirects(self.client.get(url), reverse('home'))

        self.organization.organizationuserrelation_set.filter(
            user=self.user).delete()
        self.assertEqual(self.client.get(url).status_code, 404)

    def test_deselect_active_organization(self):
        redirect_url = reverse(
            'organizations:edit', args=(self.organization.slug,))
        url = '%s?%s' % (
            reverse('organizations:deselect-active'),
            urlencode({'next': redirect_url}))

        self.client.login(username=self.user.username, password='password')
        self.client.get(reverse(
            'organizations:select-active', args=(self.organization.slug,)))
        self.assertIn(ORGANIZATION_SESSION_KEY, self.client.session)

        response = self.client.get(url)
        self.assertRedirects(response, redirect_url)
        self.assertNotIn(ORGANIZATION_SESSION_KEY, self.client.session)

        # check redirect for missing next param and external redirect
        url = reverse('organizations:deselect-active')
        self.assertRedirects(self.client.get(url), reverse('home'))
        url = '%s?%s' % (reverse(
            'organizations:deselect-active'),
            urlencode({'next': 'http://google.com'}))
        self.assertRedirects(self.client.get(url), reverse('home'))

    def test_edit_organization(self):
        url = reverse('organizations:edit', args=(self.organization.slug,))
        response = self.client.get(url)
        form = response.context['form']
        self.assertContains(response, self.user.email)
        self.assertIsInstance(form, OrganizationFormHelper)
        self.assertEqual(
            form.organization_form.initial, {'name': self.organization.name})
        self.assertEqual(
            form.users_formset[0].initial,
            {'is_admin': True, 'organization': self.organization.pk})

    def test_edit_organization_no_admin_permission(self):
        url = reverse('organizations:edit', args=(self.organization.slug,))
        self.organization.organizationuserrelation_set.update(is_admin=False)
        self.assertEqual(self.client.get(url).status_code, 404)
