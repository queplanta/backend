# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2017-02-12 01:05
from __future__ import unicode_literals

import db.fields
from django.db import migrations, models
import django.db.models.deletion
import django.db.models.manager


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('db', '0008_documentid_owner'),
    ]

    operations = [
        migrations.CreateModel(
            name='Page',
            fields=[
                ('revision', models.OneToOneField(on_delete=django.db.models.deletion.PROTECT, primary_key=True, related_name='+', serialize=False, to='db.Revision')),
                ('is_tip', models.NullBooleanField()),
                ('is_deleted', models.NullBooleanField()),
                ('title', models.CharField(max_length=255)),
                ('slug', models.SlugField(max_length=255)),
                ('document', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='+', to='db.DocumentID')),
                ('tags', db.fields.ManyToManyField(related_name='test_post_tagged', to='db.DocumentID')),
            ],
            managers=[
                ('objects_revisions', django.db.models.manager.Manager()),
            ],
        ),
        migrations.CreateModel(
            name='Tag',
            fields=[
                ('revision', models.OneToOneField(on_delete=django.db.models.deletion.PROTECT, primary_key=True, related_name='+', serialize=False, to='db.Revision')),
                ('is_tip', models.NullBooleanField()),
                ('is_deleted', models.NullBooleanField()),
                ('title', models.CharField(max_length=255)),
                ('slug', models.SlugField(max_length=255)),
                ('document', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='+', to='db.DocumentID')),
            ],
            managers=[
                ('objects_revisions', django.db.models.manager.Manager()),
            ],
        ),
        migrations.AlterUniqueTogether(
            name='tag',
            unique_together=set([('is_tip', 'slug')]),
        ),
        migrations.AlterUniqueTogether(
            name='page',
            unique_together=set([('is_tip', 'slug')]),
        ),
    ]