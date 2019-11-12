# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2018-12-06 17:25
from __future__ import unicode_literals

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0407_auto_20181203_1108'),
    ]

    operations = [
        migrations.CreateModel(
            name='EducationGroupPublicationContact',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('order', models.PositiveIntegerField(db_index=True, editable=False)),
                ('role', models.CharField(blank=True, default='', max_length=100)),
                ('email', models.EmailField(max_length=254, verbose_name='email')),
                ('type', models.CharField(choices=[('ACADEMIC_RESPONSIBLE', 'Academic responsible'), ('OTHER_ACADEMIC_RESPONSIBLE', 'Other academic responsible'), ('JURY_MEMBER', 'Jury member'), ('OTHER_CONTACT', 'Other contact')], default='OTHER_CONTACT', max_length=100, verbose_name='type')),
                ('education_group_year', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='base.EducationGroupYear')),
            ],
            options={
                'ordering': ('education_group_year', 'type', 'order'),
            },
        ),
    ]
