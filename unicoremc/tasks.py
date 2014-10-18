from celery import task
from unicoremc.models import Project
from unicoremc.states import ProjectWorkflow


@task(serializer='json')
def start_new_project(project_id):
    project = Project.objects.get(project_id)
    workflow = ProjectWorkflow(instance=project)
    workflow.run_all()
