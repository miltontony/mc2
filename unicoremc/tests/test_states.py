from django.test import TestCase

from unicoremc.models import Project
from unicoremc.states import ProjectWorkflow


class PostTestCase(TestCase):

    def test_initial_state(self):
        p = Project(
            app_type='ffl',
            base_repo_url='http://some-git-repo.com',
            country='ZA')
        p.save()
        self.assertEquals(p.state, 'initial')

    def test_create_repo_state(self):
        p = Project(
            app_type='ffl',
            base_repo_url='http://some-git-repo.com',
            country='ZA')
        p.save()
        self.assertEquals(p.state, 'initial')

        pw = ProjectWorkflow(instance=p)
        pw.take_action('create_repo')

        self.assertEquals(
            p.repo_url,
            'http://new-git-repo/user/unicore-cms-content-ffl-za.git')
        self.assertEquals(p.state, 'repo_created')
