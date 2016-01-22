from django.test import TestCase, Client
from mc2 import permissions
from django.contrib.auth.models import User, Group
from mc2.models import AuthorizedSite
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

    def test_group_access(self):
        user = User.objects.create(first_name='foo')
        attr = permissions.custom_attributes(user, 'http://foobar.com/')
        self.assertEqual(attr['has_perm'], False)

    def test_correct_user(self):
        user = User.objects.create(first_name='foo')
        attr = permissions.custom_attributes(user, 'http://foobar.com/')
        self.assertEqual(attr['givenName'], 'foo')

    def test_correct_group(self):
        user = User.objects.create(first_name=' ')
        attr = permissions.custom_attributes(user, 'http://foobar.com/')
        self.assertEqual(len(attr['groups']), 0)

        group = Group.objects.create(name='The Foo')
        user.groups.add(group)
        user.save()
        site = AuthorizedSite.objects.create(site='http://foobar.com/*')
        site.group.add(group)
        site.save()

        attr = permissions.custom_attributes(user, 'http://foobar.com/')
        self.assertEqual(len(attr['groups']), 1)
        self.assertEqual(attr['groups'], ['The Foo'])

    def test_wildcard_url(self):
        user = User.objects.create(first_name='foo')
        group = Group.objects.create(name='Unicef')
        user.groups.add(group)
        user.save()

        site = AuthorizedSite.objects.create(
            site='http://*.fflangola.qa-hub.unicore.io/*')
        site.group.add(group)
        site.save()

        attr = permissions.custom_attributes(
            user, 'http://cms.tz.fflangola.qa-hub.unicore.io/login/')
        self.assertEqual(attr['has_perm'], True)
        self.assertEqual(attr['groups'], ['Unicef'])

        attr = permissions.custom_attributes(
            user, 'http://cms.za.fflangola.qa-hub.unicore.io/login/')
        self.assertEqual(attr['has_perm'], True)

        attr = permissions.custom_attributes(
            user, 'http://cms.za.ffl.qa-hub.unicore.io/login/')
        self.assertEqual(attr['has_perm'], False)

        attr = permissions.custom_attributes(
            user, 'http://cms.za.gem.qa-hub.unicore.io/login/')
        self.assertEqual(attr['has_perm'], False)

    def test_exact_match_site(self):
        user = User.objects.create(first_name='foo')
        group = Group.objects.create(name='MAMA')
        user.groups.add(group)
        user.save()

        site = AuthorizedSite.objects.create(
            site='http://cms.za.mama.qa-hub.unicore.io/*')
        site.group.add(group)
        site.save()

        attr = permissions.custom_attributes(
            user, 'http://cms.za.mama.qa-hub.unicore.io/login/')
        self.assertEqual(attr['has_perm'], True)
        self.assertEqual(attr['groups'], ['MAMA'])

        attr = permissions.custom_attributes(
            user, 'htto://cms.za.mama.qa-hub.unicore.io/login/')  # deliberate
        self.assertEqual(attr['has_perm'], False)

        attr = permissions.custom_attributes(
            user, 'ssh://cms.za.mama.qa-hub.unicore.io/login/')
        self.assertEqual(attr['has_perm'], False)

    def test_multiple_groups(self):
        group_mama = Group.objects.create(name='MAMA')
        group_gem = Group.objects.create(name='GEM')
        group_prk = Group.objects.create(name='Praekelt')

        user_mama = User.objects.create(username='mamauser')
        user_mama.groups.add(group_mama)
        user_mama.save()

        user_gem = User.objects.create(username='gemuser')
        user_gem.groups.add(group_gem)
        user_gem.save()

        site = AuthorizedSite.objects.create(
            site='http://cms.za.mama.qa-hub.unicore.io/*')
        site.group.add(*[group_prk, group_mama])
        site.save()

        attr = permissions.custom_attributes(
            user_mama, 'http://cms.za.mama.qa-hub.unicore.io/login/')
        self.assertEqual(attr['has_perm'], True)

        attr = permissions.custom_attributes(
            user_gem, 'http://cms.za.mama.qa-hub.unicore.io/login/')
        self.assertEqual(attr['has_perm'], False)
