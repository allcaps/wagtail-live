# Generated by Django 2.1.7 on 2019-03-16 10:41

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('website', '0009_auto_20190315_1221'),
    ]

    operations = [
        migrations.AlterField(
            model_name='liveblog',
            name='last_updated',
            field=models.DateTimeField(default=datetime.datetime(1, 1, 2, 0, 0)),
        ),
    ]
