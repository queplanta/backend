# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2016-06-26 00:08
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('db', '0002_documentid_revisions_count'),
    ]

    operations = [
        migrations.RenameField(
            model_name='documentid',
            old_name='version_tip_id',
            new_name='revision_tip_id',
        ),
    ]
