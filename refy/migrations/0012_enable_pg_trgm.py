import os

from django.contrib.postgres.operations import TrigramExtension
from django.db import migrations

_here = os.path.dirname(__file__)
_self = os.path.splitext(os.path.basename(__file__))[0]
_prev = max(f[:-3] for f in os.listdir(_here) if f[:4].isdigit() and f.endswith('.py') and f[:-3] < _self)


class Migration(migrations.Migration):
    dependencies = [('refy', _prev)]
    operations = [TrigramExtension()]
