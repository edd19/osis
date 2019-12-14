# Generated by Django 2.2.5 on 2019-12-14 00:47

import uuid

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    replaces = [('base', '0080_scoresencoding'), ('base', '0081_auto_20161207_1432'), ('base', '0082_auto_20161213_1654'), ('base', '0083_auto_20161215_1414'), ('base', '0084_auto_20161216_1338'), ('base', '0085_auto_20170105_1315')]

    dependencies = [
        ('base', '0079_pgm_managers_and_score_sheet_address'),
    ]

    operations = [
        migrations.RunSQL(
            sql='\n            DROP VIEW IF EXISTS app_scores_encoding;\n\n            CREATE OR REPLACE VIEW app_scores_encoding AS\n            SELECT row_number() OVER () as id,\n\n                base_programmanager.id as program_manager_id,\n                program_manager_person.id as pgm_manager_person_id,\n                base_offeryear.id as offer_year_id,\n                base_learningunityear.id as learning_unit_year_id,\n                base_examenrollment.enrollment_state,\n\n                count(base_examenrollment.id) as total_exam_enrollments,\n                sum(case when base_examenrollment.score_final is not null\n                              or base_examenrollment.justification_final is not null\n                         then 1 else 0 end) exam_enrollments_encoded,\n                sum(case when (base_examenrollment.score_draft is not null\n                               and base_examenrollment.score_final is null\n                               and base_examenrollment.justification_final is null)\n                              or (base_examenrollment.justification_draft is not null\n                                  and base_examenrollment.score_final is null\n                                  and base_examenrollment.justification_final is null)\n                         then 1 else 0 end) scores_not_yet_submitted\n\n\n            from base_examenrollment\n            join base_sessionexam on base_sessionexam.id = base_examenrollment.session_exam_id\n            join base_learningunityear on base_learningunityear.id = base_sessionexam.learning_unit_year_id\n\n            join base_offeryearcalendar on base_offeryearcalendar.id = base_sessionexam.offer_year_calendar_id\n\n            join base_learningunitenrollment on base_learningunitenrollment.id = base_examenrollment.learning_unit_enrollment_id\n            join base_offerenrollment on base_offerenrollment.id = base_learningunitenrollment.offer_enrollment_id\n            join base_offeryear on base_offeryear.id = base_offerenrollment.offer_year_id\n\n            join base_programmanager on base_programmanager.offer_year_id = base_offeryear.id\n            join base_person program_manager_person on program_manager_person.id = base_programmanager.person_id\n\n            where base_offeryearcalendar.start_date <= CURRENT_TIMESTAMP::date\n            and base_offeryearcalendar.end_date >=  CURRENT_TIMESTAMP::date\n\n            group by\n            base_programmanager.id,\n            program_manager_person.id,\n            base_offeryear.id,\n            base_learningunityear.id,\n            base_examenrollment.enrollment_state\n            ;\n            ',
        ),
        migrations.AlterField(
            model_name='structure',
            name='type',
            field=models.CharField(blank=True, choices=[('SECTOR', 'SECTOR'), ('FACULTY', 'FACULTY'), ('INSTITUTE', 'INSTITUTE'), ('POLE', 'POLE'), ('DOCTORAL_COMMISSION', 'DOCTORAL_COMMISSION'), ('PROGRAM_COMMISSION', 'PROGRAM_COMMISSION'), ('LOGISTIC', 'LOGISTIC'), ('RESEARCH_CENTER', 'RESEARCH_CENTER'), ('TECHNOLOGIC_PLATFORM', 'TECHNOLOGIC_PLATFORM'), ('UNDEFINED', 'UNDEFINED')], max_length=30, null=True),
        ),
        migrations.RemoveField(
            model_name='attribution',
            name='learning_unit',
        ),
        migrations.AlterField(
            model_name='attribution',
            name='learning_unit_year',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='learning_unit_year_attribution', to='base.LearningUnitYear'),
        ),
        migrations.AlterField(
            model_name='attribution',
            name='tutor',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='tutor_attribution', to='base.Tutor'),
        ),
        migrations.AddField(
            model_name='learningunityear',
            name='team',
            field=models.BooleanField(default=False),
        ),
        migrations.CreateModel(
            name='LearningUnitComponent',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('external_id', models.CharField(blank=True, max_length=100, null=True)),
                ('type', models.CharField(blank=True, choices=[('LECTURING', 'LECTURING'), ('PRACTICAL_EXERCISES', 'PRACTICAL_EXERCISES')], db_index=True, max_length=25, null=True)),
                ('duration', models.DecimalField(blank=True, decimal_places=2, max_digits=6, null=True)),
                ('learning_unit_year', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='base.LearningUnitYear')),
                ('uuid', models.UUIDField(db_index=True, default=uuid.uuid4, null=True)),
            ],
            options={
                'permissions': (('can_access_learningunit', 'Can access learning unit'),),
            },
        ),
        migrations.AddField(
            model_name='learningunitenrollment',
            name='uuid',
            field=models.UUIDField(db_index=True, default=uuid.uuid4, null=True),
        ),
        migrations.AddField(
            model_name='learningunityear',
            name='uuid',
            field=models.UUIDField(db_index=True, default=uuid.uuid4, null=True),
        ),
    ]
