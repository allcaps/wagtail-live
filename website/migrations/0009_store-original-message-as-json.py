# Generated by Django 2.1.7 on 2019-03-17 21:48

import datetime
import django.contrib.postgres.fields.jsonb
from django.db import migrations, models
import wagtail.core.blocks
import wagtail.core.fields
import wagtail.embeds.blocks
import wagtail.images.blocks


class Migration(migrations.Migration):

    dependencies = [
        ('website', '0008_merge_20190314_1812'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='snippet',
            name='page',
        ),
        migrations.AddField(
            model_name='pendingupdate',
            name='json',
            field=django.contrib.postgres.fields.jsonb.JSONField(default='[]'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='liveblog',
            name='body',
            field=wagtail.core.fields.StreamField([('text', wagtail.core.blocks.StructBlock([('message_id', wagtail.core.blocks.CharBlock(required=False)), ('timestamp', wagtail.core.blocks.DateTimeBlock(required=False)), ('message', wagtail.core.blocks.TextBlock())])), ('image', wagtail.core.blocks.StructBlock([('message_id', wagtail.core.blocks.CharBlock(required=False)), ('timestamp', wagtail.core.blocks.DateTimeBlock(required=False)), ('image', wagtail.images.blocks.ImageChooserBlock())])), ('embed', wagtail.core.blocks.StructBlock([('message_id', wagtail.core.blocks.CharBlock(required=False)), ('timestamp', wagtail.core.blocks.DateTimeBlock(required=False)), ('embed', wagtail.embeds.blocks.EmbedBlock())]))], blank=True),
        ),
        migrations.AlterField(
            model_name='liveblog',
            name='last_updated',
            field=models.DateTimeField(default=datetime.datetime(1, 1, 2, 0, 0)),
        ),
        migrations.DeleteModel(
            name='Snippet',
        ),
    ]
