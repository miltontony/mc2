from django.test import TestCase, Client
from django.contrib.auth.models import User

from mc2 import permissions
from mc2.organizations.models import Organization, OrganizationUserRelation
from mc2.controllers.docker.models import DockerController

import pytest


@pytest.mark.django_db
class LoginTest(TestCase):
    def test_email_login_successful(self):
        user = User.objects.create_user(
            first_name='foo', username="foo@example.com",
            email="foo@example.com", password="1234")
        client = Client()
        response = client.get('/')
        self.assertRedirects(response, '/login/?next=/')

        response = client.post(
            '/login/?next=/', {'username': user.username, 'password': '1234'})
        self.assertRedirects(response, '/')

    def test_email_login_unsuccessful(self):
        user = User.objects.create_user(
            first_name='foo', username="foo@example.com",
            email="foo@example.com", password="1234")
        client = Client()
        response = client.get('/')
        self.assertRedirects(response, '/login/?next=/')

        response = client.post(
            '/login/?next=/', {'username': user.username, 'password': '123'})
        self.assertContains(response, 'name or password is not correct')

    def test_email_login_sso(self):
        user = User.objects.create_user(
            first_name='foo', username="foo@example.com",
            email="foo@example.com", password="1234")
        client = Client()
        response = client.get(
            '/login?service=http%3A%2F%2Ftestapp.com%2F'
            'admin%2Flogin%2F%3Fnext%3D%252Fadmin%252F')
        self.assertContains(response, 'Welcome to Mission Control')
        response = client.post(
            ('/login?service=http%3A%2F%2Ftestapp.com%2F'
             'admin%2Flogin%2F%3Fnext%3D%252Fadmin%252F'),
            {'username': user.username, 'password': '1234'})
        self.assertEquals(
            response.request.get('QUERY_STRING'),
            ('service=http%3A%2F%2Ftestapp.com%2Fadmin%2Flogin'
             '%2F%3Fnext%3D%252Fadmin%252F'))

    def test_login_sso_redirects_to_home_when_no_service(self):
        user = User.objects.create_user(
            first_name='foo', username="foo@example.com",
            email="foo@example.com", password="1234")
        client = Client()
        response = client.post(
            ('/login?service=None'),
            {'username': user.username, 'password': '1234'}, follow=True)
        self.assertRedirects(response, '/')


@pytest.mark.django_db
class CustomAttributesTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            'testuser', 'test@email.com', '1234')
        self.client = Client()

    def test_group_access(self):
        user = User.objects.create(first_name='foo')
        attr = permissions.org_permissions(user, 'http://foobar.com/')
        self.assertEqual(attr['has_perm'], False)

    def test_user_details(self):
        user = User.objects.create(first_name='foo', email='foo@email.com')
        attr = permissions.org_permissions(user, 'http://foobar.com/')
        self.assertEqual(attr['givenName'], 'foo')
        self.assertEqual(attr['email'], 'foo@email.com')

    def test_org_admin_must_have_superuser_access(self):
        user = User.objects.create_user('joe', 'joe@email.com', '1234')
        org = Organization.objects.create(name='Test', slug='test')
        OrganizationUserRelation.objects.create(
            user=user, organization=org, is_admin=True)
        DockerController.objects.create(
            name='my test app', organization=org,
            owner=user, domain_urls='foobar.com')
        self.client.login(username='joe', password='1234')

        attr = permissions.org_permissions(user, 'http://foobar1.com/')
        self.assertEqual(attr['has_perm'], False)
        self.assertEqual(attr['is_admin'], False)

        attr = permissions.org_permissions(user, 'http://foobar.com/')
        self.assertEqual(attr['has_perm'], True)
        self.assertEqual(attr['is_admin'], True)

    def test_super_user_must_have_super_user_access(self):
        org = Organization.objects.create(name='Test', slug='test')
        OrganizationUserRelation.objects.create(
            user=self.user, organization=org, is_admin=True)

        joe = User.objects.create_superuser('joe', 'joe@email.com', '1234')
        self.client.login(username='joe', password='1234')

        attr = permissions.org_permissions(joe, 'http://foobar.com/')
        self.assertEqual(attr['has_perm'], True)
        self.assertEqual(attr['is_admin'], True)

        attr = permissions.org_permissions(joe, 'http://test-app.molo.site/')
        self.assertEqual(attr['has_perm'], True)
        self.assertEqual(attr['is_admin'], True)

    def test_user_in_org_must_have_access(self):
        org = Organization.objects.create(name='Test', slug='test')
        OrganizationUserRelation.objects.create(
            user=self.user, organization=org, is_admin=True)

        DockerController.objects.create(
            name='my test app', organization=org,
            owner=self.user, domain_urls='test-app.molo.site my.domain.com')

        # joe is a normal user in the org (is_admin = False)
        joe = User.objects.create_user('joe', 'joe@email.com', '1234')
        OrganizationUserRelation.objects.create(
            user=joe, organization=org)
        # create the controller as testuser
        self.client.login(username='testuser', password='1234')

        attr = permissions.org_permissions(joe, 'http://foobar.com/')
        self.assertEqual(attr['has_perm'], False)
        self.assertEqual(attr['is_admin'], False)

        attr = permissions.org_permissions(joe, 'http://test-app.molo.site/')
        self.assertEqual(attr['has_perm'], True)
        self.assertEqual(attr['is_admin'], False)

    def test_app_admin_user_in_org_must_have_admin_access_for_the_app(self):
        org = Organization.objects.create(name='Test', slug='test')
        OrganizationUserRelation.objects.create(
            user=self.user, organization=org, is_admin=True)

        DockerController.objects.create(
            name='my test app', organization=org,
            owner=self.user, domain_urls='test-app.molo.site my.domain.com')

        # joe is an app admin user in the org (is_app_admin = True)
        joe = User.objects.create_user('joe', 'joe@email.com', '1234')
        OrganizationUserRelation.objects.create(
            user=joe, organization=org, is_app_admin=True)
        # create the controller as testuser
        self.client.login(username='testuser', password='1234')

        attr = permissions.org_permissions(joe, 'http://foobar.com/')
        self.assertEqual(attr['has_perm'], False)
        self.assertEqual(attr['is_admin'], False)

        attr = permissions.org_permissions(joe, 'http://test-app.molo.site/')
        self.assertEqual(attr['has_perm'], True)
        self.assertEqual(attr['is_admin'], True)

    def test_user_in_other_org_must_not_have_cross_access(self):
        org = Organization.objects.create(name='Test', slug='test')
        OrganizationUserRelation.objects.create(
            user=self.user, organization=org, is_admin=True)

        # joe is a normal user in the org (is_admin = False)
        joe = User.objects.create_user('joe', 'joe@email.com', '1234')
        OrganizationUserRelation.objects.create(
            user=joe, organization=org)

        DockerController.objects.create(
            name='my test app', organization=org,
            owner=self.user, domain_urls='foobar.com')

        # sam is a normal user in other org
        sam = User.objects.create_user('sam', 'sam@email.com', '1234')
        other_org = Organization.objects.create(name='Other', slug='other')
        OrganizationUserRelation.objects.create(
            user=sam, organization=other_org)

        DockerController.objects.create(
            name='my test app', organization=other_org,
            owner=self.user, domain_urls='test-app.molo.site')

        attr = permissions.org_permissions(joe, 'http://foobar.com/')
        self.assertEqual(attr['has_perm'], True)
        self.assertEqual(attr['is_admin'], False)

        attr = permissions.org_permissions(sam, 'http://foobar.com/')
        self.assertEqual(attr['has_perm'], False)
        self.assertEqual(attr['is_admin'], False)

        attr = permissions.org_permissions(joe, 'http://test-app.molo.site/')
        self.assertEqual(attr['has_perm'], False)
        self.assertEqual(attr['is_admin'], False)

        attr = permissions.org_permissions(sam, 'http://test-app.molo.site/')
        self.assertEqual(attr['has_perm'], True)
        self.assertEqual(attr['is_admin'], False)

        # tom is an admin user in other org
        tom = User.objects.create_user('tom', 'tom@email.com', '1234')
        OrganizationUserRelation.objects.create(
            user=tom, organization=other_org, is_admin=True)

        attr = permissions.org_permissions(tom, 'http://foobar.com/')
        self.assertEqual(attr['has_perm'], False)
        self.assertEqual(attr['is_admin'], False)

        attr = permissions.org_permissions(tom, 'http://test-app.molo.site/')
        self.assertEqual(attr['has_perm'], True)
        self.assertEqual(attr['is_admin'], True)

        attr = permissions.org_permissions(sam, 'http://test-app.molo.site/')
        self.assertEqual(attr['has_perm'], True)
        self.assertEqual(attr['is_admin'], False)

    def test_access_using_generic_domain(self):
        user = User.objects.create_user('joe', 'joe@email.com', '1234')
        org = Organization.objects.create(name='Test', slug='test')
        OrganizationUserRelation.objects.create(
            user=user, organization=org, is_admin=True)

        self.client.login(username='joe', password='1234')

        controller = DockerController.objects.create(
            name='my test app', organization=org,
            owner=self.user, slug='test-app')

        attr = permissions.org_permissions(
            user, 'http://%s.seed.p16n.org/admin/' % controller.app_id)
        self.assertEqual(attr['has_perm'], True)
        self.assertEqual(attr['is_admin'], True)
