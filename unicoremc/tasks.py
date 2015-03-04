from celery import task

from elasticgit import EG

from unicoremc.states import ProjectWorkflow


@task(serializer='json')
def start_new_project(project_id, access_token):
    from unicoremc.models import Project

    project = Project.objects.get(pk=project_id)
    workflow = ProjectWorkflow(instance=project)
    workflow.run_all(access_token=access_token)


@task(serializer='json')
def push_to_git(repo_path):
    workspace = EG.workspace(repo_path)
    if workspace.repo.remotes:
        print 'pushing to git started'
        repo = workspace.repo
        remote = repo.remote()
        remote.fetch()
        remote_master = remote.refs.master
        remote.push(remote_master.remote_head)
        print 'pushing to git finished'
