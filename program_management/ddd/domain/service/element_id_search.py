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
from typing import List, Dict

from django.db.models import F

from education_group.models.group_year import GroupYear
from osis_common.ddd import interface

ElementId = int
Year = int


class ElementIdByYearSearch(interface.DomainService):

    def search_from_element_ids(
            self,
            element_ids: List[ElementId]
    ) -> Dict[ElementId, Dict[Year, ElementId]]:
        """
        :return: Map associating elements ids given in parameter with these elements ids mapped by year :
        {
            <element_id>: {year: <element_id_of_year>}
        }
        """

        values_list = GroupYear.objects.filter(
            group__groupyear__element__pk__in=element_ids,
        ).annotate(
            element_id=F('element__pk'),
            year=F('academic_year__year'),
        ).values(
            'element_id',
            'group_id',
            'year',
        )

        grouped_by_group_id = {}
        for rec in values_list:
            grouped_by_group_id.setdefault(rec['group_id'], []).append(rec)

        result = {}
        for group_id, records in grouped_by_group_id.items():
            for record in records:
                element_id = record['element_id']
                result[element_id] = {
                    rec['year']: rec['element_id'] for rec in records
                }
        return result