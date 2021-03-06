# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2016-07-28 01:23
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
            name='Vote',
            fields=[
                ('revision', models.OneToOneField(on_delete=django.db.models.deletion.PROTECT, primary_key=True, serialize=False, to='db.Revision')),
                ('is_tip', models.NullBooleanField()),
                ('is_deleted', models.NullBooleanField()),
                ('value', models.IntegerField()),
                ('document', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='db.DocumentID')),
                ('parent', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='votes', to='db.DocumentID')),
            ],
            options={
                'abstract': False,
            },
            managers=[
                ('objects_revisions', django.db.models.manager.Manager()),
            ],
        ),
        migrations.CreateModel(
            name='VoteStats',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('count', models.IntegerField(default=0)),
                ('sum_values', models.IntegerField(default=0)),
                ('count_downs', models.IntegerField(default=0)),
                ('count_ups', models.IntegerField(default=0)),
                ('confidence_score', models.FloatField(default=0.0, editable=False)),
                ('hot_score', models.FloatField(default=0.0, editable=False)),
                ('document', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='db.DocumentID')),
            ],
        ),
        migrations.AlterUniqueTogether(
            name='vote',
            unique_together=set([('is_tip', 'document')]),
        ),
    ]
