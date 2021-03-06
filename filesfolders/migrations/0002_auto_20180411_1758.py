# -*- coding: utf-8 -*-
# Generated by Django 1.11.11 on 2018-04-11 15:58
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('projectroles', '0001_initial'),
        ('filesfolders', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='hyperlink',
            name='owner',
            field=models.ForeignKey(help_text='User who owns the object', on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='hyperlink',
            name='project',
            field=models.ForeignKey(help_text='Project in which the object belongs', on_delete=django.db.models.deletion.CASCADE, related_name='filesfolders_hyperlink_objects', to='projectroles.Project'),
        ),
        migrations.AddField(
            model_name='folder',
            name='folder',
            field=models.ForeignKey(blank=True, help_text='Folder under which object exists (null if root folder)', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='filesfolders_folder_children', to='filesfolders.Folder'),
        ),
        migrations.AddField(
            model_name='folder',
            name='owner',
            field=models.ForeignKey(help_text='User who owns the object', on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='folder',
            name='project',
            field=models.ForeignKey(help_text='Project in which the object belongs', on_delete=django.db.models.deletion.CASCADE, related_name='filesfolders_folder_objects', to='projectroles.Project'),
        ),
        migrations.AddField(
            model_name='file',
            name='folder',
            field=models.ForeignKey(blank=True, help_text='Folder under which object exists (null if root folder)', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='filesfolders_file_children', to='filesfolders.Folder'),
        ),
        migrations.AddField(
            model_name='file',
            name='owner',
            field=models.ForeignKey(help_text='User who owns the object', on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='file',
            name='project',
            field=models.ForeignKey(help_text='Project in which the object belongs', on_delete=django.db.models.deletion.CASCADE, related_name='filesfolders_file_objects', to='projectroles.Project'),
        ),
        migrations.AlterUniqueTogether(
            name='hyperlink',
            unique_together=set([('project', 'folder', 'name')]),
        ),
        migrations.AlterUniqueTogether(
            name='folder',
            unique_together=set([('project', 'folder', 'name')]),
        ),
        migrations.AlterUniqueTogether(
            name='file',
            unique_together=set([('project', 'folder', 'name')]),
        ),
    ]
