# This is a workaround for https://github.com/DRMacIver/hypothesis/issues/283
# When https://github.com/DRMacIver/hypothesis/pull/285 has been released we
# can kill it and just depend on the relevant Hypothesis version.

import django.db.models as dm

import hypothesis.strategies as st
from hypothesis.errors import InvalidArgument
from hypothesis.extra.django.models import field_mappings, ModelStrategy

DEFAULT_VALUE = object()


def models(model, **extra):
    result = {}
    mappings = field_mappings()
    mandatory = set()
    for f in model._meta.concrete_fields:
        if isinstance(f, dm.AutoField):
            continue
        try:
            mapped = mappings[type(f)]
        except KeyError:
            if not f.null:
                mandatory.add(f.name)
            continue
        if f.null:
            mapped = st.one_of(st.none(), mapped)
        result[f.name] = mapped
    missed = {x for x in mandatory if x not in extra}
    if missed:
        raise InvalidArgument((
            u'Missing arguments for mandatory field%s %s for model %s' % (
                u's' if len(missed) > 1 else u'',
                u', '.join(missed),
                model.__name__,
            )))
    for k, v in extra.items():
        if v is not DEFAULT_VALUE:
            result[k] = v
    return ModelStrategy(model, result)
