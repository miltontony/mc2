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
        repo = workspace.repo
        print 'fetch started..'
        remote = repo.remote()
        finfo = remote.fetch()[0]
        print finfo.ref
        print finfo.flags
        print finfo.note
        print finfo.old_commit
        remote_master = remote.refs.master
        print 'push started..'
        info = remote.push(remote_master.remote_head)[0]
        print info.local_ref
        print info.remote_ref_string
        print info.flags
        print info.old_commit
        print info.summary
