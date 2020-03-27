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
import random

from django.conf import settings
from django.db.models import F, When, Case
from django.http import HttpResponse
from django.test import TestCase
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from waffle.testutils import override_flag, override_switch

from backoffice.settings.base import LANGUAGE_CODE_EN
from base.models.enums import education_group_categories, education_group_types
from base.models.learning_component_year import volume_total_verbose, LearningComponentYear
from base.tests.factories.academic_year import AcademicYearFactory
from base.tests.factories.education_group_type import EducationGroupTypeFactory
from base.tests.factories.education_group_year import EducationGroupYearFactory, GroupFactory, MiniTrainingFactory, \
    EducationGroupYearBachelorFactory
from base.tests.factories.group_element_year import GroupElementYearFactory
from base.tests.factories.learning_component_year import LearningComponentYearFactory
from base.tests.factories.learning_unit_year import LearningUnitYearFactory
from base.tests.factories.person import CentralManagerFactory, PersonFactory
from base.tests.factories.user import SuperUserFactory
from program_management.business.group_element_years.group_element_year_tree import EducationGroupHierarchy


class TestRead(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.academic_year = AcademicYearFactory()
        cls.person = PersonFactory(language=settings.LANGUAGE_CODE_FR)
        cls.education_group_year_1 = EducationGroupYearFactory(title_english="", academic_year=cls.academic_year)
        cls.education_group_year_2 = EducationGroupYearBachelorFactory(
            title_english="",
            academic_year=cls.academic_year
        )
        cls.education_group_year_3 = EducationGroupYearFactory(title_english="", academic_year=cls.academic_year,
                                                               acronym='ed3')
        cls.learning_unit_year_1 = LearningUnitYearFactory(specific_title_english="")
        cls.learning_unit_year_2 = LearningUnitYearFactory(specific_title_english="", acronym="luy2")
        cls.learning_component_year_1 = LearningComponentYearFactory(
            learning_unit_year=cls.learning_unit_year_1, hourly_volume_partial_q1=10,
            hourly_volume_partial_q2=10)
        cls.learning_component_year_2 = LearningComponentYearFactory(
            learning_unit_year=cls.learning_unit_year_1, hourly_volume_partial_q1=10,
            hourly_volume_partial_q2=10)
        cls.group_element_year_1 = GroupElementYearFactory(parent=cls.education_group_year_1,
                                                           child_branch=cls.education_group_year_2,
                                                           comment="commentaire",
                                                           comment_english="english",
                                                           block=1)
        cls.group_element_year_2 = GroupElementYearFactory(parent=cls.education_group_year_2,
                                                           child_branch=None,
                                                           child_leaf=cls.learning_unit_year_1,
                                                           comment="commentaire",
                                                           comment_english="english",
                                                           block=6)
        cls.group_element_year_3 = GroupElementYearFactory(parent=cls.education_group_year_1,
                                                           child_branch=cls.education_group_year_3,
                                                           comment="commentaire",
                                                           comment_english="english",
                                                           block=1)
        cls.group_element_year_4 = GroupElementYearFactory(parent=cls.education_group_year_3,
                                                           child_branch=None,
                                                           child_leaf=cls.learning_unit_year_2,
                                                           comment="commentaire",
                                                           comment_english="english",
                                                           block=123)
        cls.a_superuser = SuperUserFactory()

    @override_switch('education_group_year_generate_pdf', active=True)
    def test_pdf_content(self):
        self.client.force_login(self.a_superuser)
        lang = random.choice(['fr-be', 'en'])
        url = reverse("pdf_content", args=[self.education_group_year_1.id, self.education_group_year_2.id, lang])
        response = self.client.get(url)
        self.assertTemplateUsed(response, 'pdf_content.html')

    def test_get_verbose_children(self):
        result = EducationGroupHierarchy(self.education_group_year_1).to_list()
        context_waiting = [self.group_element_year_1, [self.group_element_year_2], self.group_element_year_3,
                           [self.group_element_year_4]]
        self.assertEqual(result, context_waiting)

        credits = self.group_element_year_1.relative_credits or self.group_element_year_1.child_branch.credits or 0
        verbose_branch = "{} ({} {})".format(self.group_element_year_1.child.title, credits, _("credits"))

        self.assertEqual(self.group_element_year_1.verbose, verbose_branch)

        components = LearningComponentYear.objects.filter(
            learning_unit_year=self.group_element_year_2.child_leaf).annotate(
            total=Case(When(hourly_volume_total_annual=None, then=0),
                       default=F('hourly_volume_total_annual'))).values('type', 'total')

        verbose_leaf = "{} {} [{}] ({} {})".format(
            self.group_element_year_2.child_leaf.acronym,
            self.group_element_year_2.child_leaf.complete_title,
            volume_total_verbose(components),
            self.group_element_year_2.relative_credits or self.group_element_year_2.child_leaf.credits or 0,
            _("credits"),
        )
        self.assertEqual(self.group_element_year_2.verbose, verbose_leaf)

    def test_max_block(self):
        result = EducationGroupHierarchy(self.education_group_year_1)
        self.assertEqual(result.max_block, 6)

        result = EducationGroupHierarchy(self.education_group_year_3)
        self.assertEqual(result.max_block, 3)


@override_flag('pdf_content', active=True)
class TestReadPdfContent(TestCase):
    @classmethod
    def setUpTestData(cls):
        academic_year = AcademicYearFactory()
        education_group_year = EducationGroupYearFactory(academic_year=academic_year)
        GroupElementYearFactory(parent=education_group_year,
                                child_branch__academic_year=academic_year)
        cls.person = CentralManagerFactory("can_access_education_group")
        cls.url = reverse(
            "group_content",
            kwargs={
                "root_id": education_group_year.id,
                "education_group_year_id": education_group_year.id
            }
        )
        cls.post_valid_data = {'action': 'Generate pdf', 'language': LANGUAGE_CODE_EN}

    def setUp(self):
        self.client.force_login(self.person.user)

    def test_pdf_content_case_get_without_ajax_success(self):
        response = self.client.get(self.url, data=self.post_valid_data, follow=True)
        self.assertEqual(response.status_code, HttpResponse.status_code)
        self.assertTemplateUsed(response, "group_element_year/pdf_content.html")

    def test_pdf_content_case_get_with_ajax_success(self):
        response = self.client.get(self.url, data=self.post_valid_data, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, HttpResponse.status_code)
        self.assertTemplateUsed(response, "group_element_year/pdf_content_inner.html")


class TestReadTree(TestCase):
    @classmethod
    def setUpTestData(cls):
        academic_year = AcademicYearFactory()
        minor_list_type = EducationGroupTypeFactory(
            category=education_group_categories.GROUP,
            name=education_group_types.GroupType.MINOR_LIST_CHOICE.name,
        )
        common_type = EducationGroupTypeFactory(
            category=education_group_categories.GROUP,
            name=education_group_types.GroupType.COMMON_CORE,
        )

        cls.base_1 = GroupFactory(education_group_type=common_type,
                                  acronym="BASE",
                                  academic_year=academic_year)
        child_1 = GroupFactory(education_group_type=common_type,
                               acronym="CHILD",
                               academic_year=academic_year)
        minor_list_choice = GroupFactory(education_group_type=minor_list_type,
                                         acronym="MINOR LIST",
                                         academic_year=academic_year)

        minor_content_1 = MiniTrainingFactory(education_group_type=minor_list_type,
                                              academic_year=academic_year)
        minor_content_2 = MiniTrainingFactory(education_group_type=minor_list_type,
                                              academic_year=academic_year)

        cls.groupe_element_yr_1 = GroupElementYearFactory(parent=cls.base_1, child_branch=minor_list_choice)
        cls.groupe_element_yr_2 = GroupElementYearFactory(parent=cls.base_1, child_branch=child_1)
        cls.groupe_element_yr_3 = GroupElementYearFactory(parent=minor_list_choice, child_branch=minor_content_1)
        cls.groupe_element_yr_4 = GroupElementYearFactory(parent=minor_list_choice, child_branch=minor_content_2)

    def test_minor_list_detail_in_pdf_tree(self):
        result = EducationGroupHierarchy(self.base_1, pdf_content=True).to_list()
        self.assertCountEqual(result, [self.groupe_element_yr_1, self.groupe_element_yr_2])

    def test_minor_list_detail_in_tree(self):
        result = EducationGroupHierarchy(self.base_1).to_list()
        self.assertCountEqual(result, [self.groupe_element_yr_1,
                                       self.groupe_element_yr_2,
                                       [self.groupe_element_yr_3, self.groupe_element_yr_4]]
                              )
