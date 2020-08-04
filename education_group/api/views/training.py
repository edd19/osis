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
from django.db.models import Case, When, Value, F, CharField
from django_filters import rest_framework as filters
from rest_framework import generics
from rest_framework.generics import get_object_or_404

from backoffice.settings.rest_framework.common_views import LanguageContextSerializerMixin
from base.models.education_group_year import EducationGroupYear
from base.models.enums import education_group_categories
from base.models.enums.education_group_types import TrainingType
from education_group.api.serializers.education_group_title import EducationGroupTitleSerializer
from education_group.api.serializers.training import TrainingListSerializer, TrainingDetailSerializer


class TrainingFilter(filters.FilterSet):
    from_year = filters.NumberFilter(field_name="academic_year__year", lookup_expr='gte')
    to_year = filters.NumberFilter(field_name="academic_year__year", lookup_expr='lte')
    in_type = filters.CharFilter(field_name="education_group_type__name", lookup_expr='icontains')
    campus = filters.CharFilter(field_name='main_teaching_campus__name', lookup_expr='icontains')
    education_group_type = filters.MultipleChoiceFilter(
        field_name='education_group_type__name',
        choices=TrainingType.choices()
    )

    class Meta:
        model = EducationGroupYear
        fields = [
            'acronym', 'partial_acronym', 'title', 'title_english', 'from_year', 'to_year', 'education_group_type'
        ]


class TrainingList(LanguageContextSerializerMixin, generics.ListAPIView):
    """
       Return a list of all the training with optional filtering.
    """
    name = 'training-list'
    queryset = EducationGroupYear.objects.filter(
        education_group_type__category=education_group_categories.TRAINING
    ).select_related('education_group_type', 'academic_year') \
        .prefetch_related(
        'administration_entity__entityversion_set',
        'management_entity__entityversion_set'
    ).exclude(
        acronym__icontains='common'
    )
    serializer_class = TrainingListSerializer
    filterset_class = TrainingFilter
    search_fields = (
        'acronym',
        'partial_acronym',
        'title',
        'title_english',
    )
    ordering_fields = (
        'acronym',
        'partial_acronym',
        'title',
        'title_english',
    )
    ordering = (
        '-academic_year__year',
        'acronym',
    )  # Default ordering


class TrainingDetail(LanguageContextSerializerMixin, generics.RetrieveAPIView):
    """
        Return the detail of the training
    """
    name = 'training_read'
    serializer_class = TrainingDetailSerializer
    pagination_class = None
    filter_backends = ()

    def get_object(self):
        acronym = self.kwargs['acronym']
        year = self.kwargs['year']
        egy = get_object_or_404(
            EducationGroupYear.objects.filter(
                education_group_type__category=education_group_categories.TRAINING
            ).select_related(
                'education_group_type',
                'academic_year',
                'main_teaching_campus',
                'enrollment_campus',
                'primary_language',
            ).prefetch_related(
                'administration_entity__entityversion_set',
                'management_entity__entityversion_set',
            ).annotate(
                domain_code=Case(
                    When(main_domain=None, then=Value(None)),
                    default=F('main_domain__code'),
                    output_field=CharField()
                ),
                domain_name=Case(
                    When(main_domain=None, then=Value(None)),
                    When(main_domain__parent=None, then=F('main_domain__name')),
                    default=F('main_domain__parent__name'),
                    output_field=CharField()
                )
            ),
            acronym__iexact=acronym,
            academic_year__year=year
        )

        return egy


class TrainingTitle(LanguageContextSerializerMixin, generics.RetrieveAPIView):
    """
        Return the title of the training
    """
    name = 'trainingstitle_read'
    serializer_class = EducationGroupTitleSerializer

    def get_object(self):
        acronym = self.kwargs['acronym']
        year = self.kwargs['year']
        egy = get_object_or_404(
            EducationGroupYear.objects.all().select_related(
                'academic_year',
            ),
            acronym__iexact=acronym,
            academic_year__year=year
        )
        return egy
