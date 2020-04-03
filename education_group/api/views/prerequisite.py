##############################################################################
#
#    OSIS stands for Open Student Information System. It's an application
#    designed to manage the core business of higher education institutions,
#    such as universities, faculties, institutes and professional schools.
#    The core business involves the administration of students, teachers,
#    courses, programs and so on.
#
#    Copyright (C) 2015-2020 Université catholique de Louvain (http://www.uclouvain.be)
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
from django.http import JsonResponse
from rest_framework import viewsets
from rest_framework.generics import get_object_or_404

from backoffice.settings.rest_framework.common_views import LanguageContextSerializerMixin
from base.models.education_group_year import EducationGroupYear
from base.models.enums import education_group_categories
from education_group.api.serializers.prerequisite import EducationGroupPrerequisitesSerializer
from program_management.ddd.repositories import load_tree


class EducationGroupYearPrerequisites(LanguageContextSerializerMixin, viewsets.ViewSet):
    """
        Return the prerequisites of an education group
    """
    name = 'education_group_prerequisites'
    serializer_class = EducationGroupPrerequisitesSerializer
    base_queryset = EducationGroupYear.objects.all().select_related('education_group_type', 'academic_year')
    pagination_class = None
    filter_backends = ()

    def list(self, request, year=None, acronym=None):
        egy = get_object_or_404(
            self.base_queryset,
            acronym__iexact=acronym,
            academic_year__year=year
        )
        tree = load_tree.load(egy.id)
        serializer_context = {
            'request': request,
            'tree': tree
        }
        serializer = EducationGroupPrerequisitesSerializer(tree.get_nodes_that_have_prerequisites(),
                                                           many=True,
                                                           context=serializer_context)
        return JsonResponse(serializer.data, safe=False)


class TrainingPrerequisites(EducationGroupYearPrerequisites):
    name = 'training_prerequisites'
    base_queryset = EducationGroupYear.objects.filter(
        education_group_type__category=education_group_categories.TRAINING
    ).select_related(
        'education_group_type',
        'academic_year',
    )


class MiniTrainingPrerequisites(EducationGroupYearPrerequisites):
    name = 'mini_training_prerequisites'
    base_queryset = EducationGroupYear.objects.filter(
        education_group_type__category=education_group_categories.MINI_TRAINING
    ).select_related(
        'education_group_type',
        'academic_year',
    )

