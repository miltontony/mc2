import pytest

from django.contrib.auth.models import User

from unicoremc.tests.base import UnicoremcTestCase
from unicoremc.models import Project, AppType


@pytest.mark.django_db
class ModelsTestCase(UnicoremcTestCase):
    fixtures = ['test_users.json', 'test_social_auth.json']

    def setUp(self):
        self.user = User.objects.get(username='testuser')

    def test_app_type_title(self):
        app_type = AppType._for('gem', 'Girl Effect')
        self.assertEquals(str(app_type), 'Girl Effect')

    def test_project_app_type(self):
        app_type = AppType._for('gem', 'Girl Effect')

        p = Project(
            project_type='unicore-cms',
            base_repo_url='http://some-git-repo.com',
            country='ZA',
            owner=self.user)
        p.save()

        self.assertEquals(p.app_type, '')

        p = Project(
            project_type='unicore-cms',
            application_type=app_type,
            base_repo_url='http://some-git-repo.com',
            country='ZA',
            owner=self.user)
        p.save()

        self.assertEquals(p.app_type, 'gem')
