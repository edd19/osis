# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2016-07-18 12:35
from __future__ import unicode_literals

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reference', '0003_decree_domain'),
        ('base', '0058_add_initial_users_to_groups'),
    ]

    operations = [
        migrations.CreateModel(
            name='Campus',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('external_id', models.CharField(blank=True, max_length=100, null=True)),
                ('changed', models.DateTimeField(null=True)),
                ('name', models.CharField(blank=True, max_length=100, null=True)),
                ('organization', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='base.Organization')),
            ],
        ),
        migrations.CreateModel(
            name='DomainOffer',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('external_id', models.CharField(blank=True, max_length=100, null=True)),
                ('priority', models.CharField(max_length=20)),
            ],
        ),
        migrations.RemoveField(
            model_name='domain',
            name='parent',
        ),
        migrations.RemoveField(
            model_name='person',
            name='birth_date',
        ),
        migrations.DeleteModel(
            name='Domain',
        ),
        migrations.AddField(
            model_name='domainoffer',
            name='domain',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='reference.Domain'),
        ),
        migrations.AddField(
            model_name='domainoffer',
            name='offer_year',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='base.OfferYear'),
        ),
        migrations.AddField(
            model_name='offeryear',
            name='campus',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='base.Campus'),
        ),
    ]