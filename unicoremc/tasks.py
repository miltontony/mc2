from celery import task

from elasticgit import EG


@task(serializer='json')
def start_new_controller(project_id):
    from controllers.base.models import Controller

    controller = Controller.objects.get(pk=project_id)
    controller.get_builder().build()


@task(serializer='json')
def push_to_git(repo_path):
    workspace = EG.workspace(repo_path)
    if workspace.repo.remotes:
        repo = workspace.repo
        remote = repo.remote()
        remote.fetch()
        remote_master = remote.refs.master
        remote.push(remote_master.remote_head)
