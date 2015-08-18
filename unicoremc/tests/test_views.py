import json
import os
import shutil
import pytest
import responses
from urlparse import urljoin

from django.conf import settings
from django.test import RequestFactory
from django.test.client import Client
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from django.db.models.signals import post_save

from unicoremc.constants import LANGUAGES
from unicoremc.models import (
    Project, Localisation, AppType, ProjectRepo, publish_to_websocket)
from unicoremc.managers import DbManager
from unicore.content.models import (
    Category, Page, Localisation as EGLocalisation)
from unicoremc.tests.base import UnicoremcTestCase
from unicoremc.tests.utils import setup_responses_for_logdriver
from unicoremc.views import AppEventSourceView

from mock import patch

from pycountry import languages


@pytest.mark.django_db
class ViewsTestCase(UnicoremcTestCase):
    fixtures = [
        'test_users.json', 'test_social_auth.json', 'test_organizations.json']

    def setUp(self):
        self.client = Client()
        self.client.login(username='testuser', password='test')
        self.user = User.objects.get(username='testuser')

        self.mk_test_repos()
        post_save.disconnect(publish_to_websocket, sender=Project)

    @responses.activate
    def test_create_new_project(self):
        existing_project = self.mk_project()

        self.client.login(username='testuser2', password='test')
        self.client.get(
            reverse('organizations:select-active', args=('foo-org',)))

        self.mock_create_repo()
        self.mock_create_webhook()
        self.mock_create_hub_app()
        self.mock_create_unicore_distribute_repo()
        self.mock_create_marathon_app()

        app_type = AppType._for(
            'ffl', 'Facts for Life', 'springboard',
            'universalcore/unicore-cms-ffl')

        data = {
            'app_type': app_type.id,
            'base_repo': self.base_repo_sm.repo.git_dir,
            'project_repos[]': existing_project.own_repo().pk,
            'country': 'ZA',
            'user_id': 1,
            'team_id': 1
        }

        with patch.object(DbManager, 'call_subprocess') as mock_subprocess:
            mock_subprocess.return_value = None
            response = self.client.post(reverse('new_project'), data)

        self.assertEqual(response['Content-Type'], 'application/json')
        self.assertEqual(json.loads(response.content), {
            'success': True
        })

        project = Project.objects.exclude(pk=existing_project.pk).get()
        self.assertEqual(project.state, 'done')
        self.assertEqual(
            project.frontend_url(),
            'http://ffl-za-%s.qa-hub.unicore.io' % project.id)
        self.assertEqual(
            project.frontend_custom_domain, 'za.ffl.qa-hub.unicore.io')
        self.assertEqual(
            project.cms_url(),
            'http://cms.ffl-za-%s.qa-hub.unicore.io' % project.id)
        self.assertEqual(
            project.cms_custom_domain, 'cms.za.ffl.qa-hub.unicore.io')
        self.assertEqual(project.external_repos.count(), 1)
        self.assertTrue(project.own_repo())
        self.assertEqual(len(project.all_repos()), 2)
        self.assertEqual(project.organization.slug, 'foo-org')

        workspace = self.mk_workspace(
            working_dir=settings.CMS_REPO_PATH,
            name='ffl-za',
            index_prefix='unicore_cms_ffl_za')

        self.assertEqual(workspace.S(Category).count(), 1)
        self.assertEqual(workspace.S(Page).count(), 1)
        self.assertEqual(workspace.S(EGLocalisation).count(), 1)

        cat = Category({
            'title': 'Some title',
            'slug': 'some-slug'
        })
        workspace.save(cat, 'Saving a Category')

        page = Page({
            'title': 'Some page title',
            'slug': 'some-page-slug'
        })
        workspace.save(page, 'Saving a Page')

        loc = EGLocalisation({
            'locale': 'spa_ES',
            'image': 'some-image-uuid',
            'image_host': 'http://some.site.com',
        })
        workspace.save(loc, 'Saving a Localisation')

        workspace.refresh_index()

        self.assertEqual(workspace.S(Category).count(), 2)
        self.assertEqual(workspace.S(Page).count(), 2)
        self.assertEqual(workspace.S(EGLocalisation).count(), 2)

        self.addCleanup(lambda: shutil.rmtree(
            os.path.join(settings.CMS_REPO_PATH, 'ffl-za')))

    @responses.activate
    def test_create_new_project_error(self):
        existing_project = self.mk_project()

        self.client.login(username='testuser2', password='test')

        app_type = AppType._for(
            'ffl', 'Facts for Life', 'unicore-cms',
            'universalcore/unicore-cms-ffl')

        data = {
            'app_type': app_type.id,
            'country': 'ZA',
            'user_id': 1,
            'team_id': 1
        }
        response = self.client.post(reverse('new_project'), data)

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.content, 'No repo selected')
        self.assertEqual(Project.objects.count(), 1)
        self.assertEqual(ProjectRepo.objects.count(), 1)

        data['base_repo'] = self.base_repo_sm.repo.git_dir,
        data['project_repos[]'] = existing_project.own_repo().pk,
        response = self.client.post(reverse('new_project'), data)

        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.content, 'unicore-cms does not support multiple repos')
        self.assertEqual(Project.objects.count(), 1)
        self.assertEqual(ProjectRepo.objects.count(), 1)

    @responses.activate
    def test_advanced_page(self):
        self.client.login(username='testuser2', password='test')

        self.mock_create_repo()
        self.mock_create_webhook()
        self.mock_create_hub_app()
        self.mock_create_unicore_distribute_repo()
        self.mock_create_marathon_app()

        english = Localisation._for('eng_UK')
        swahili = Localisation._for('swa_TZ')

        app_type = AppType._for(
            'ffl', 'Facts for Life', 'unicore-cms',
            'universalcore/unicore-cms-ffl')

        data = {
            'app_type': app_type.id,
            'project_type': 'unicore-cms',
            'base_repo': self.base_repo_sm.repo.git_dir,
            'country': 'ZA',
            'user_id': 1,
            'team_id': 1
        }

        with patch.object(DbManager, 'call_subprocess') as mock_subprocess:
            mock_subprocess.return_value = None
            self.client.post(reverse('new_project'), data)

        project = Project.objects.all().last()
        project.hub_app_id = None
        project.save()
        self.assertFalse(project.hub_app())

        frontend_settings_path = os.path.join(
            settings.FRONTEND_SETTINGS_OUTPUT_PATH,
            'ffl_za.ini')

        self.assertTrue(os.path.exists(frontend_settings_path))
        with open(frontend_settings_path, "r") as config_file:
            data = config_file.read()

        self.assertTrue("available_languages = []" in data)
        self.assertTrue('pyramid.default_locale_name = eng_GB' in data)
        self.assertFalse('ga.profile_id' in data)

        resp = self.client.get(reverse('advanced', args=[project.id]))

        self.assertContains(resp, 'English')
        self.assertContains(resp, 'Swahili')

        self.assertEqual(project.available_languages.count(), 0)
        self.assertIsNone(project.default_language)

        self.mock_update_marathon_app(
            project.app_type,
            project.country.lower(),
            project.id)

        resp = self.client.post(
            reverse('advanced', args=[project.id]), {
                'available_languages': [english.id, swahili.id],
                'default_language': [Localisation._for('swa_TZ').pk],
                'ga_profile_id': 'UA-some-profile-id',
                'frontend_custom_domain': 'some.domain.com',
                'cms_custom_domain': 'cms.some.domain.com',
                'marathon_cpus': 0.5,
                'marathon_mem': 100.0,
                'marathon_instances': 2,
                'marathon_health_check_path': '/health/',
                'docker_cmd': '/path/to/exec some command'
                })
        project = Project.objects.get(pk=project.id)
        self.assertEqual(project.available_languages.count(), 2)
        self.assertEqual(project.default_language.get_code(), 'swa_TZ')
        self.assertEqual(project.frontend_custom_domain, 'some.domain.com')
        self.assertEqual(project.cms_custom_domain, 'cms.some.domain.com')
        self.assertEqual(project.marathon_cpus, 0.5)
        self.assertEqual(project.marathon_mem, 100.0)
        self.assertEqual(project.marathon_instances, 2)
        self.assertEqual(project.marathon_health_check_path, '/health/')
        self.assertEqual(project.docker_cmd, '/path/to/exec some command')
        self.assertTrue(project.hub_app_id)

        frontend_settings_path = os.path.join(
            settings.FRONTEND_SETTINGS_OUTPUT_PATH,
            'ffl_za.ini')

        with open(frontend_settings_path, "r") as config_file:
            data = config_file.read()

        self.assertTrue(
            "[(u'eng_UK', u'English'), "
            "(u'swa_TZ', u'Swahili')]" in data)
        self.assertTrue('pyramid.default_locale_name = swa_TZ' in data)
        self.assertTrue('ga.profile_id = UA-some-profile-id' in data)

        self.addCleanup(lambda: shutil.rmtree(
            os.path.join(settings.CMS_REPO_PATH, 'ffl-za')))

    def test_view_only_on_homepage(self):
        resp = self.client.get(reverse('home'))
        self.assertNotContains(resp, 'Start new project')
        self.assertNotContains(resp, 'edit')

        self.client.login(username='testuser2', password='test')

        resp = self.client.get(reverse('home'))
        self.assertContains(resp, 'Start new project')

    def test_staff_access_required(self):
        self.mk_project(project={'owner': User.objects.get(pk=2)})

        resp = self.client.get(reverse('new_project'))
        self.assertEqual(resp.status_code, 302)

        resp = self.client.post(reverse('new_project'), {})
        self.assertEqual(resp.status_code, 302)

        resp = self.client.get(reverse('advanced', args=[1]))
        self.assertEqual(resp.status_code, 302)

    @responses.activate
    def test_get_repos(self):
        self.mock_list_repos()
        resp = self.client.get(reverse('repos_json'), {'refresh': 'true'})
        resp_json = json.loads(resp.content)
        self.assertEquals(
            resp_json[0], {
                'clone_url':
                    'https://github.com/universalcore/unicore-cms.git',
                'git_url': 'git://github.com/universalcore/unicore-cms.git',
                'name': 'unicore-cms'}
        )
        self.assertEqual(resp['Content-Type'], 'application/json')

    @responses.activate
    def test_get_repos_no_repos(self):
        self.mock_list_repos(data=[])
        resp = self.client.get(reverse('repos_json'))
        resp_json = json.loads(resp.content)
        self.assertIs(resp_json, None)
        self.assertEqual(resp['Content-Type'], 'application/json')

    @responses.activate
    def test_get_teams(self):
        self.mock_get_teams()
        resp = self.client.get(reverse('teams_json'))
        resp_json = json.loads(resp.content)
        self.assertEqual(resp_json, [{
            'repositories_url': 'https://api.github.com/teams/1/repos',
            'members_url':
                'https://api.github.com/teams/1/members{/member}',
            'description': '',
            'permission': 'push',
            'url': 'https://api.github.com/teams/1',
            'id': 1,
            'slug': 'foo',
            'name': 'Foo'
        }])
        self.assertEqual(resp['Content-Type'], 'application/json')

    @patch('unicoremc.utils.create_ga_profile')
    @patch('unicoremc.utils.get_ga_accounts')
    def test_manage_ga(self, mock_get_ga_accounts, mock_create_ga_profile):
        mock_get_ga_accounts.return_value = [
            {'id': '1', 'name': 'Account 1'},
            {'id': '2', 'name': 'GEM Test Account'},
        ]
        mock_create_ga_profile.return_value = "UA-some-new-profile-id"

        p = self.mk_project(
            project={'owner': User.objects.get(pk=2), 'state': 'done'})
        self.mk_project(
            project={'owner': User.objects.get(pk=2)},
            app_type={'name': 'gem', 'title': 'Girl Effect Mobile',
                      'project_type': 'unicore-cms'})

        self.client.login(username='testuser2', password='test')
        resp = self.client.get(reverse('manage_ga'))
        self.assertContains(resp, 'Facts for Life')
        self.assertNotContains(resp, 'Girl Effect Mobile')
        self.assertContains(resp, 'Account 1')
        self.assertContains(resp, 'GEM Test Account')

        data = {
            'account_id': 'some-account-id',
            'project_id': p.id,
        }
        resp = self.client.post(reverse('manage_ga'), data)
        self.assertEqual(resp['Content-Type'], 'application/json')
        self.assertEqual(json.loads(resp.content), {
            'ga_profile_id': 'UA-some-new-profile-id'
        })
        p = Project.objects.get(pk=p.id)
        self.assertEqual(p.ga_profile_id, 'UA-some-new-profile-id')
        self.assertEqual(p.ga_account_id, 'some-account-id')

        resp = self.client.post(reverse('manage_ga'), data)
        self.assertEqual(resp.status_code, 403)
        self.assertEqual(resp.content, "Project already has a profile")

    def test_all_language_codes(self):
        for k, v in LANGUAGES.items():
            lang = languages.get(bibliographic=k)
            self.assertEqual(lang.bibliographic, k)

    @responses.activate
    def test_reset_hub_app_key(self):
        self.mock_create_hub_app()
        self.client.login(username='testuser2', password='test')

        proj = self.mk_project(project={
            'owner': User.objects.get(pk=2),
            'state': 'done'})
        proj.create_or_update_hub_app()
        app_data = proj.hub_app().data
        app_data_with_new_key = app_data.copy()
        app_data_with_new_key['key'] = 'iamanewkey'

        responses.reset()
        responses.add(
            responses.GET,
            urljoin(settings.HUBCLIENT_SETTINGS['host'],
                    'apps/%s' % app_data['uuid']),
            body=json.dumps(app_data),
            status=200,
            content_type='application/json')
        responses.add(
            responses.PUT,
            urljoin(settings.HUBCLIENT_SETTINGS['host'],
                    'apps/%s/reset_key' % app_data['uuid']),
            body=json.dumps(app_data_with_new_key),
            status=200,
            content_type='application/json')

        resp = self.client.get(reverse('reset-hub-app-key', args=(proj.id, )))
        self.assertRedirects(resp, reverse('advanced', args=(proj.id, )))
        self.assertEqual(len(responses.calls), 2)
        self.assertIn(
            '%s/reset_key' % app_data['uuid'],
            responses.calls[-1].request.url)

        frontend_settings_path = os.path.join(
            settings.FRONTEND_SETTINGS_OUTPUT_PATH,
            'ffl_za.ini')

        with open(frontend_settings_path, "r") as config_file:
            data = config_file.read()

        self.assertIn('unicorehub.app_key = iamanewkey', data)

    @responses.activate
    def test_applog_view(self):
        self.client.login(username='testuser2', password='test')
        project = self.mk_project(project={
            'owner': User.objects.get(pk=2),
            'state': 'done'})
        setup_responses_for_logdriver(project)
        response = self.client.get(reverse('logs', kwargs={
            'project_id': project.pk,
        }))
        [task] = response.context['tasks']
        self.assertEqual(task['id'], '%s.the-task-id' % (project.app_id,))
        [task_id] = response.context['task_ids']
        self.assertEqual(task_id, 'the-task-id')

    @responses.activate
    def test_event_source_response_stdout(self):
        self.client.login(username='testuser2', password='test')
        project = self.mk_project(project={
            'owner': User.objects.get(pk=2),
            'state': 'done'})
        setup_responses_for_logdriver(project)
        resp = self.client.get(reverse('logs_event_source', kwargs={
            'project_id': project.pk,
            'task_id': 'the-task-id',
            'path': 'stdout',
        }))
        self.assertEqual(
            resp['X-Accel-Redirect'],
            os.path.join(
                settings.LOGDRIVER_PATH,
                ('/worker-machine-id'
                 '/frameworks/the-framework-id/executors'
                 '/ffl-za-1.the-task-id/runs/latest/stdout')))
        self.assertEqual(resp['X-Accel-Buffering'], 'no')

    @responses.activate
    def test_event_source_response_stderr(self):
        self.client.login(username='testuser2', password='test')
        project = self.mk_project(project={
            'owner': User.objects.get(pk=2),
            'state': 'done'})
        setup_responses_for_logdriver(project)
        resp = self.client.get(reverse('logs_event_source', kwargs={
            'project_id': project.pk,
            'task_id': 'the-task-id',
            'path': 'stderr',
        }))
        self.assertEqual(
            resp['X-Accel-Redirect'],
            os.path.join(
                settings.LOGDRIVER_PATH,
                ('/worker-machine-id'
                 '/frameworks/the-framework-id/executors'
                 '/ffl-za-1.the-task-id/runs/latest/stderr')))
        self.assertEqual(resp['X-Accel-Buffering'], 'no')

    @responses.activate
    def test_event_source_response_badpath(self):
        self.client.login(username='testuser2', password='test')
        project = self.mk_project(project={
            'owner': User.objects.get(pk=2),
            'state': 'done'})
        setup_responses_for_logdriver(project)
        # NOTE: bad path according to URL regex, hence the manual requesting
        view = AppEventSourceView()
        response = view.get(RequestFactory().get('/'), project.pk,
                            'the-task-id', 'foo')
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.content, 'File not found.')
