# Generated by Django 2.2.4 on 2019-08-12 12:46

import db.fields
from django.db import migrations, models
import django.db.models.deletion
import occurrences.models


class Migration(migrations.Migration):

    dependencies = [
        ('occurrences', '0003_auto_20170213_0154'),
    ]

    operations = [
        migrations.AlterField(
            model_name='occurrence',
            name='identity',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='occurrence_identity', to='db.DocumentID'),
        ),
        migrations.AlterField(
            model_name='occurrence',
            name='images',
            field=db.fields.ManyToManyField(limit_choices_to=db.fields.limit_by_contenttype('images.Image'), related_name='occurrence_image', to='db.DocumentID'),
        ),
    ]
