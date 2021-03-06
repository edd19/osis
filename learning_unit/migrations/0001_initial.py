# Generated by Django 2.2.5 on 2020-01-24 19:55

import django.core.validators
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='LearningClassYear',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('external_id', models.CharField(blank=True, db_index=True, max_length=100, null=True)),
                ('acronym', models.CharField(max_length=3, validators=[django.core.validators.RegexValidator('^[a-zA-Z]*$', 'Only letters are allowed.')])),
                ('description', models.CharField(blank=True, max_length=100)),
                ('learning_component_year', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='base.LearningComponentYear')),
            ],
        ),
    ]
