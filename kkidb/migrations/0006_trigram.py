from django.contrib.postgres.operations import TrigramExtension
from django.db import migrations, models


class Migration(migrations.Migration):    

    dependencies = [
        ('kkidb', '0005_remove_member_username'),
    ]
    operations = [
        TrigramExtension(),
    ]