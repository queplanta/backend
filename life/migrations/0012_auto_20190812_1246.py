# Generated by Django 2.2.4 on 2019-08-12 12:46

import db.fields
from django.db import migrations, models
import django.db.models.deletion
import life.models


class Migration(migrations.Migration):

    dependencies = [
        ('life', '0011_auto_20161215_2325'),
    ]

    operations = [
        migrations.AlterField(
            model_name='characteristic',
            name='document',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='+', to='db.DocumentID'),
        ),
        migrations.AlterField(
            model_name='characteristic',
            name='revision',
            field=models.OneToOneField(on_delete=django.db.models.deletion.PROTECT, primary_key=True, related_name='+', serialize=False, to='db.Revision'),
        ),
        migrations.AlterField(
            model_name='commonname',
            name='document',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='+', to='db.DocumentID'),
        ),
        migrations.AlterField(
            model_name='commonname',
            name='revision',
            field=models.OneToOneField(on_delete=django.db.models.deletion.PROTECT, primary_key=True, related_name='+', serialize=False, to='db.Revision'),
        ),
        migrations.AlterField(
            model_name='lifenode',
            name='commonNames',
            field=db.fields.ManyToManyField(limit_choices_to=db.fields.limit_by_contenttype('life.CommonName'), related_name='lifeNode_commonName', to='db.DocumentID'),
        ),
        migrations.AlterField(
            model_name='lifenode',
            name='document',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='+', to='db.DocumentID'),
        ),
        migrations.AlterField(
            model_name='lifenode',
            name='images',
            field=db.fields.ManyToManyField(limit_choices_to=db.fields.limit_by_contenttype('images.Image'), related_name='lifeNode_image', to='db.DocumentID'),
        ),
        migrations.AlterField(
            model_name='lifenode',
            name='parent',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='children', to='db.DocumentID'),
        ),
        migrations.AlterField(
            model_name='lifenode',
            name='revision',
            field=models.OneToOneField(on_delete=django.db.models.deletion.PROTECT, primary_key=True, related_name='+', serialize=False, to='db.Revision'),
        ),
    ]
