# Generated by Django 2.2.10 on 2020-04-08 19:25

import django.contrib.postgres.fields
from django.core.management import call_command
from django.db import migrations, models
import django.db.models.deletion
import education_group.auth.roles.utils
from education_group.auth.scope import Scope


def create_faculty_manager_rows(apps, shema_editor):
    """
    We will create a row to faculty managers for each user within faculty_managers groups.
    The entity linked will be set from personentity
    Set scopes to ALL because IUFC / DOCTORAT module are not released
    """
    FacultyManager = apps.get_model('education_group', 'facultymanager')
    PersonEntity = apps.get_model('base', 'personentity')
    User = apps.get_model('auth', 'User')
    Group = apps.get_model('auth', 'Group')

    faculty_managers = PersonEntity.objects.filter(
        person__user__groups__name='faculty_managers'
    )
    for faculty_manager in faculty_managers:
        FacultyManager.objects.create(
            person_id=faculty_manager.person_id,
            entity_id=faculty_manager.entity_id,
            with_child=faculty_manager.with_child,
            scopes=[Scope.ALL.name]
        )

    # [Backward compatible]
    # Add all users of faculty_managers's group to faculty_managers_for_ue because migration
    # of learning_unit to new role isn't done yet
    faculty_managers_for_ue_group, _ = Group.objects.get_or_create(name='faculty_managers_for_ue')
    for user in User.objects.filter(groups__name='faculty_managers'):
        faculty_managers_for_ue_group.user_set.add(user)

    # Resynchronize role managed with OSIS-Role with RBAC Django
    call_command('sync_perm_role', group='faculty_managers')


def create_central_manager_rows(apps, shema_editor):
    """
    We will create a row to central managers for each user within central_managers groups.
    The entity linked will be set from personentity
    Set scopes to ALL because IUFC / DOCTORAT module are not released
    """
    CentralManager = apps.get_model('education_group', 'centralmanager')
    PersonEntity = apps.get_model('base', 'personentity')
    User = apps.get_model('auth', 'User')
    Group = apps.get_model('auth', 'Group')

    central_managers = PersonEntity.objects.filter(
        person__user__groups__name='central_managers'
    )
    for central_manager in central_managers:
        CentralManager.objects.create(
            person_id=central_manager.person_id,
            entity_id=central_manager.entity_id,
            with_child=central_manager.with_child,
            scopes=[Scope.ALL.name]
        )

    # [Backward compatible]
    # Add all users of central_managers's group to central_managers_for_ue because migration
    # of learning_unit to new role isn't done yet
    central_managers_for_ue_group, _ = Group.objects.get_or_create(name='central_managers_for_ue')
    for user in User.objects.filter(groups__name='central_managers'):
        central_managers_for_ue_group.user_set.add(user)

    # Resynchronize role managed with OSIS-Role with RBAC Django
    call_command('sync_perm_role', group='central_managers')


def create_central_admission_rows(apps, shema_editor):
    """
    Previously called SIC groups
    """
    CentralAdmissionManager = apps.get_model('education_group', 'centraladmissionmanager')
    Person = apps.get_model('base', 'Person')
    Group = apps.get_model('auth', 'Group')

    central_admission_managers = Person.objects.filter(user__groups__name='sic')
    for central_admission_manager in central_admission_managers:
        CentralAdmissionManager.objects.create(person=central_admission_manager)

    sic_group = Group.objects.filter(name='sic').first()
    if sic_group:
        sic_group.user_set.clear()
        sic_group.delete()

    # Resynchronize role managed with OSIS-Role with RBAC Django
    call_command('sync_perm_role', group='central_admission_managers')


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0510_auto_20200408_1924'),
        ('education_group', '0005_auto_20200128_1246'),
    ]

    operations = [
        migrations.CreateModel(
            name='FacultyManager',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('with_child', models.BooleanField(default=False)),
                ('scopes', django.contrib.postgres.fields.ArrayField(base_field=models.CharField(choices=[('ALL', 'ALL'), ('IUFC', 'IUFC'), ('DOCTORAT', 'DOCTORAT')], max_length=200), blank=True, size=None)),
                ('entity', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='base.Entity')),
                ('person', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='base.Person')),
            ],
            options={
                'verbose_name': 'Faculty manager',
                'verbose_name_plural': 'Faculty managers',
            },
            bases=(education_group.auth.roles.utils.EducationGroupTypeScopeRoleMixin, models.Model),
        ),
        migrations.CreateModel(
            name='CentralManager',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('with_child', models.BooleanField(default=False)),
                ('scopes', django.contrib.postgres.fields.ArrayField(base_field=models.CharField(choices=[('ALL', 'ALL'), ('IUFC', 'IUFC'), ('DOCTORAT', 'DOCTORAT')], max_length=200), blank=True, size=None)),
                ('entity', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='base.Entity')),
                ('person', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='base.Person')),
            ],
            options={
                'verbose_name': 'Central manager',
                'verbose_name_plural': 'Central managers',
            },
            bases=(education_group.auth.roles.utils.EducationGroupTypeScopeRoleMixin, models.Model),
        ),
        migrations.CreateModel(
            name='CentralAdmissionManager',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('person', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='base.Person')),
            ],
            options={
                'verbose_name': 'Central admission manager',
                'verbose_name_plural': 'Central admission manager',
            },
        ),
        migrations.RunPython(create_faculty_manager_rows, migrations.RunPython.noop),
        migrations.RunPython(create_central_manager_rows, migrations.RunPython.noop),
        migrations.RunPython(create_central_admission_rows, migrations.RunPython.noop)
    ]
