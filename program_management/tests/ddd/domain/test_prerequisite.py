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
from django.test import SimpleTestCase
from django.utils.translation import gettext_lazy as _

from base.models.enums import prerequisite_operator
from program_management.ddd.domain import prerequisite
from program_management.ddd.domain.prerequisite import NullPrerequisite


class TestPrerequisiteItem(SimpleTestCase):
    def test_case_assert_str_method(self):
        p_item = prerequisite.PrerequisiteItem(code='LDROI1200', year=2018)
        expected_str = p_item.code

        self.assertEquals(str(p_item), expected_str)


class TestPrerequisiteGroupItem(SimpleTestCase):
    def test_case_assert_invalid_operator_raise_exception(self):
        with self.assertRaises(AssertionError):
            prerequisite.PrerequisiteItemGroup(operator="XOR")

    def test_case_assert_str_method_no_element_on_group(self):
        p_group = prerequisite.PrerequisiteItemGroup(operator=prerequisite_operator.OR)
        self.assertEquals(str(p_group), '')

    def test_case_assert_str_method_one_element_on_group(self):
        p_group = prerequisite.PrerequisiteItemGroup(operator=prerequisite_operator.OR)
        p_group.add_prerequisite_item('LDROI1200', 2018)

        expected_str = 'LDROI1200'
        self.assertEquals(str(p_group), expected_str)

    def test_case_assert_str_method_multiple_elements_on_group(self):
        p_group = prerequisite.PrerequisiteItemGroup(operator=prerequisite_operator.OR)
        p_group.add_prerequisite_item('LDROI1200', 2018)
        p_group.add_prerequisite_item('LAGRO2200', 2018)

        expected_str = 'LDROI1200 {OR} LAGRO2200'.format(OR=_(prerequisite_operator.OR))
        self.assertEquals(str(p_group), expected_str)


class TestPrerequisite(SimpleTestCase):
    def setUp(self):
        self.p_group = prerequisite.PrerequisiteItemGroup(operator=prerequisite_operator.OR)
        self.p_group.add_prerequisite_item('LDROI1300', 2018)
        self.p_group.add_prerequisite_item('LAGRO2400', 2018)

        self.p_group_2 = prerequisite.PrerequisiteItemGroup(operator=prerequisite_operator.OR)
        self.p_group_2.add_prerequisite_item('LDROI1400', 2018)

    def test_case_assert_invalid_main_operator_raise_exception(self):
        with self.assertRaises(AssertionError):
            prerequisite.Prerequisite(main_operator="XOR")

    def test_case_assert_str_method_no_group(self):
        p_req = prerequisite.Prerequisite(main_operator=prerequisite_operator.AND)
        self.assertEquals(str(p_req), '')

    def test_case_assert_str_method_with_one_group(self):
        p_req = prerequisite.Prerequisite(main_operator=prerequisite_operator.AND)
        p_req.add_prerequisite_item_group(self.p_group)

        expected_str = 'LDROI1300 {OR} LAGRO2400'.format(OR=_(prerequisite_operator.OR))
        self.assertEquals(str(p_req), expected_str)

    def test_case_assert_str_method_with_multiple_groups(self):
        p_req = prerequisite.Prerequisite(main_operator=prerequisite_operator.AND)
        p_req.add_prerequisite_item_group(self.p_group)
        p_req.add_prerequisite_item_group(self.p_group_2)

        expected_str = '(LDROI1300 {OR} LAGRO2400) {AND} LDROI1400'.format(
            OR=_(prerequisite_operator.OR),
            AND=_(prerequisite_operator.AND)
        )
        self.assertEquals(str(p_req), expected_str)


class TestConstructPrerequisiteFromExpression(SimpleTestCase):
    def test_return_null_prerequisite_when_empty_expression_given(self):
        self.assertIsInstance(
            prerequisite.factory.from_expression("", 2019),
            NullPrerequisite
        )

    def test_return_prerequisite_object_when_expression_given(self):
        prerequisite_expression = "LOSIS4525 OU (LMARC5823 ET BRABD6985)"

        prerequisite_obj = prerequisite.factory.from_expression(prerequisite_expression, 2019)
        self.assertEqual(
            prerequisite_expression,
            str(prerequisite_obj)
        )
