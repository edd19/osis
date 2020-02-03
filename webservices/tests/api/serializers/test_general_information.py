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
import collections

from django.conf import settings
from django.test import TestCase

from base.business.education_groups import general_information_sections
from base.business.education_groups.general_information_sections import DETAILED_PROGRAM, \
    COMMON_DIDACTIC_PURPOSES, SKILLS_AND_ACHIEVEMENTS, WELCOME_INTRODUCTION
from base.tests.factories.education_group_year import EducationGroupYearFactory, EducationGroupYearCommonFactory
from base.tests.factories.group_element_year import GroupElementYearFactory
from cms.enums.entity_name import OFFER_YEAR
from cms.tests.factories.translated_text import TranslatedTextFactory
from cms.tests.factories.translated_text_label import TranslatedTextLabelFactory
from webservices.api.serializers.general_information import GeneralInformationSerializer
from webservices.business import EVALUATION_KEY, SKILLS_AND_ACHIEVEMENTS_INTRO, SKILLS_AND_ACHIEVEMENTS_EXTRA


class GeneralInformationSerializerTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.egy = EducationGroupYearFactory()
        cls.common_egy = EducationGroupYearCommonFactory(academic_year=cls.egy.academic_year)
        cls.language = settings.LANGUAGE_CODE_EN
        cls.pertinent_sections = {
            'specific': [EVALUATION_KEY, DETAILED_PROGRAM, SKILLS_AND_ACHIEVEMENTS],
            'common': [COMMON_DIDACTIC_PURPOSES]
        }
        for section in cls.pertinent_sections['common']:
            TranslatedTextLabelFactory(
                language=cls.language,
                text_label__label=section
            )
            TranslatedTextFactory(
                reference=cls.common_egy.id,
                entity=OFFER_YEAR,
                language=cls.language,
                text_label__label=section,
                text=section.upper() + "_TEXT_COMMON"
            )
        for section in cls.pertinent_sections['specific']:
            TranslatedTextLabelFactory(
                language=cls.language,
                text_label__label=section
            )
            TranslatedTextFactory(
                reference=cls.egy.id,
                entity=OFFER_YEAR,
                language=cls.language,
                text_label__label=section,
                text=section.upper() + "_TEXT"
            )
        for label in [SKILLS_AND_ACHIEVEMENTS_INTRO, SKILLS_AND_ACHIEVEMENTS_EXTRA]:
            TranslatedTextFactory(
                text_label__label=label,
                reference=cls.egy.id,
                entity=OFFER_YEAR,
                language=cls.language
            )
        GroupElementYearFactory(parent=cls.egy, block='1')
        cls.serializer = GeneralInformationSerializer(
            cls.egy, context={
                'language': cls.language,
                'acronym': cls.egy.acronym
            }
        )

    def setUp(self):
        general_information_sections.SECTIONS_PER_OFFER_TYPE[
            self.egy.education_group_type.name
        ] = self.pertinent_sections

    def test_contains_expected_fields(self):
        expected_fields = [
            'language',
            'acronym',
            'title',
            'year',
            'education_group_type',
            'education_group_type_text',
            'sections'
        ]
        self.assertListEqual(list(self.serializer.data.keys()), expected_fields)

    def test_ensure_content_field_is_list_of_dict(self):
        expected_fields = [
            'id',
            'label',
            'content',
        ]
        self.assertEqual(type(self.serializer.data['sections']), list)
        self.assertEqual(
            len(self.serializer.data['sections']),
            len(self.pertinent_sections['common'] + self.pertinent_sections['specific'])
        )
        for section in self.serializer.data['sections']:
            if section['id'] == EVALUATION_KEY:
                self.assertTrue(isinstance(section, dict))
                self.assertListEqual(list(section.keys()), expected_fields + ['free_text'])
            else:
                self.assertTrue(isinstance(section, collections.OrderedDict))
                self.assertListEqual(list(section.keys()), expected_fields)

    def test_get_both_evaluation_texts(self):
        general_information_sections.SECTIONS_PER_OFFER_TYPE[self.egy.education_group_type.name] = {
            'specific': [EVALUATION_KEY],
            'common': [EVALUATION_KEY]
        }
        TranslatedTextFactory(
            reference=self.common_egy.id,
            entity=OFFER_YEAR,
            language=self.language,
            text_label__label=EVALUATION_KEY,
            text="EVALUATION_TEXT_COMMON"
        )
        evaluation_section = GeneralInformationSerializer(
            self.egy, context={
                'language': self.language,
                'acronym': self.egy.acronym
            }
        ).data['sections'][0]
        self.assertEqual(evaluation_section['content'], 'EVALUATION_TEXT_COMMON')
        self.assertEqual(evaluation_section['free_text'], 'EVALUATION_TEXT')

    def test_get_only_specific_evaluation(self):
        general_information_sections.SECTIONS_PER_OFFER_TYPE[self.egy.education_group_type.name] = {
            'specific': [EVALUATION_KEY],
            'common': []
        }
        evaluation_section = GeneralInformationSerializer(
            self.egy, context={
                'language': self.language,
                'acronym': self.egy.acronym
            }
        ).data['sections'][0]
        self.assertEqual(evaluation_section['content'], None)
        self.assertEqual(evaluation_section['free_text'], 'EVALUATION_TEXT')

    def test_case_text_not_existing(self):
        general_information_sections.SECTIONS_PER_OFFER_TYPE[
            self.egy.education_group_type.name
        ] = {
            'specific': [WELCOME_INTRODUCTION],
            'common': []
        }
        TranslatedTextLabelFactory(
            language=self.language,
            text_label__label=WELCOME_INTRODUCTION
        )
        welcome_introduction_section = GeneralInformationSerializer(
            self.egy, context={
                'language': self.language,
                'acronym': self.egy.acronym
            }
        ).data['sections'][0]
        self.assertEqual(welcome_introduction_section['content'], None)
