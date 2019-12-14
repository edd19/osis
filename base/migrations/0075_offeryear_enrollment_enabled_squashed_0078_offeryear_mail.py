# Generated by Django 2.2.5 on 2019-12-14 00:47

from django.db import migrations, models


class Migration(migrations.Migration):

    replaces = [('base', '0075_offeryear_enrollment_enabled'), ('base', '0076_auto_20161104_1504'), ('base', '0077_scoresencoding'), ('base', '0078_offeryear_mail')]

    dependencies = [
        ('base', '0074_update_ext_id_learning_unit'),
    ]

    operations = [
        migrations.AddField(
            model_name='offeryear',
            name='enrollment_enabled',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='examenrollment',
            name='enrollment_state',
            field=models.CharField(choices=[('ENROLLED', 'ENROLLED'), ('NOT_ENROLLED', 'NOT_ENROLLED')], db_index=True, default='ENROLLED', max_length=20),
        ),
        migrations.RunSQL(
            sql='\n            DROP VIEW IF EXISTS app_scores_encoding;\n\n            CREATE OR REPLACE VIEW app_scores_encoding AS\n            SELECT row_number() OVER () as id,\n\n                base_programmanager.id as program_manager_id,\n                program_manager_person.id as pgm_manager_person_id,\n                base_offeryear.id as offer_year_id,\n                base_learningunityear.id as learning_unit_year_id,\n                base_examenrollment.enrollment_state,\n\n                count(base_examenrollment.id) as total_exam_enrollments,\n                sum(case when base_examenrollment.score_final is not null or base_examenrollment.justification_final is not null then 1 else 0 end) exam_enrollments_encoded,\n                sum(case when (base_examenrollment.score_draft is not null and base_examenrollment.score_final is null)\n                              or (base_examenrollment.justification_draft is not null and base_examenrollment.justification_final is null)\n                         then 1 else 0 end) scores_not_yet_submitted\n\n\n            from base_examenrollment\n            join base_sessionexam on base_sessionexam.id = base_examenrollment.session_exam_id\n            join base_learningunityear on base_learningunityear.id = base_sessionexam.learning_unit_year_id\n\n            join base_offeryearcalendar on base_offeryearcalendar.id = base_sessionexam.offer_year_calendar_id\n\n            join base_learningunitenrollment on base_learningunitenrollment.id = base_examenrollment.learning_unit_enrollment_id\n            join base_offerenrollment on base_offerenrollment.id = base_learningunitenrollment.offer_enrollment_id\n            join base_offeryear on base_offeryear.id = base_offerenrollment.offer_year_id\n\n            join base_programmanager on base_programmanager.offer_year_id = base_offeryear.id\n            join base_person program_manager_person on program_manager_person.id = base_programmanager.person_id\n\n            where base_offeryearcalendar.start_date <= CURRENT_TIMESTAMP::date\n            and base_offeryearcalendar.end_date >=  CURRENT_TIMESTAMP::date\n\n            group by\n            base_programmanager.id,\n            program_manager_person.id,\n            base_offeryear.id,\n            base_learningunityear.id,\n            base_examenrollment.enrollment_state\n            ;\n            ',
        ),
        migrations.AddField(
            model_name='offeryear',
            name='email',
            field=models.EmailField(blank=True, max_length=254, null=True),
        ),
    ]
