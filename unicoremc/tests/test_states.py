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

    def test_clone_repo_state(self):
        p = Project(
            app_type='ffl',
            base_repo_url='http://some-git-repo.com',
            country='ZA')
        p.save()

        pw = ProjectWorkflow(instance=p)
        pw.take_action('create_repo')
        pw.take_action('clone_repo')

        self.assertEquals(p.state, 'repo_cloned')

    def test_create_remote_state(self):
        p = Project(
            app_type='ffl',
            base_repo_url='http://some-git-repo.com',
            country='ZA')
        p.save()

        pw = ProjectWorkflow(instance=p)
        pw.take_action('create_repo')
        pw.take_action('clone_repo')
        pw.take_action('create_remote')

        self.assertEquals(p.state, 'remote_created')

    def test_merge_state(self):
        p = Project(
            app_type='ffl',
            base_repo_url='http://some-git-repo.com',
            country='ZA')
        p.save()

        pw = ProjectWorkflow(instance=p)
        pw.take_action('create_repo')
        pw.take_action('clone_repo')
        pw.take_action('create_remote')
        pw.take_action('merge_remote')

        self.assertEquals(p.state, 'remote_merged')
