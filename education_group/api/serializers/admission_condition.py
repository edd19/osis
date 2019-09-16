##############################################################################
#
#    OSIS stands for Open Student Information System. It's an application
#    designed to manage the core business of higher education institutions,
#    such as universities, faculties, institutes and professional schools.
#    The core business involves the administration of students, teachers,
#    courses, programs and so on.
#
#    Copyright (C) 2015-2018 Université catholique de Louvain (http://www.uclouvain.be)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    A copy of this license - GNU General Public License - is available
#    at the root of the source code of this program.  If not,
#    see http://www.gnu.org/licenses/.
#
##############################################################################
from rest_framework import serializers

from base.models.admission_condition import AdmissionCondition
from base.models.education_group_year import EducationGroupYear


class AdmissionConditionsSerializer(serializers.ModelSerializer):
    free_text = serializers.SerializerMethodField(read_only=True, required=False)
    alert_message = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = AdmissionCondition

        fields = (
            'free_text',
            'alert_message',
        )

    def get_free_text(self, obj):
        return _get_appropriate_text(obj, 'free', self.context.get('lang'))

    def get_alert_message(self, obj):
        common_acronym = 'common-{}'.format(self.context.get('full_suffix'))
        common_education_group_year = EducationGroupYear.objects.get(
            acronym=common_acronym,
            academic_year=self.context.get('egy').academic_year
        )
        admission_condition_common = common_education_group_year.admissioncondition
        return _get_appropriate_text(admission_condition_common, 'alert_message', self.context.get('lang'))


def _get_appropriate_text(eg_ac, field, language):
    lang = '' if language == 'fr-be' else '_' + language
    return getattr(eg_ac, 'text_' + field + lang)
