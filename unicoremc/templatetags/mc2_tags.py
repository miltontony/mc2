from django import template
from django_gravatar.templatetags.gravatar import gravatar_url

# Get template.Library instance
register = template.Library()

# enables the use of the gravatar_url as an assignment tag
register.assignment_tag(gravatar_url)


@register.simple_tag(takes_context=True)
def display_name(context):
    user = context['user']
    full_name = ' '.join([user.first_name, user.last_name]).strip()
    return full_name if full_name else user.username


@register.simple_tag(takes_context=True)
def load_skin(context):
    user = context['request'].user

    if not user.is_authenticated:
        t = template.loader.get_template('skins/basic.html')
        return t.render(context)

    try:
        t = template.loader.get_template(
            'skins/%s.html' % user.settings.settings_level)
    except template.TemplateDoesNotExist:
        t = template.loader.get_template('skins/basic.html')
    return t.render(context)


@register.filter
def multiply(value, factor):
    try:
        return value * factor
    except:
        pass
    return 0
