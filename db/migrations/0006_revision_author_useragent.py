# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2016-07-01 00:07
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('db', '0005_revision_author_ip'),
    ]

    operations = [
        migrations.AddField(
            model_name='revision',
            name='author_useragent',
            field=models.CharField(max_length=512, null=True),
        ),
    ]
