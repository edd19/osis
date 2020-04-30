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
from unittest import skip, mock

import factory.fuzzy
from django.test import SimpleTestCase, TestCase
from django.utils.translation import gettext as _

from base.models.enums.education_group_types import GroupType, MiniTrainingType
from base.models.enums.link_type import LinkTypes
from base.tests.factories.academic_year import AcademicYearFactory
from base.tests.factories.authorized_relationship import AuthorizedRelationshipFactory
from base.tests.factories.education_group_year import TrainingFactory, MiniTrainingFactory, EducationGroupYearFactory, \
    GroupFactory
from base.tests.factories.group_element_year import GroupElementYearFactory
from base.tests.factories.learning_unit_year import LearningUnitYearFactory
from program_management.ddd.domain.program_tree import ProgramTree
from program_management.forms.tree import attach
from program_management.forms.tree.attach import AttachNodeForm, GroupElementYearForm
from program_management.tests.ddd.factories.authorized_relationship import AuthorizedRelationshipListFactory, \
    AuthorizedRelationshipObjectFactory
from program_management.tests.ddd.factories.node import NodeGroupYearFactory, NodeLearningUnitYearFactory, \
    NodeEducationGroupYearFactory


class TestAttachNodeFormFactory(SimpleTestCase):
    def test_form_returned_when_child_node_is_a_learning_unit(self):
        parent_node = NodeEducationGroupYearFactory()
        child_node = NodeLearningUnitYearFactory()
        path = ""
        relationships = AuthorizedRelationshipListFactory()

        form = attach.attach_form_factory(None, parent_node, child_node, path, relationships)
        self.assertIsInstance(form, attach.AttachLearningUnitForm)

    def test_form_returned_when_relationship_is_not_authorized(self):
        parent_node = NodeEducationGroupYearFactory()
        child_node = NodeEducationGroupYearFactory(
            node_type=MiniTrainingType.FSA_SPECIALITY
        )
        path = ""
        relationships = AuthorizedRelationshipListFactory(
            authorized_relationships=[AuthorizedRelationshipObjectFactory(child_type=MiniTrainingType.SOCIETY_MINOR)]
        )

        form = attach.attach_form_factory(None, parent_node, child_node, path, relationships)
        self.assertIsInstance(form, attach.AttachNotAuthorizedChildren)

    def test_form_returned_when_parent_is_minor_major_list_choice(self):
        parent_node = NodeEducationGroupYearFactory(
            node_type=factory.fuzzy.FuzzyChoice(GroupType.minor_major_list_choice_enums())
        )
        child_node = NodeEducationGroupYearFactory()
        path = ""
        relationship_object = AuthorizedRelationshipObjectFactory(
            parent_type=parent_node.node_type,
            child_type=child_node.node_type
        )
        relationships = AuthorizedRelationshipListFactory(
            authorized_relationships=[relationship_object]
        )

        form = attach.attach_form_factory(None, parent_node, child_node, path, relationships)
        self.assertIsInstance(form, attach.AttachToMinorMajorListChoiceForm)

    def test_form_returned_when_parent_is_training_and_child_is_minor_major_list_choice(self):
        parent_node = NodeEducationGroupYearFactory()
        child_node = NodeEducationGroupYearFactory(
            node_type=factory.fuzzy.FuzzyChoice(GroupType.minor_major_list_choice_enums())
        )
        path = ""
        relationship_object = AuthorizedRelationshipObjectFactory(
            parent_type=parent_node.node_type,
            child_type=child_node.node_type
        )
        relationships = AuthorizedRelationshipListFactory(
            authorized_relationships=[relationship_object]
        )

        form = attach.attach_form_factory(None, parent_node, child_node, path, relationships)
        self.assertIsInstance(form, attach.AttachMinorMajorListChoiceToTrainingForm)

    def test_return_base_form_when_no_special_condition_met(self):
        parent_node = NodeEducationGroupYearFactory()
        child_node = NodeEducationGroupYearFactory()
        path = ""
        relationship_object = AuthorizedRelationshipObjectFactory(
            parent_type=parent_node.node_type,
            child_type=child_node.node_type
        )
        relationships = AuthorizedRelationshipListFactory(
            authorized_relationships=[relationship_object]
        )

        form = attach.attach_form_factory(None, parent_node, child_node, path, relationships)
        self.assertEqual(type(form), attach.AttachNodeForm)


class TestAttachNodeForm(SimpleTestCase):
    @classmethod
    def setUpClass(cls):
        root_node = NodeGroupYearFactory()
        cls.tree = ProgramTree(root_node)
        super().setUpClass()

    def _get_attach_node_form_instance(self, link_attributes=None):
        to_path = str(self.tree.root_node.pk)
        node_to_attach = NodeGroupYearFactory()

        return AttachNodeForm(
            to_path,
            node_to_attach,
            data=link_attributes
        )

    def test_ensure_link_type_choice(self):
        form_instance = self._get_attach_node_form_instance({'link_type': 'invalid_link_type'})
        self.assertFalse(form_instance.is_valid())
        self.assertTrue(form_instance.errors['link_type'])

    @mock.patch("program_management.ddd.service.attach_node_service.attach_node")
    def test_save_should_call_attach_service(self, mock_service_attach_node):
        form_instance = self._get_attach_node_form_instance(link_attributes={})
        form_instance.is_valid()
        form_instance.save()

        self.assertTrue(mock_service_attach_node.called)


class TestAttachNodeFormFields(SimpleTestCase):
    def test_attach_node_form_base_fields(self):
        form = attach.AttachNodeForm("", NodeEducationGroupYearFactory())
        actual_fields = form.fields
        expected_fields = [
            'relative_credits',
            'access_condition',
            'is_mandatory',
            'block',
            'link_type',
            'comment',
            'comment_english'
        ]
        self.assertCountEqual(expected_fields, actual_fields)

    def test_attach_learning_unit_form_should_remove_access_condition_and_link_type_field(self):
        form = attach.AttachLearningUnitForm("", NodeLearningUnitYearFactory())
        actual_fields = form.fields

        self.assertNotIn("access_condition", actual_fields)
        self.assertNotIn("link_type", actual_fields)

    def test_attach_to_minor_major_list_choice_should_remove_all_fields_but_access_condition(self):
        form = attach.AttachToMinorMajorListChoiceForm("", NodeEducationGroupYearFactory())
        actual_fields = form.fields
        expected_fields = ["access_condition"]

        self.assertCountEqual(actual_fields, expected_fields)

    def test_attach_minor_major_list_choice_to_training_form_should_disable_all_fields_but_block(self):
        form = attach.AttachMinorMajorListChoiceToTrainingForm("", NodeEducationGroupYearFactory())

        expected_fields_disabled = ["block"]
        actual_fields_disabled = [name for name, field in form.fields.items() if not field.disabled]
        self.assertCountEqual(expected_fields_disabled, actual_fields_disabled)

    def test_attach_not_authorized_children_should_remove_relative_credits_and_access_condition(self):
        form = attach.AttachNotAuthorizedChildren("", NodeEducationGroupYearFactory())
        actual_fields = form.fields

        self.assertNotIn("access_condition", actual_fields)
        self.assertNotIn("relative_credits", actual_fields)


class TestGroupElementYearForm(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.academic_year = AcademicYearFactory()
        cls.parent = TrainingFactory(
            academic_year=cls.academic_year,
            education_group_type__learning_unit_child_allowed=True
        )
        cls.child_leaf = LearningUnitYearFactory()
        cls.child_branch = MiniTrainingFactory(academic_year=cls.academic_year)

    def test_fields_relevant(self):
        form = GroupElementYearForm()

        expected_fields = {
            "relative_credits",
            "is_mandatory",
            "block",
            "link_type",
            "comment",
            "comment_english",
            "access_condition"
        }
        self.assertFalse(expected_fields.symmetric_difference(set(form.fields.keys())))

    @skip
    def test_clean_link_type_reference_between_eg_lu(self):
        form = GroupElementYearForm(
            data={'link_type': LinkTypes.REFERENCE.name},
            parent=self.parent,
            child_leaf=self.child_leaf
        )

        self.assertTrue(form.is_valid(), form.errors)
        self.assertTrue("link_type" not in form.fields)

    def test_clean_link_type_reference_with_authorized_relationship(self):
        AuthorizedRelationshipFactory(
            parent_type=self.parent.education_group_type,
            child_type=self.child_branch.education_group_type,
        )
        ref_group = GroupElementYearFactory(
            parent=self.child_branch,
            child_branch=EducationGroupYearFactory(
                academic_year=self.academic_year,
                education_group_type=self.child_branch.education_group_type
            )
        )
        AuthorizedRelationshipFactory(
            parent_type=self.parent.education_group_type,
            child_type=ref_group.child_branch.education_group_type,
        )

        form = GroupElementYearForm(
            data={'link_type': LinkTypes.REFERENCE.name},
            parent=self.parent,
            child_branch=self.child_branch
        )

        self.assertTrue(form.is_valid())

    def test_remove_access_condition_when_not_authorized_relationship(self):
        form = GroupElementYearForm(parent=self.parent, child_branch=self.child_branch)
        self.assertTrue("access_condition" not in list(form.fields.keys()))

    def test_only_keep_access_condition_when_parent_is_minor_major_option_list_choice(self):
        expected_fields = ["access_condition"]
        for name in GroupType.minor_major_option_list_choice():
            with self.subTest(type=name):
                parent = GroupFactory(education_group_type__name=name)
                AuthorizedRelationshipFactory(
                    parent_type=parent.education_group_type,
                    child_type=self.child_branch.education_group_type
                )
                form = GroupElementYearForm(parent=parent, child_branch=self.child_branch)
                self.assertCountEqual(expected_fields, list(form.fields.keys()))

    def test_disable_all_fields_except_block_when_parent_is_formation_and_child_is_minor_major_option_list_choice(self):
        expected_fields = [
            "block"
        ]
        for name in GroupType.minor_major_option_list_choice():
            with self.subTest(type=name):
                child_branch = GroupFactory(education_group_type__name=name)
                AuthorizedRelationshipFactory(
                    parent_type=self.parent.education_group_type,
                    child_type=child_branch.education_group_type
                )
                form = GroupElementYearForm(parent=self.parent, child_branch=child_branch)
                enabled_fields = [name for name, field in form.fields.items() if not field.disabled]
                self.assertCountEqual(expected_fields, enabled_fields)

    def test_remove_access_condition_when_authorized_relationship(self):
        AuthorizedRelationshipFactory(
            parent_type=self.parent.education_group_type,
            child_type=self.child_branch.education_group_type
        )
        form = GroupElementYearForm(parent=self.parent, child_branch=self.child_branch)
        self.assertTrue("access_condition" not in list(form.fields.keys()))

    def test_child_education_group_year_without_authorized_relationship_fails(self):
        form = GroupElementYearForm(
            data={'link_type': ""},
            parent=self.parent,
            child_branch=self.child_branch
        )

        self.assertFalse(form.is_valid())
        self.assertEqual(
            form.errors["link_type"],
            [_("You cannot add \"%(child_types)s\" to \"%(parent)s\" (type \"%(parent_type)s\")") % {
                 'child_types': self.child_branch.education_group_type,
                 'parent': self.parent,
                 'parent_type': self.parent.education_group_type,
             }]
        )

    def test_initial_value_relative_credits(self):
        form = GroupElementYearForm(parent=self.parent, child_branch=self.child_branch)
        self.assertEqual(form.initial['relative_credits'], self.child_branch.credits)

        form = GroupElementYearForm(parent=self.parent, child_leaf=self.child_leaf)
        self.assertEqual(form.initial['relative_credits'], self.child_leaf.credits)

        form = GroupElementYearForm(parent=self.parent)
        self.assertEqual(form.initial['relative_credits'], None)
