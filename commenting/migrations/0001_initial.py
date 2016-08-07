# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2016-07-02 02:18
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
import django.db.models.manager


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('db', '0006_revision_author_useragent'),
    ]

    operations = [
        migrations.CreateModel(
            name='Comment',
            fields=[
                ('revision', models.OneToOneField(on_delete=django.db.models.deletion.PROTECT, primary_key=True, serialize=False, to='db.Revision')),
                ('is_tip', models.NullBooleanField()),
                ('is_deleted', models.NullBooleanField()),
                ('body', models.TextField()),
                ('document', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='db.DocumentID')),
                ('parent', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='comments', to='db.DocumentID')),
            ],
            options={
                'abstract': False,
            },
            managers=[
                ('objects_revisions', django.db.models.manager.Manager()),
            ],
        ),
        migrations.AlterUniqueTogether(
            name='comment',
            unique_together=set([('is_tip', 'document')]),
        ),
    ]
