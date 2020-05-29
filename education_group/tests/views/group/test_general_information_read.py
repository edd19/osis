from unittest import mock

from django.http import HttpResponseForbidden, HttpResponse, HttpResponseNotFound
from django.test import TestCase
from django.urls import reverse

from base.models.enums.education_group_types import GroupType
from base.tests.factories.person import PersonWithPermissionsFactory
from base.tests.factories.user import UserFactory
from education_group.views.group.common_read import Tab
from program_management.ddd.domain.node import NodeGroupYear
from program_management.tests.factories.element import ElementGroupYearFactory


class TestGroupReadGeneralInformation(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.person = PersonWithPermissionsFactory('view_educationgroup')
        cls.element_group_year = ElementGroupYearFactory(
            group_year__partial_acronym="LTRONC100B",
            group_year__academic_year__year=2018,
            group_year__education_group_type__name=GroupType.COMMON_CORE.name
        )
        cls.url = reverse('group_general_information', kwargs={'year': 2018, 'code': 'LTRONC100B'})

    def setUp(self) -> None:
        self.client.force_login(self.person.user)

    def test_case_user_not_logged(self):
        self.client.logout()
        response = self.client.get(self.url)
        self.assertRedirects(response, '/login/?next={}'.format(self.url))

    def test_case_user_have_not_permission(self):
        self.client.force_login(UserFactory())
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, HttpResponseForbidden.status_code)
        self.assertTemplateUsed(response, "access_denied.html")

    def test_case_group_not_exists(self):
        dummy_url = reverse('group_general_information', kwargs={'year': 2018, 'code': 'DUMMY100B'})
        response = self.client.get(dummy_url)

        self.assertEqual(response.status_code, HttpResponseNotFound.status_code)

    def test_case_group_not_type_of_common_core(self):
        ElementGroupYearFactory(
            group_year__partial_acronym="LSUB100G",
            group_year__academic_year__year=2018,
            group_year__education_group_type__name=GroupType.SUB_GROUP.name
        )
        url = reverse('group_general_information', kwargs={'year': 2018, 'code': 'LSUB100G'})
        response = self.client.get(url)

        self.assertEqual(response.status_code, HttpResponseForbidden.status_code)

    def test_assert_template_used(self):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, HttpResponse.status_code)
        self.assertTemplateUsed(response, "group/general_informations_read.html")

    @mock.patch('education_group.views.serializers.general_information.get_sections', return_value={})
    def test_assert_context_data(self, mock_get_sections):
        response = self.client.get(self.url)

        self.assertEqual(response.context['person'], self.person)
        self.assertEqual(response.context['group_year'], self.element_group_year.group_year)
        expected_update_label_url = reverse('education_group_pedagogy_edit', args=[
            self.element_group_year.group_year_id,
            self.element_group_year.group_year_id
        ])
        self.assertEqual(response.context['update_label_url'], expected_update_label_url)
        expected_publish_url = reverse(
            'publish_general_information', args=["2018", "LTRONC100B"]
        ) + "?path=" + str(self.element_group_year.pk)
        self.assertEqual(response.context['publish_url'], expected_publish_url)
        self.assertIsInstance(response.context['tree'], str)
        self.assertIsInstance(response.context['node'], NodeGroupYear)
        self.assertFalse(response.context['can_edit_information'])

        self.assertTrue(mock_get_sections.called)
        self.assertDictEqual(response.context['sections'], {})

    def test_assert_active_tabs_is_general_information_and_others_are_not_active(self):
        response = self.client.get(self.url)

        self.assertTrue(response.context['tab_urls'][Tab.GENERAL_INFO]['active'])
        self.assertFalse(response.context['tab_urls'][Tab.IDENTIFICATION]['active'])
        self.assertFalse(response.context['tab_urls'][Tab.CONTENT]['active'])
        self.assertFalse(response.context['tab_urls'][Tab.UTILIZATION]['active'])