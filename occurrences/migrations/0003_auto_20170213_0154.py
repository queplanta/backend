# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2017-02-13 01:54
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('occurrences', '0002_auto_20170210_1543'),
    ]

    operations = [
        migrations.RenameField(
            model_name='suggestion',
            old_name='whatisthis',
            new_name='occurrence',
        ),
        migrations.AlterField(
            model_name='occurrence',
            name='document',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='+', to='db.DocumentID'),
        ),
        migrations.AlterField(
            model_name='occurrence',
            name='revision',
            field=models.OneToOneField(on_delete=django.db.models.deletion.PROTECT, primary_key=True, related_name='+', serialize=False, to='db.Revision'),
        ),
        migrations.AlterField(
            model_name='suggestion',
            name='document',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='+', to='db.DocumentID'),
        ),
        migrations.AlterField(
            model_name='suggestion',
            name='revision',
            field=models.OneToOneField(on_delete=django.db.models.deletion.PROTECT, primary_key=True, related_name='+', serialize=False, to='db.Revision'),
        ),
    ]