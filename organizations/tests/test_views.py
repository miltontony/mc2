from django.core.urlresolvers import reverse
from django.utils.http import urlencode, urlquote

from organizations.tests.base import OrganizationTestCase
from organizations.models import ORGANIZATION_SESSION_KEY


class TestViews(OrganizationTestCase):

    def setUp(self):
        self.user = self.mk_user()
        self.organization = self.mk_organization(users=[self.user])

    def assertLoginRequired(self, url):
        self.client.logout()
        self.assertRedirects(self.client.get(url), '%s?next=%s' % (
            reverse('login'), urlquote(url)))

    def test_select_active_organization(self):
        redirect_url = reverse(
            'organizations:edit', args=(self.organization.slug,))
        url = '%s?%s' % (reverse(
            'organizations:select-active', args=(self.organization.slug,)),
            urlencode({'next': redirect_url}))

        self.assertLoginRequired(url)

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
