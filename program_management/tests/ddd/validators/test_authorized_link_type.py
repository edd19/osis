# ############################################################################
#  OSIS stands for Open Student Information System. It's an application
#  designed to manage the core business of higher education institutions,
#  such as universities, faculties, institutes and professional schools.
#  The core business involves the administration of students, teachers,
#  courses, programs and so on.
#
#  Copyright (C) 2015-2020 Université catholique de Louvain (http://www.uclouvain.be)
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  A copy of this license - GNU General Public License - is available
#  at the root of the source code of this program.  If not,
#  see http://www.gnu.org/licenses/.
# ############################################################################
import factory.fuzzy
from django.test import SimpleTestCase

from base.models.enums.education_group_types import GroupType, MiniTrainingType
from base.models.enums.link_type import LinkTypes
from program_management.ddd.validators._authorized_link_type import AuthorizedLinkTypeValidator
from program_management.tests.ddd.factories.node import NodeLearningUnitYearFactory, NodeGroupYearFactory
from program_management.tests.ddd.validators.mixins import TestValidatorValidateMixin
from django.utils.translation import gettext_lazy as _


class TestAuthorizedLinkTypeValidator(TestValidatorValidateMixin, SimpleTestCase):
    def test_a_reference_link_with_a_learning_unit_as_child_should_raise_exception(self):
        parent_node = NodeGroupYearFactory()
        learning_unit_node_to_add = NodeLearningUnitYearFactory()
        link_type = LinkTypes.REFERENCE

        self.assertValidatorRaises(
            AuthorizedLinkTypeValidator(parent_node, learning_unit_node_to_add, link_type),
            [_("You are not allowed to create a reference with a learning unit %(child_node)s") % {
                "child_node": learning_unit_node_to_add
            }]
        )

    def test_a_none_link_type_with_a_learning_unit_as_child_should_not_raise_exception(self):
        parent_node = NodeGroupYearFactory()
        learning_unit_node_to_add = NodeLearningUnitYearFactory()
        link_type = None

        self.assertValidatorNotRaises(AuthorizedLinkTypeValidator(parent_node, learning_unit_node_to_add, link_type))

    def test_a_none_link_type_with_a_minor_major_list_and_a_minitraining_as_child_should_raise_exception(self):
        minor_major_list_parent_node = NodeGroupYearFactory(
            node_type=factory.fuzzy.FuzzyChoice(GroupType.minor_major_list_choice_enums())
        )
        minitraining_node_to_add = NodeGroupYearFactory(node_type=factory.fuzzy.FuzzyChoice(MiniTrainingType))
        link_type = None

        self.assertValidatorRaises(
            AuthorizedLinkTypeValidator(minor_major_list_parent_node, minitraining_node_to_add, link_type),
            [_("Link type should be reference between %(parent)s and %(child)s") % {
                "parent": minor_major_list_parent_node,
                "child": minitraining_node_to_add
            }]
        )

    def test_a_reference_link_type_with_a_minor_major_list_and_a_minitraining_as_child_should_raise_exception(self):
        minor_major_list_parent_node = NodeGroupYearFactory(
            node_type=factory.fuzzy.FuzzyChoice(GroupType.minor_major_list_choice_enums())
        )
        minitraining_child_node = NodeGroupYearFactory(node_type=factory.fuzzy.FuzzyChoice(MiniTrainingType))
        link_type = LinkTypes.REFERENCE

        self.assertValidatorNotRaises(
            AuthorizedLinkTypeValidator(minor_major_list_parent_node, minitraining_child_node, link_type)
        )

    def test_a_link_with_an_education_group_as_child_should_not_raise_exception(self):
        parent_node = NodeGroupYearFactory()
        education_group_node_to_add = NodeGroupYearFactory()

        link_types = (None, LinkTypes.REFERENCE)
        for link_type in link_types:
            with self.subTest(link_type=link_type):
                self.assertValidatorNotRaises(
                    AuthorizedLinkTypeValidator(parent_node, education_group_node_to_add, link_type)
                )
