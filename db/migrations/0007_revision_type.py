# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2016-08-12 19:07
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('db', '0006_revision_author_useragent'),
    ]

    operations = [
        migrations.AddField(
            model_name='revision',
            name='type',
            field=models.CharField(choices=[('create', 'Create'), ('change', 'Change'), ('delete', 'Delete')], default='change', max_length=6),
            preserve_default=False,
        ),
    ]