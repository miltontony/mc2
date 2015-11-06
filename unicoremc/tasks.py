from celery import task


@task(serializer='json')
def start_new_controller(project_id):
    from controllers.base.models import Controller

    controller = Controller.objects.get(pk=project_id).as_leaf_class()
    controller.get_builder().build()
