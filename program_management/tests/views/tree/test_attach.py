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
import mock
from django.contrib import messages
from django.http import HttpResponseBadRequest, HttpResponseNotFound, HttpResponse
from django.test import TestCase
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from base.models.enums.education_group_types import GroupType
from base.tests.factories.education_group_year import GroupFactory
from base.tests.factories.person import PersonFactory
from base.utils.cache import ElementCache
from program_management.ddd.domain.program_tree import ProgramTree
from program_management.forms.tree.attach import AttachNodeFormSet, AttachNodeForm
from program_management.tests.ddd.factories.node import NodeEducationGroupYearFactory, NodeLearningUnitYearFactory


class TestAttachNodeView(TestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.person = PersonFactory()

    def setUp(self):
        self.tree = self.setUpTreeData()
        self.url = reverse("tree_attach_node", kwargs={'root_id': self.tree.root_node.pk})
        self.client.force_login(self.person.user)

        fetch_tree_patcher = mock.patch('program_management.ddd.repositories.fetch_tree.fetch', return_value=self.tree)
        fetch_tree_patcher.start()
        self.addCleanup(fetch_tree_patcher.stop)

    def setUpTreeData(self):
        """
           |BIR1BA
           |----LBIR150T (common-core)
                |---LBIR1110 (UE)
           |----LBIR101G (subgroup)
        """
        root_node = NodeEducationGroupYearFactory(acronym="BIR1BA")
        common_core = NodeEducationGroupYearFactory(acronym="LBIR150T")
        learning_unit_node = NodeLearningUnitYearFactory(acronym='LBIR1110')
        subgroup = NodeEducationGroupYearFactory(acronym="LBIR101G")

        common_core.add_child(learning_unit_node)
        root_node.add_child(common_core)
        root_node.add_child(subgroup)
        return ProgramTree(root_node)

    def test_when_path_parameter_is_not_set(self):
        response = self.client.get(self.url)
        self.assertEquals(response.status_code, HttpResponseBadRequest.status_code)

    def test_when_path_destination_is_invalid(self):
        response = self.client.get(self.url + "?to_path=555")
        self.assertEquals(response.status_code, HttpResponseNotFound.status_code)

    def test_when_no_data_selected_on_cache(self):
        ElementCache(self.person.user).clear()

        to_path = "|".join([str(self.tree.root_node.pk), str(self.tree.root_node.children[0].child.pk)])
        response = self.client.get(self.url + "?to_path=" + to_path)
        self.assertEquals(response.status_code, HttpResponse.status_code)
        self.assertTemplateUsed(response, 'tree/attach_inner.html')

        msgs = [m.message for m in messages.get_messages(response.wsgi_request)]
        self.assertEqual(msgs, [_("Please cut or copy an item before attach it")])

    def test_when_education_group_year_element_is_selected(self):
        subgroup_to_attach = GroupFactory(
            academic_year__year=self.tree.root_node.year,
            education_group_type__name=GroupType.SUB_GROUP.name,
        )

        ElementCache(self.person.user).save_element_selected(
            subgroup_to_attach,
            action=ElementCache.ElementCacheAction.COPY.value
        )

        # To path :  BIR1BA ---> COMMON_CORE
        to_path = "|".join([str(self.tree.root_node.pk), str(self.tree.root_node.children[0].child.pk)])
        response = self.client.get(self.url + "?to_path=" + to_path)
        self.assertEquals(response.status_code, HttpResponse.status_code)
        self.assertTemplateUsed(response, 'tree/attach_inner.html')

        self.assertIsInstance(response.context['formset'], AttachNodeFormSet)
        self.assertEquals(len(response.context['formset'].forms), 1)
        self.assertIsInstance(response.context['formset'].forms[0], AttachNodeForm)

    def test_when_multiple_education_group_year_element_are_selected(self):
        pass
