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
import itertools

from django.db.models import QuerySet
from openpyxl import Workbook

from base.models.education_group_year import EducationGroupYear


def generate_prerequisites_workbook(egy: EducationGroupYear, prerequisites_qs: QuerySet):
    workbook = Workbook(encoding='utf-8')

    sheet = workbook.active

    # Header
    sheet.append(
        (egy.acronym, egy.title)
    )
    sheet.append(
        ("Officiel",)
    )

    # Content
    for prerequisite in prerequisites_qs:
        sheet.append(
            (prerequisite.learning_unit_year.acronym, prerequisite.learning_unit_year.complete_title)
        )
        groups_generator = itertools.groupby(prerequisite.items, key=lambda item: item.group_number)
        for key, group_gen in groups_generator:
            group = list(group_gen)
            if len(group) == 1:
                prerequisite_item = group[0]
                sheet.append(
                    [
                        "a comme prérequis :" if prerequisite_item.group_number == 1 else None,
                        prerequisite.main_operator if prerequisite_item.group_number != 1 else None,
                        prerequisite_item.learning_unit.luys[0].acronym,
                        prerequisite_item.learning_unit.luys[0].complete_title
                    ]
                )
            else:
                first_item = group[0]
                sheet.append(
                    [
                        "a comme prérequis :" if first_item.group_number == 1 else None,
                        prerequisite.main_operator if first_item.group_number != 1 else None,
                        "(" + first_item.learning_unit.luys[0].acronym,
                        first_item.learning_unit.luys[0].complete_title
                    ]
                )

                for item in group[1:-1]:
                    sheet.append(
                        [
                            None,
                            prerequisite.secondary_operator,
                            item.learning_unit.luys[0].acronym,
                            item.learning_unit.luys[0].complete_title
                        ]
                    )

                last_item = group[-1]
                sheet.append(
                    [
                        None,
                        prerequisite.secondary_operator,
                        last_item.learning_unit.luys[0].acronym + ")",
                        last_item.learning_unit.luys[0].complete_title
                    ]
                )
    return workbook
