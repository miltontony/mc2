import mc2
from mc2.forms import UserSettingsForm


def default_forms(request):
    if request.user.is_authenticated():
        return {
            'user_settings_form': UserSettingsForm(
                instance=request.user.settings)
        }

    return {}


def app_version(request):
    return {
        'mc2_version': mc2.__version__
    }
