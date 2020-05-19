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
from unittest.mock import patch
from unittest import mock

from django.test import TestCase

from base.models.group_element_year import GroupElementYear
from base.tests.factories.academic_year import AcademicYearFactory
from base.tests.factories.education_group_year import TrainingFactory, GroupFactory
from base.tests.factories.group_element_year import GroupElementYearFactory
from base.tests.factories.learning_unit_year import LearningUnitYearFactory
from program_management.ddd.domain.node import NodeEducationGroupYear, NodeLearningUnitYear
from program_management.ddd.repositories import persist_tree, load_tree
from program_management.ddd.validators._authorized_relationship import DetachAuthorizedRelationshipValidator
from program_management.tests.ddd.factories.link import LinkFactory
from program_management.tests.ddd.factories.node import NodeLearningUnitYearFactory
from program_management.tests.ddd.factories.program_tree import ProgramTreeFactory
from program_management.tests.factories.education_group_version import EducationGroupVersionFactory
from education_group.tests.factories.group_year import GroupYearFactory
from program_management.ddd.repositories.program_tree import ProgramTreeRepository
from program_management.ddd.repositories.program_tree_version import ProgramTreeVersionRepository
from program_management.ddd.domain.program_tree_version import ProgramTreeVersionIdentity
from program_management.models.education_group_version import EducationGroupVersion
from program_management.tests.factories.element import ElementFactory
from base.tests.factories.group_element_year import GroupElementYearFactory


class TestDeleteTreeVersion(TestCase):
    def setUp(self):
        academic_year = AcademicYearFactory(current=True)

        self.root = GroupYearFactory(academic_year=academic_year)
        self.element_root = ElementFactory(group_year=self.root)
        print("id: {}".format(self.element_root.pk))
        self.level1 = GroupYearFactory(academic_year=academic_year)
        self.element_level1 = ElementFactory(group_year=self.level1)
        self.learning_unit_year = LearningUnitYearFactory(academic_year=academic_year)
        self.element_ue = ElementFactory(learning_unit_year=self.learning_unit_year)

        GroupElementYearFactory(parent_element=self.element_root,
                                child_element=self.element_level1)
        GroupElementYearFactory(parent_element=self.element_level1,
                                child_element=self.element_ue)
        self.training = TrainingFactory(academic_year=academic_year)
        print("(self.training.id {} ".format(self.training.id))
        self.education_group_version = EducationGroupVersionFactory(offer=self.training,
                                                                    root_group=self.root)

    def test_persist_tree_from_scratch(self):
        for e in EducationGroupVersion.objects.all():
            print(e.offer.acronym)
            print(e.offer.academic_year.year)
            print(e.version_name)
            print(e.is_transition)
            # print(e.root_group__element)
            print(e.root_group.element.pk)
        # education_group_version = EducationGroupVersion.objects \
        #     .filter(root_group__element__isnull=False) \
        #     .select_related('root_group__element').get(
        #     offer__acronym=acronym,
        #     offer__academic_year__year=year,
        #     version_name=version_name,
        #     is_transition=transition
        # )
        print('***')
        print(EducationGroupVersion.objects.filter(root_group__element__isnull=False).first())
        print('***2')

        identity = ProgramTreeVersionIdentity(offer_acronym=self.education_group_version.offer.acronym,
                                              year=self.education_group_version.offer.academic_year.year,
                                              version_name=self.education_group_version.version_name,
                                              is_transition=self.education_group_version.is_transition)
        ProgramTreeVersionRepository.delete(entity_id=identity)

        # persist_tree.persist(tree)
#
#         link_root_with_common_core = GroupElementYear.objects.filter(
#             parent_id=self.root_node.node_id,
#             child_branch_id=self.common_core_node.node_id,
#         )
#         self.assertTrue(link_root_with_common_core.exists())
#
#         link_common_core_with_learn_unit = GroupElementYear.objects.filter(
#             parent_id=self.common_core_node.node_id,
#             child_leaf_id=self.learning_unit_year_node.node_id,
#         )
#         self.assertTrue(link_common_core_with_learn_unit.exists())
#
#     def test_save_when_first_link_exists_and_second_one_does_not(self):
#         GroupElementYearFactory(parent=self.training, child_branch=self.common_core, child_leaf=None)
#         tree = load_tree.load(self.root_node.node_id)
#
#         # Append UE to common core
#         tree.root_node.children[0].child.add_child(self.learning_unit_year_node)
#
#         persist_tree.persist(tree)
#
#         new_link = GroupElementYear.objects.filter(
#             parent_id=self.common_core_node.node_id,
#             child_leaf_id=self.learning_unit_year_node.node_id
#         )
#         self.assertTrue(new_link.exists())
#
#     @patch("program_management.ddd.repositories.persist_tree.__persist_group_element_year")
#     def test_save_when_link_has_not_changed(self, mock):
#         GroupElementYearFactory(parent=self.training, child_branch=self.common_core, child_leaf=None)
#         tree = load_tree.load(self.root_node.node_id)
#         persist_tree.persist(tree)
#         assertion_msg = "No changes made, so function GroupelementYear.save() should not have been called"
#         self.assertFalse(mock.called, assertion_msg)
#
#     @patch("program_management.ddd.repositories.persist_tree.__persist_group_element_year")
#     def test_save_when_link_has_changed(self, mock):
#         GroupElementYearFactory(parent=self.training, child_branch=self.common_core, child_leaf=None)
#         tree = load_tree.load(self.root_node.node_id)
#         tree.root_node.children[0]._has_changed = True  # Made some changes
#         persist_tree.persist(tree)
#         assertion_msg = """
#             Changes were triggered in the Link object, so function GroupelementYear.save() should have been called
#         """
#         self.assertTrue(mock.called, assertion_msg)
#
#     @patch.object(DetachAuthorizedRelationshipValidator, 'validate')
#     def test_delete_when_1_link_has_been_deleted(self, mock):
#         GroupElementYearFactory(parent=self.training, child_branch=self.common_core, child_leaf=None)
#         node_to_detach = self.common_core_node
#         qs_link_will_be_detached = GroupElementYear.objects.filter(child_branch_id=node_to_detach.pk)
#         self.assertEqual(qs_link_will_be_detached.count(), 1)
#
#         tree = load_tree.load(self.root_node.node_id)
#
#         path_to_detach = "|".join([str(self.root_node.pk), str(node_to_detach.pk)])
#         tree.detach_node(path_to_detach)
#         persist_tree.persist(tree)
#         self.assertEqual(qs_link_will_be_detached.count(), 0)
#
#     @patch("program_management.ddd.repositories.persist_tree.__delete_group_element_year")
#     def test_delete_when_nothing_has_been_deleted(self, mock):
#         GroupElementYearFactory(parent=self.training, child_branch=self.common_core, child_leaf=None)
#         tree = load_tree.load(self.root_node.node_id)
#         persist_tree.persist(tree)
#         assertion_msg = "No changes made, so function GroupelementYear.delete() should not have been called"
#         self.assertFalse(mock.called, assertion_msg)
#
#
# class TestPersistPrerequisites(TestCase):
#     @mock.patch("program_management.ddd.repositories._persist_prerequisite.persist")
#     def test_call_persist_(self, mock_persist_prerequisite):
#         tree = ProgramTreeFactory()
#         LinkFactory(parent=tree.root_node, child=NodeLearningUnitYearFactory())
#
#         persist_tree.persist(tree)
#
#         mock_persist_prerequisite.assert_called_once_with(tree)
