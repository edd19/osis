# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2018-07-04 12:17
from __future__ import unicode_literals

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reference', '0017_language_changed'),
        ('base', '0301_auto_20180703_1611'),
    ]

    operations = [
        migrations.CreateModel(
            name='EducationGroupYearDomain',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('external_id', models.CharField(blank=True, max_length=100, null=True)),
                ('changed', models.DateTimeField(auto_now=True, null=True)),
                ('domain', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='reference.Domain')),
                ('education_group_year', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='base.EducationGroupYear')),
            ],
        ),
        migrations.RemoveField(
            model_name='offeryeardomain',
            name='education_group_year',
        ),
        migrations.AddField(
            model_name='educationgroupyear',
            name='domains',
            field=models.ManyToManyField(related_name='education_group_years', through='base.EducationGroupYearDomain', to='reference.Domain'),
        ),
    ]
