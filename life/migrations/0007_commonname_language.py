# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2016-11-14 19:24
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('life', '0006_lifenode_gbif_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='commonname',
            name='language',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
