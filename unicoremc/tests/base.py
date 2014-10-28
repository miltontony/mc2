import json
import responses

from django.conf import settings
from elasticgit.tests.base import ModelBaseTest


class UnicoremcTestCase(ModelBaseTest):

    def mock_create_repo(self, status=201, data={}):
        default_response = {'clone_url': self.source_repo_sm.repo.git_dir}
        default_response.update(data)

        responses.add(
            responses.POST, settings.GITHUB_API + 'repos',
            body=json.dumps(default_response),
            content_type="application/json",
            status=status)
