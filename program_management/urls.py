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
from django.conf.urls import url
from django.urls import include, path

import program_management.views.tree.copy_cut
from program_management.views import groupelementyear_update, \
    groupelementyear_read, element_utilization, excel, search, tree, quick_search
from program_management.views.prerequisite import read, update

urlpatterns = [
    url(r'^(?P<root_id>[0-9]+)/(?P<education_group_year_id>[0-9]+)/', include([
        url(r'^content/', include([
            url(r'^(?P<group_element_year_id>[0-9]+)/', include([
                url(r'^update/$', groupelementyear_update.UpdateGroupElementYearView.as_view(),
                    name="group_element_year_update"),
            ]))
        ])),
        url(r'^group_content/', groupelementyear_read.ReadEducationGroupTypeView.as_view(), name="group_content"),
        url(r'^pdf_content/(?P<language>[a-z\-]+)', groupelementyear_read.pdf_content, name="pdf_content"),
    ])),
    url(r'^(?P<root_id>[0-9]+)/(?P<learning_unit_year_id>[0-9]+)/learning_unit/', include([
        url(r'^utilization/$',
            element_utilization.LearningUnitUtilization.as_view(),
            name='learning_unit_utilization'),
        url(r'^prerequisite/$',
            read.LearningUnitPrerequisite.as_view(),
            name='learning_unit_prerequisite'),
        url(r'^prerequisite/update/$',
            update.LearningUnitPrerequisite.as_view(),
            name='learning_unit_prerequisite_update'),
    ])),
    url(
        r'reporting/(?P<education_group_year_pk>[0-9]+)/prerequisites/$',
        excel.get_learning_unit_prerequisites_excel,
        name="education_group_learning_units_prerequisites"
    ),
    url(
        r'reporting/(?P<education_group_year_pk>[0-9]+)/is_prerequisite_of/$',
        excel.get_learning_units_is_prerequisite_for_excel,
        name="education_group_learning_units_is_prerequisite_for"
    ),
    url(
        r'reporting/(?P<root_id>[0-9]+)/(?P<education_group_year_pk>[0-9]+)/contains/$',
        excel.get_learning_units_of_training_for_excel,
        name="education_group_learning_units_contains"
    ),
    url(r'^$', search.EducationGroupSearch.as_view(), name='version_program'),

    # NEW VERSION URL - Program management
    path('<int:root_id>/', include([
        path('create/', tree.create.CreateLinkView.as_view(), name='tree_create_link'),
        path('update/', tree.update.UpdateLinkView.as_view(), name='tree_update_link'),
        path('attach/', tree.paste.PasteNodesView.as_view(), name='tree_paste_node'),
        path('detach/', tree.detach.DetachNodeView.as_view(), name='tree_detach_node'),
        path('move/', tree.paste.PasteNodesView.as_view(), name='group_element_year_move'),
        path('<int:link_id>/', include([
            path('up/', tree.move.up, name="group_element_year_up"),
            path('down/', tree.move.down, name="group_element_year_down")
        ])),
        path('check_attach/', tree.paste.CheckPasteView.as_view(),
             name="check_tree_paste_node"),
        path('<str:node_path>/quick_search/', include([
            path(
                'learning_unit/',
                quick_search.QuickSearchLearningUnitYearView.as_view(),
                name="quick_search_learning_unit"
            ),
            path(
                'education_group/',
                quick_search.QuickSearchEducationGroupYearView.as_view(),
                name="quick_search_education_group"
            ),
        ])),

    ])),
    path('cut_element/', tree.copy_cut.cut_to_cache, name='cut_element'),
    path('copy_element/', tree.copy_cut.copy_to_cache, name='copy_element'),
]
