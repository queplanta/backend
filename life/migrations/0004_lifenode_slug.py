# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2016-11-12 21:24
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('life', '0003_auto_20161103_1632'),
    ]

    operations = [
        migrations.AddField(
            model_name='lifenode',
            name='slug',
            field=models.SlugField(max_length=512, null=True),
        ),
    ]
