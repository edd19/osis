# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2019-03-18 09:42
from __future__ import unicode_literals

import base.models.group_element_year
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0436_auto_20190313_1410'),
    ]

    operations = [
        migrations.AlterField(
            model_name='groupelementyear',
            name='block',
            field=models.IntegerField(blank=True, null=True, validators=[base.models.group_element_year.validate_block_value], verbose_name='Block'),
        ),
    ]
