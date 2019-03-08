# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2019-03-08 14:50
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('reference', '0002_auto_20190308_1450'),
        ('base', '0434_auto_20190305_1918'),
    ]

    operations = [
        migrations.AddField(
            model_name='educationgroupyear',
            name='isced_domain',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='reference.DomainIsced', verbose_name='ISCED domain'),
        ),
    ]
