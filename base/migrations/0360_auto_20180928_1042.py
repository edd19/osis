# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2018-09-28 10:42
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('base', '0359_message_template_luys_automatic_postponement_update'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='admissionconditionline',
            name='access_en',
        ),
        migrations.AlterField(
            model_name='admissionconditionline',
            name='access',
            field=models.CharField(choices=[
                ('-', '-'),
                ('on_the_file', 'On the file: direct access or access with additional training'),
                ('direct_access', 'Direct Access'),
                ('access_with_training', 'Access with additional training')
            ],
            max_length=32),
        ),
        migrations.RunSQL([
            "UPDATE base_admissionconditionline SET access='-' WHERE access = ''",
            "UPDATE base_admissionconditionline SET access='on_the_file' WHERE access='Sur dossier: accès direct ou moyennant compléments de formation'",
            "UPDATE base_admissionconditionline SET access='direct_access' WHERE access='Accès direct'",
            "UPDATE base_admissionconditionline SET access='access_with_training' WHERE access='Accès moyennant compléments de formation'",
        ])
    ]
