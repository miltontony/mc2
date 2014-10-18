from django.db import models
from unicoremc.constants import COUNTRIES


class Project(models.Model):
    FFL = 'ffl'
    GEM = 'gem'
    EBOLA = 'ebola'
    MAMA = 'mama'

    APP_TYPES = (
        (FFL, 'Facts for Life'),
        (GEM, 'Girl Effect Mobile'),
        (EBOLA, 'Ebola Information'),
        (MAMA, 'MAMA Baby Center')
    )

    app_type = models.CharField(choices=APP_TYPES, max_length=10)
    base_repo_url = models.URLField()
    country = models.CharField(choices=COUNTRIES, max_length=2)
    state = models.CharField(max_length=50, default='initial')
    repo_url = models.URLField(blank=True, null=True)
    owner = models.ForeignKey('auth.User')
