##############################################################################
#
#    OSIS stands for Open Student Information System. It's an application
#    designed to manage the core business of higher education institutions,
#    such as universities, faculties, institutes and professional schools.
#    The core business involves the administration of students, teachers,
#    courses, programs and so on.
#
#    Copyright (C) 2015-2019 Université catholique de Louvain (http://www.uclouvain.be)
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

from django.conf import settings
from rest_framework import serializers

from base.api.serializers.campus import CampusDetailSerializer
from base.models.academic_year import AcademicYear
from base.models.education_group_type import EducationGroupType
from base.models.education_group_year import EducationGroupYear
from base.models.enums import education_group_categories, education_group_types
from education_group.api.serializers import utils
from education_group.api.serializers.education_group_title import EducationGroupTitleSerializer
from education_group.api.serializers.utils import TrainingHyperlinkedIdentityField
from reference.models.language import Language


class TrainingBaseListSerializer(EducationGroupTitleSerializer, serializers.HyperlinkedModelSerializer):
    url = TrainingHyperlinkedIdentityField(read_only=True)
    code = serializers.CharField(source='partial_acronym')
    academic_year = serializers.SlugRelatedField(slug_field='year', queryset=AcademicYear.objects.all())
    education_group_type = serializers.SlugRelatedField(
        slug_field='name',
        queryset=EducationGroupType.objects.filter(category=education_group_categories.TRAINING),
    )
    administration_entity = serializers.CharField(source='administration_entity_version.acronym', read_only=True)
    administration_faculty = serializers.SerializerMethodField()
    management_entity = serializers.CharField(source='management_entity_version.acronym', read_only=True)
    management_faculty = serializers.SerializerMethodField()

    # Display human readable value
    education_group_type_text = serializers.CharField(source='education_group_type.get_name_display', read_only=True)

    class Meta(EducationGroupTitleSerializer.Meta):
        model = EducationGroupYear
        fields = EducationGroupTitleSerializer.Meta.fields + (
            'url',
            'acronym',
            'code',
            'education_group_type',
            'education_group_type_text',
            'academic_year',
            'administration_entity',
            'administration_faculty',
            'management_entity',
            'management_faculty',
        )

    @staticmethod
    def get_administration_faculty(obj):
        return utils.get_entity(obj, 'administration')

    @staticmethod
    def get_management_faculty(obj):
        return utils.get_entity(obj, 'management')


class TrainingListSerializer(TrainingBaseListSerializer):
    partial_title = serializers.SerializerMethodField()

    class Meta(TrainingBaseListSerializer.Meta):
        fields = TrainingBaseListSerializer.Meta.fields + (
            'partial_title',
        )

    def get_partial_title(self, training):
        language = self.context.get('language')
        return getattr(
            training,
            'partial_title' + ('_english' if language and language not in settings.LANGUAGE_CODE_FR else '')
        )

    def to_representation(self, instance):
        data = super().to_representation(instance)
        if instance.education_group_type.name not in education_group_types.TrainingType.finality_types():
            data.pop('partial_title')
        return data


class TrainingDetailSerializer(TrainingListSerializer):
    primary_language = serializers.SlugRelatedField(slug_field='code', queryset=Language.objects.all())
    enrollment_campus = CampusDetailSerializer()
    main_teaching_campus = CampusDetailSerializer()

    # Display human readable value
    academic_type_text = serializers.CharField(source='get_academic_type_display', read_only=True)
    internship_text = serializers.CharField(source='get_internship_display', read_only=True)
    schedule_type_text = serializers.CharField(source='get_schedule_type_display', read_only=True)
    english_activities_text = serializers.CharField(source='get_english_activities_display', read_only=True)
    other_language_activities_text = serializers.CharField(
        source='get_other_language_activities_display',
        read_only=True
    )
    other_campus_activities_text = serializers.CharField(source='get_other_campus_activities_display', read_only=True)
    diploma_printing_orientation_text = serializers.CharField(
        source='get_diploma_printing_orientation_display',
        read_only=True,
    )
    language_association_text = serializers.CharField(source='get_language_association_display', read_only=True)
    duration_unit_text = serializers.CharField(source='get_duration_unit_display', read_only=True)
    constraint_type_text = serializers.CharField(source='get_constraint_type_display', read_only=True)
    decree_category_text = serializers.CharField(source='get_decree_category_display', read_only=True)
    rate_code_text = serializers.CharField(source='get_rate_code_display', read_only=True)
    active_text = serializers.CharField(source='get_active_display', read_only=True)
    remark = serializers.SerializerMethodField()
    domain_name = serializers.CharField(source='main_domain.parent.name', read_only=True)
    domain_code = serializers.CharField(source='main_domain.code', read_only=True)

    class Meta(TrainingListSerializer.Meta):
        fields = TrainingListSerializer.Meta.fields + (
            'partial_deliberation',
            'admission_exam',
            'funding',
            'funding_direction',
            'funding_cud',
            'funding_direction_cud',
            'academic_type',
            'academic_type_text',
            'university_certificate',
            'dissertation',
            'internship',
            'internship_text',
            'schedule_type',
            'schedule_type_text',
            'english_activities',
            'english_activities_text',
            'other_language_activities',
            'other_language_activities_text',
            'other_campus_activities',
            'other_campus_activities_text',
            'professional_title',
            'joint_diploma',
            'diploma_printing_orientation',
            'diploma_printing_orientation_text',
            'diploma_printing_title',
            'inter_organization_information',
            'inter_university_french_community',
            'inter_university_belgium',
            'inter_university_abroad',
            'primary_language',
            'keywords',
            'duration',
            'duration_unit',
            'duration_unit_text',
            'language_association_text',
            'enrollment_enabled',
            'credits',
            'remark',
            'min_constraint',
            'max_constraint',
            'constraint_type',
            'constraint_type_text',
            'weighting',
            'default_learning_unit_enrollment',
            'decree_category',
            'decree_category_text',
            'rate_code',
            'rate_code_text',
            'internal_comment',
            'co_graduation',
            'co_graduation_coefficient',
            'web_re_registration',
            'active',
            'active_text',
            'enrollment_campus',
            'main_teaching_campus',
            'domain_code',
            'domain_name'
        )

    def get_remark(self, training):
        language = self.context.get('language')
        return getattr(
            training,
            'remark' + ('_english' if language and language not in settings.LANGUAGE_CODE_FR else '')
        )
