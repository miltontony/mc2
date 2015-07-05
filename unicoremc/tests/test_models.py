import pytest

from django.contrib.auth.models import User
from django.db.models.signals import post_save

from unicoremc.tests.base import UnicoremcTestCase
from unicoremc.models import Project, AppType, publish_to_websocket


@pytest.mark.django_db
class ModelsTestCase(UnicoremcTestCase):
    fixtures = ['test_users.json', 'test_social_auth.json']

    def setUp(self):
        self.user = User.objects.get(username='testuser')
        post_save.disconnect(publish_to_websocket, sender=Project)

    def test_app_type_title(self):
        app_type = AppType._for('gem', 'Girl Effect', 'unicore-cms')
        self.assertEquals(str(app_type), 'Girl Effect (unicore-cms)')

    def test_project_app_type(self):
        app_type = AppType._for('gem', 'Girl Effect', 'unicore-cms')

        p = Project(
            base_repo_url='http://some-git-repo.com',
            country='ZA',
            owner=self.user)
        p.save()

        self.assertEquals(p.app_type, '')

        p = Project(
            application_type=app_type,
            base_repo_url='http://some-git-repo.com',
            country='ZA',
            owner=self.user)
        p.save()

        self.assertEquals(p.app_type, 'gem')
