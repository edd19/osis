# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2018-11-02 08:49
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0381_auto_20181031_1332'),
    ]

    operations = [
        migrations.AddField(
            model_name='organizationaddress',
            name='is_main',
            field=models.BooleanField(default=False),
        ),
    ]
